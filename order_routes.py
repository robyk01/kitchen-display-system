from flask import render_template, request, redirect, url_for, Blueprint, session, flash
from extensions import db
from models import Order, User
from woocommerce import API
from extensions import login_required
from datetime import datetime, date, timedelta
import requests

orders_bp = Blueprint('orders', __name__)

@orders_bp.route("/orders")
@login_required
def show_orders():
    user = User.query.get(session.get('user_id'))
    settings = user.settings

    woo_orders, error = fetch_woo_orders(user)

    if error:
        flash(error, "error")
        orders = []
    else:
        sync_orders_from_woo(woo_orders)
        orders = Order.query.all()
    
    in_kitchen = [o for o in orders if o.status == "in_kitchen"]
    ready = [o for o in orders if o.status == "ready"]

    soon_orders = []
    late_orders = []
    now = datetime.now()
    today = date.today().isoformat()

    for order in ready:
        start_time_str = order.time_slot_start_time or "23:59"  
        end_time_str = order.time_slot_end_time or "00:00"      

        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = datetime.strptime(end_time_str, "%H:%M").time()

        start_dt = datetime.combine(datetime.today(), start_time)
        end_dt = datetime.combine(datetime.today(), end_time)

        if order.delivery_date == today and start_dt - timedelta(minutes=10) <= now < end_dt:
            soon_orders.append(order) # yellow alert
        elif order.delivery_date == today and now >= end_dt:
            late_orders.append(order) # red alert

    return render_template("orders.html", page='Orders', in_kitchen=in_kitchen, ready=ready, soon_orders=soon_orders, late_orders=late_orders, settings=settings, error=error)

# Set Woocommerce API
def get_wcapi(user):
    if not user.api_key or not user.api_secret or not user.store_url:
        return None
    
    return API(url=user.store_url, consumer_key=user.api_key, consumer_secret=user.api_secret, version="wc/v3", verify_ssl=False)


# Check if user linked store API credentials with KDS
def fetch_woo_orders(user):
    if not user.api_key or not user.api_secret or not user.store_url:
        return None, "Please connect your store API in settings"
    
    try:
        wcapi = get_wcapi(user)
        response = wcapi.get("orders", params={"orderby": "date", "order": "desc", "status": "pending, on-hold, processing, cancelled, completed"})
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"Cannot connect to store: {str(e)}"


# Sync order from Woocommerce to database
def sync_orders_from_woo(woo_orders):
    if  not woo_orders:
        flash('Cannot fetch orders', 'error')
    else:
        woo_ids = [w["id"] for w in woo_orders]
        existing_orders = {o.woo_order_id: o for o in Order.query.filter(Order.woo_order_id.in_(woo_ids)).all()}

        woo_to_kds = {
            "pending": "in_kitchen",
            "on-hold": "in_kitchen",
            "processing": "in_kitchen",
            "completed": "delivered",
            "cancelled": "cancelled"
        }

        for w in woo_orders:
            existing = existing_orders.get(w["id"])
            status = woo_to_kds.get(w["status"], "in_kitchen")

            data = {
                "customer_name": f"{w['billing']['first_name']} {w['billing']['last_name']}",
                "payment_method": w["payment_method"],
                "delivery_method": get_order_meta(w, "_delivery_type"),
                "delivery_date": get_order_meta(w, "_delivery_date_slot"),
                "delivery_time_slot": get_order_meta(w, "_delivery_time_slot_id"),
                "time_slot_start_time": get_order_meta(w, "_delivery_time_start"),
                "time_slot_end_time": get_order_meta(w, "_delivery_time_end"),
                "time_slot_fee": get_order_meta(w, "_delivery_time_fee"),
                "total": w["total"],
                "line_items": w["line_items"],
                "status": status
            }

            if not existing:
                db.session.add(Order(woo_order_id=w["id"], **data))
            else:
                for key, value in data.items():
                    if key == 'status':
                        if existing.status == 'ready' and value not in ['delivered', 'cancelled', 'completed']:
                            continue
                    
                    setattr(existing, key, value)

        orders = Order.query.all()

        for o in orders:
            if o.woo_order_id not in woo_ids:
                o.status = 'deleted'

        flash('Orders fetched succesfully!', 'success')
        
    db.session.commit()


# Get metadata from Woocommerce order
def get_order_meta(order, key):
    for meta in order.get("meta_data", []):
        if meta["key"] == key:
            return meta["value"]
    return None



@orders_bp.route('/update_status/<int:id>')
@login_required
def update_status(id):
    order = Order.query.get(id)
    user = User.query.get(session.get('user_id'))
    wcapi = get_wcapi(user)

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

@orders_bp.route('/delete_order/<int:id>', methods=["POST"])
@login_required
def delete_order(id):
    order = Order.query.get_or_404(id)
    user = User.query.get(session.get('user_id'))
    wcapi = get_wcapi(user)

    data = {"status": "cancelled"}
    wcapi.put(f"orders/{order.woo_order_id}", data).json()
    
    db.session.delete(order)
    db.session.commit()

    flash("Order deleted succesfully!", "success")
    return redirect(url_for('.show_orders'))



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
