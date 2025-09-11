from flask import render_template, request, redirect, url_for, Blueprint, session, flash
from extensions import db
from models import User

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


@users_bp.route("/db_users")
def show_users():
    users = User.query.all()
    default_user = User.query.get(session.get('user_id'))
    return render_template("users.html", page="Users", users = users, current_user=default_user)


@users_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.username = request.form.get('username')
        db.session.commit()

        flash("User edited succesfully!", "success")
        return redirect(url_for('.show_users'))
    return render_template("edit_user.html", user=user)


@users_bp.route('/delete_user/<int:user_id>', methods = ['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    flash("User deleted succesfully!", "success")
    return redirect(url_for('.db_users'))
