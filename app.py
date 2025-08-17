from flask import Flask, render_template, request
from extensions import db
from models import User, Order
from user_routes import users_bp
from order_routes import orders_bp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(users_bp)
app.register_blueprint(orders_bp)

@app.route("/")
def home():
    user_count = User.query.count()
    users = User.query.limit(5).all()
    default_user = User.query.filter_by(email="roberto@gmail.com").first()
    return render_template('home.html', user=default_user, user_count=user_count, users=users)


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



@app.route("/users/<string:username>")
def user_page(username):
    return render_template("hello.html", name = username)



with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)