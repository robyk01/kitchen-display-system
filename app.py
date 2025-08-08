from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello World"

@app.route("/about")
def about():
    return "This is the kitchen display system"

@app.route("/orders")
def orders():
    return "List of orders"

@app.route("/orders/<int:id>")
def order_detail(id):
    return f"Details for order {id}"

@app.route("/users/")
def users():
    return render_template('users.html', users=['Andrei', 'Roerto'])

@app.route("/users/<string:username>")
def user_page(username):
    return render_template("hello.html", name=username)



app.run(debug=True)