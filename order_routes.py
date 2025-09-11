from flask import render_template, request, redirect, url_for, Blueprint, session, flash
from extensions import db
from models import Order, User
from woo import wcapi
from extensions import login_required
from datetime import datetime, date, timedelta

orders_bp = Blueprint('orders', __name__)

def sync_orders_from_woo(woo_orders):
    if woo_orders:
        for w in woo_orders:
            delivery_type = get_order_meta(w, "_delivery_type")
            delivery_date = get_order_meta(w, "_delivery_date_slot")
            delivery_time_slot = get_order_meta(w, "_delivery_time_slot_id")

            time_slot_start_time = get_order_meta(w, "_delivery_time_start")
            time_slot_end_time = get_order_meta(w, "_delivery_time_end")
            time_slot_fee = get_order_meta(w, "_delivery_time_fee")

            existing = Order.query.filter_by(woo_order_id=w["id"]).first()
            if not existing:
                new_order = Order(
                    woo_order_id=w["id"],
                    customer_name=f"{w['billing']['first_name']} {w['billing']['last_name']}",
                    payment_method=w["payment_method"],

                    delivery_method=delivery_type,
                    delivery_date=delivery_date,
                    delivery_time_slot=delivery_time_slot,

                    time_slot_start_time=time_slot_start_time,
                    time_slot_end_time=time_slot_end_time,
                    time_slot_fee=time_slot_fee,


                    total=w["total"],
                    line_items=w["line_items"])
                db.session.add(new_order)
            else:
                existing.payment_method=w["payment_method"]

                existing.delivery_method=delivery_type
                existing.delivery_date=delivery_date
                existing.delivery_time_slot=delivery_time_slot
                
                existing.time_slot_start_time=time_slot_start_time
                existing.time_slot_end_time=time_slot_end_time
                existing.time_slot_fee=time_slot_fee

                existing.total=w["total"]
                existing.line_items=w["line_items"]
        flash('Orders fetched succesfully!', 'success')
    else:
        flash('Cannot fetch orders', 'error')
    db.session.commit()

def get_order_meta(order, key):
    for meta in order.get("meta_data", []):
        if meta["key"] == key:
            return meta["value"]
    return None


@orders_bp.route("/orders")
@login_required
def show_orders():
    user = User.query.get(session.get('user_id'))
    settings = user.settings

    response = wcapi.get("orders", params={"orderby": "date", "order": "desc"})
    
    if response.status_code == 200:
        woo_orders = response.json()
        sync_orders_from_woo(woo_orders)
    else:
        return f"Error: {response.status_code}"
    
    in_kitchen = Order.query.filter_by(status="in_kitchen").all()
    ready = Order.query.filter_by(status="ready").all()

    soon_orders = []
    late_orders = []
    now = datetime.now()
    today = date.today().isoformat()
    orders = Order.query.all()

    for order in orders:
        start_time_str = order.time_slot_start_time or "23:59"  
        end_time_str = order.time_slot_end_time or "00:00"      

        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()

        start_dt = datetime.combine(datetime.today(), start_time)
        end_dt = datetime.combine(datetime.today(), end_time)

        if order.status == 'ready' and order.delivery_date == today and start_dt - timedelta(minutes=10) <= now < end_dt:
            soon_orders.append(order) # yellow alert
        elif order.status == 'ready' and order.delivery_date == today and now >= end_dt:
            late_orders.append(order) # red alert

    return render_template("orders.html", page='Orders', in_kitchen=in_kitchen, ready=ready, soon_orders=soon_orders, late_orders=late_orders, settings=settings)

@orders_bp.route('/update_status/<int:id>')
@login_required
def update_status(id):
    order = Order.query.get(id)
    if order.status == 'in_kitchen':
        order.status = 'ready'
    elif order.status == 'ready':
        order.status = 'delivered'
        data = {"status": "completed"}
        wcapi.put(f"orders/{order.woo_order_id}", data).json()

    flash("Order status updated succesfully!", "success")
    db.session.commit()
    return redirect(url_for('orders.show_orders'))

@orders_bp.route('/edit_order/<int:id>', methods=["GET", "POST"])
@login_required
def edit_order(id):
    order = Order.query.filter_by(id=id).first()

    if not order:
        flash("Error viewing the order", "error")
        return redirect(url_for('orders.show_orders'))

    if request.method == 'POST':
        order.status = request.form.get('status')

        flash("Order edited succesfully!", "success")
        db.session.commit()
        return redirect(url_for('.show_orders'))
    return render_template('edit_order.html', order=order)

# @orders_bp.route("/add_order", methods=["GET", "POST"])
# def add_order():
#     if request.method == "POST":
#         user = User.query.filter_by(email="roberto@gmail.com").first()
#         items = request.form.get("items")
#         total_price = request.form.get("total_price")

#         new_order = Order(user_id=user.id, items=items, total_price=total_price)
#         db.session.add(new_order)
#         db.session.commit()

#         return redirect(url_for('.orders'))

#     return render_template("add_order.html")


# @orders_bp.route('/delete_order/<int:id>', methods=["POST"])
# def delete_order(id):
#     order = Order.query.get_or_404(id)

#     db.session.delete(order)
#     db.session.commit()

#     return redirect(url_for('.orders'))
