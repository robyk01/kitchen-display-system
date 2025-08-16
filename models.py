from extensions import db

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