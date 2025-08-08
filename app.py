from flask import Flask

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

if __name__ == "__main__":
    app.run(debug=True)