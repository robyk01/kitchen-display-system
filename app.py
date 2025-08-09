from flask import Flask
from flask import render_template
from flask import request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello World"

users_list = ["Andrei", "Maria", "Denis", "Robert", "marius", "cristian"]

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        users_list.append(username)
        return redirect(url_for("users"))
    return render_template("register.html")




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
    return "List of orders"

@app.route("/orders/<int:id>")
def order_detail(id):
    return f"Details for order {id}"




@app.route("/users/")
def users():
    return render_template("users.html", users = users_list)

@app.route("/users/<string:username>")
def user_page(username):
    return render_template("hello.html", name = username)



app.run(debug=True)