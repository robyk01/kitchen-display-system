from extensions import db
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default="user")
    settings = relationship("Settings", uselist=False, back_populates="user")


    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Settings(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), name='fk_settings_user_id')
    user = relationship("User", back_populates="settings")

    show_customer = db.Column(db.Boolean, default=True)
    show_items = db.Column(db.Boolean, default=True)
    show_payment_method = db.Column(db.Boolean, default=True)
    show_delivery_method = db.Column(db.Boolean, default=True)
    show_delivery_date = db.Column(db.Boolean, default=True)
    show_status = db.Column(db.Boolean, default=True)
    show_total = db.Column(db.Boolean, default=True)

    display_type = db.Column(db.String(20), default="grid")


class Store(db.Model):
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), name='fk_store_user_id')

    api_key = db.Column(db.String(100))
    api_secret = db.Column(db.String(100))
    store_url = db.Column(db.String(255))

    addons = db.Column(db.JSON, default=[])

    orders = db.relationship("Order", backref="store", lazy=True)

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    woo_order_id = db.Column(db.Integer, unique=True, index=True, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), name='fk_order_store_id')
    addons = db.Column(db.JSON, default={})

    status = db.Column(
        db.String(20),
        nullable=False,
        default="in_kitchen",
        server_default="in_kitchen"
    )

    customer_name = db.Column(db.String(120))
    payment_method = db.Column(db.String(50))
    total = db.Column(db.Numeric(10, 2))
    line_items = db.Column(db.JSON)

