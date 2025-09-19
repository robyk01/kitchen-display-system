from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask import redirect, url_for, session

db = SQLAlchemy()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] != required_role:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Get metadata from Woocommerce order
def get_order_meta(order, key):
    for meta in order.get("meta_data", []):
        if meta["key"] == key:
            return meta["value"]
    return None
