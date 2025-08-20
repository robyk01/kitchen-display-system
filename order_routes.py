from flask import render_template, request, redirect, url_for, Blueprint
from extensions import db
from models import Order, User
from woo import wcapi

orders_bp = Blueprint('orders', __name__)

@orders_bp.route("/orders")
def show_orders():
    response = wcapi.get("orders")
    
    if response.status_code == 200:
        orders = response.json()
    else:
        return f"Error: {response.status_code}"

    return render_template("orders.html", orders=orders)


@orders_bp.route("/add_order", methods=["GET", "POST"])
def add_order():
    if request.method == "POST":
        user = User.query.filter_by(email="roberto@gmail.com").first()
        items = request.form.get("items")
        total_price = request.form.get("total_price")

        new_order = Order(user_id=user.id, items=items, total_price=total_price)
        db.session.add(new_order)
        db.session.commit()

        return redirect(url_for('.orders'))

    return render_template("add_order.html")

@orders_bp.route('/edit_order/<int:id>', methods=["GET", "POST"])
def edit_order(id):
    order = wcapi.get(f"orders/{id}").json()
    if request.method == 'POST':
        status = request.form.get('status')
        data = {"status": status}
        wcapi.put(f"orders/{id}", data).json()

        return redirect(url_for('.show_orders'))
    return render_template('edit_order.html', order=order)

@orders_bp.route('/delete_order/<int:id>', methods=["POST"])
def delete_order(id):
    order = Order.query.get_or_404(id)

    db.session.delete(order)
    db.session.commit()

    return redirect(url_for('.orders'))
