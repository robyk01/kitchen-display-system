from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    orders = db.relationship('Order', backref='customer', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.Column(db.String(500), nullable=False)
    total_price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"Order {self.id}"

@app.route("/")
def home():
    user = {'username': 'Roberto'}
    user_count = User.query.count()
    users = User.query.limit(5).all()
    return render_template('home.html', user=user, user_count=user_count, users=users)



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")

        new_user = User(username=username, email=email)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("db_users"))
    return render_template("register.html")


@app.route("/db_users")
def db_users():
    users = User.query.all()
    return render_template("db_users.html", users=users)


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        db.session.commit()
        return redirect(url_for('db_users'))
    return render_template('edit_user.html', user=user)


@app.route('/delete_user/<int:user_id>', methods = ['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('db_users'))


@app.route("/about")
def about():
    return "This is the kitchen display system"



@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        message = request.form.get("message")
    else:
        message = request.args.get("message")
    
    if message:
        return "Thank you!"
    return render_template("contact.html")



@app.route("/orders")
def orders():
    return render_template("orders.html")

@app.route("/orders/<int:id>")
def order_detail(id):
    return f"Details for order {id}"




@app.route("/users/<string:username>")
def user_page(username):
    return render_template("hello.html", name = username)



with app.app_context():
    db.create_all()

app.run(debug=True)