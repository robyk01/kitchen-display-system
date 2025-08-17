from flask import render_template, request, redirect, url_for, Blueprint
from extensions import db
from models import Order, User

orders_bp = Blueprint('orders', __name__)

@orders_bp.route("/orders")
def orders():
    default_user = User.query.filter_by(email="roberto@gmail.com").first()
    users = User.query.all()
    return render_template("orders.html", default_user=default_user, users=users)

@orders_bp.route("/orders/<int:id>")
def order_detail(id):
    return f"Details for order {id}"

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
    order = Order.query.get_or_404(id)

    if request.method == 'POST':
        items = request.form.get("items")
        total_price = request.form.get("total_price")

        order.items = items
        order.total_price = total_price
        db.session.commit()

        return redirect(url_for('.orders'))
    return render_template('edit_order.html', order=order)

@orders_bp.route('/delete_order/<int:id>', methods=["POST"])
def delete_order(id):
    order = Order.query.get_or_404(id)

    db.session.delete(order)
    db.session.commit()

    return redirect(url_for('.orders'))
