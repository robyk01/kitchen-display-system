from flask import Flask, render_template, request, session, redirect, url_for, flash
from extensions import db, login_required, role_required
from flask_migrate import Migrate
from models import User, Settings, Store
#from user_routes import users_bp
from order_routes import orders_bp
from user_routes import users_bp
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'secretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(orders_bp)
app.register_blueprint(users_bp)

def role_injection():
    return dict(role = session.get("role"))

def clock_injection():
    return dict(clock = datetime.now().strftime("%H:%M"))

def user_injection():
    curr_user = None
    if 'user_id' in session:
        curr_user = User.query.get(session.get('user_id')).username
    return dict(curr_user = curr_user)

app.context_processor(role_injection)
app.context_processor(clock_injection)
app.context_processor(user_injection)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role

            flash("Welcome!", "success")

            if session['role'] == 'admin':
                return redirect(url_for('.home'))
            else:
                return redirect(url_for('orders.show_orders'))
        
        flash("Incorrect username or password.", "error")

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop("user_id", None)
    return redirect(url_for('.login'))



@app.route("/")
@login_required
@role_required('admin')
def home():
    current_user = User.query.get(session.get("user_id"))

    # response = wcapi.get('orders')

    # if response.status_code == 200:
    #     orders = response.json()
    #     order_count = response.headers.get('X-WP-Total', 0)
    # else:
    #     return f"Error: {response.status_code}"
    
    # live = wcapi.get("orders", params={"status": "processing,on-hold"})

    # if live.status_code == 200:
    #     live_orders_count = live.headers.get("X-WP-Total", 0)
    # else:
    #     return f"Error: {live.status_code}"
    
    users = User.query.limit(10).all()
    
    return render_template('home.html', page=f"Hello, {current_user.username}!", current_user=current_user, users=users, user_count=len(users))


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    user = User.query.get_or_404(session.get('user_id'))
    store = Store.query.filter_by(user_id=session.get('user_id')).first()

    if not user.settings:
        user.settings = Settings()
        db.session.commit()

    settings = user.settings
    form_name = request.form.get('form_name')

    if request.method == 'POST':
        if form_name == 'general':
            for field in ["api_key", "api_secret", "store_url"]:
                setattr(user, field, request.form.get(field))

        if form_name == 'display':
            setattr(settings, 'display_type', request.form.get('display_type'))
            for field in ['show_customer', 'show_items', 'show_payment_method', 'show_delivery_method', 'show_delivery_date', 'show_status', 'show_total']:
                setattr(settings, field, bool(request.form.get(field)))

        db.session.commit()

    return render_template("settings.html", page="Settings", settings=settings, getattr=getattr, user=user, store=store)


@app.route("/users/<string:username>")
def user_page(username):
    return render_template("hello.html", name = username)



with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)