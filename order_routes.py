from flask import render_template, request, redirect, url_for, Blueprint
from extensions import db
from models import Order

orders_bp = Blueprint('orders', __name__)

@orders_bp.route("/orders")
def orders():
    return render_template("orders.html")

@orders_bp.route("/orders/<int:id>")
def order_detail(id):
    return f"Details for order {id}"