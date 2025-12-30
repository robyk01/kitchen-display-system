from flask import render_template, request, redirect, url_for, Blueprint, session, flash
from extensions import db, login_required, role_required
from models import User, Store
from order_routes import get_wcapi
from addons import ADDON_HANDLERS
import requests

users_bp = Blueprint('users', __name__)


# @users_bp.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "POST":
#         username = request.form.get("username")
#         email = request.form.get("email")

#         new_user = User(username=username, email=email)
#         db.session.add(new_user)
#         db.session.commit()

#         return redirect(url_for(".db_users"))
#     return "Register page"


@users_bp.route("/users")
@login_required
@role_required("admin")
def show_users():
    users = User.query.all()
    default_user = User.query.get(session.get('user_id'))
    return render_template("users.html", page="Users", users = users, current_user=default_user)


@users_bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required("admin")
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    store = Store.query.filter_by(user_id=user_id).first()

    error = check_store_connection(store)

    if request.method == 'POST':
        user.username = request.form.get('username')
        db.session.commit()

        flash("User edited succesfully!", "success")
        return redirect(url_for('.show_users'))
    return render_template("edit_user.html", user=user, page=f"Edit user: {user.username}", store=store, error=error)



@users_bp.route('/user/<int:user_id>/delete', methods = ['POST'])
@login_required
@role_required("admin")
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    flash("User deleted succesfully!", "success")
    return redirect(url_for('.db_users'))   

def check_store_connection(store):
    if store is None:
        return "No store linked to this user yet."

    if not store.api_key or not store.api_secret or not store.store_url:
        return "Store credentials missing."
    
    try:
        wcapi = get_wcapi(store)
        response = wcapi.get("orders")
        response.raise_for_status()
        return None
    except requests.exceptions.HTTPError as e:
        return f"Store returned an error: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "Could not connect to the store."
    except requests.exceptions.Timeout:
        return "Connection timed out."
    except requests.exceptions.RequestException:
        return "Unexpected error contacting store."


@users_bp.route('/store/<int:id>/edit', methods=['POST', 'GET'])
def edit_store(id):
    user = User.query.get(session.get('user_id'))
    store = Store.query.get(id)

    form_name = request.form.get('form_name')
    
    if request.method == 'POST':
        if form_name == 'store_api':
            for field in ["api_key", "api_secret", "store_url"]:
                setattr(store, field, request.form.get(field))
            flash('API credentials saved!', 'success')
        elif form_name == 'store_addons':
            enabled_addons = request.form.getlist('addons')
            store.addons = enabled_addons
            flash('Addons saved!', 'success')

        db.session.commit()
                

    return render_template("edit_store.html", store=store, page=f"Edit store: { store.name }", addons=ADDON_HANDLERS)
