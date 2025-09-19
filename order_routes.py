from flask import render_template, request, redirect, url_for, Blueprint, session, flash
from extensions import db
from models import Order, User, Store
from woocommerce import API
from extensions import login_required
from datetime import datetime, date, timedelta
from addons import ADDON_HANDLERS
import requests

orders_bp = Blueprint('orders', __name__)

@orders_bp.route("/orders")
@login_required
def show_orders():
    user = User.query.get(session.get('user_id'))
    settings = user.settings
    store = Store.query.filter_by(user_id=session.get('user_id')).first()

    woo_orders, error = fetch_woo_orders(store)

    if error:
        flash(error, "error")
        orders = []
    else:
        sync_orders_from_woo(woo_orders, store)
        orders = store.orders
    
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
def get_wcapi(store):
    if not store.api_key or not store.api_secret or not store.store_url:
        return None
    
    return API(url=store.store_url, consumer_key=store.api_key, consumer_secret=store.api_secret, version="wc/v3", verify_ssl=False)


# Check if user linked store API credentials with KDS
def fetch_woo_orders(store):
    if not store.api_key or not store.api_secret or not store.store_url:
        return None, "Please connect your store API in settings"
    
    try:
        wcapi = get_wcapi(store)
        response = wcapi.get("orders", params={"orderby": "date", "order": "desc", "status": "pending, on-hold, processing, cancelled, completed"})
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.HTTPError as e:
        return None, f"Store returned an error: {response.status_code}"
    except requests.exceptions.ConnectionError as e:
        return None, "Could not connect to the store. Please check your website."
    except requests.exceptions.Timeout as e:
        return None, "Connection timed out. Try again later."
    except requests.exceptions.RequestException as e:
        return None, "An unexpected error occurred when contacting the store."


# Sync order from Woocommerce to database
def sync_orders_from_woo(woo_orders, store):
    if not woo_orders:
        flash('Cannot fetch orders', 'error')
    else:
        woo_ids = [w["id"] for w in woo_orders]
        existing_orders = {
            o.woo_order_id: o 
            for o in Order.query.filter(
                Order.woo_order_id.in_(woo_ids),
                Order.store_id == store.id
                ).all()}

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

            addon_data = {}
            for addon in store.addons:
                handler = ADDON_HANDLERS.get(addon)
                if handler:
                    addon_data[addon] = handler(w)

            data = {
                "store_id": store.id,
                "customer_name": f"{w['billing']['first_name']} {w['billing']['last_name']}",
                "payment_method": w["payment_method"],
                "total": w["total"],
                "line_items": w["line_items"],
                "status": status,
                "addons": addon_data
            }

            if not existing:
                db.session.add(Order(woo_order_id=w["id"], **data))
            else:
                for key, value in data.items():
                    if key == 'status':
                        if existing.status == 'ready' and value not in ['delivered', 'cancelled', 'completed']:
                            continue
                    
                    setattr(existing, key, value)

        orders = store.orders

        for o in orders:
            if o.woo_order_id not in woo_ids:
                o.status = 'deleted'

        flash('Orders fetched succesfully!', 'success')
        
    db.session.commit()



@orders_bp.route('/order/<int:id>/update')
@login_required
def update_status(id):
    order = Order.query.get(id)
    store = Store.query.filter_by(user_id=session.get('user_id')).first()
    wcapi = get_wcapi(store)

    if order.status == 'in_kitchen':
        order.status = 'ready'
    elif order.status == 'ready':
        order.status = 'delivered'
        data = {"status": "completed"}
        wcapi.put(f"orders/{order.woo_order_id}", data).json()

    flash("Order status updated succesfully!", "success")
    db.session.commit()
    return redirect(url_for('orders.show_orders'))

@orders_bp.route('/order/<int:id>/edit', methods=["GET", "POST"])
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

@orders_bp.route('/order/<int:id>/delete', methods=["POST"])
@login_required
def delete_order(id):
    order = Order.query.get_or_404(id)
    store = Store.query.filter_by(user_id=session.get('user_id')).first()
    wcapi = get_wcapi(store)

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
