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

    display_type = db.Column(db.String(20), default="grid")

    show_customer = db.Column(db.Boolean, default=True)
    show_items = db.Column(db.Boolean, default=True)
    show_payment_method = db.Column(db.Boolean, default=True)
    show_status = db.Column(db.Boolean, default=True)
    show_total = db.Column(db.Boolean, default=True)

    show_delivery_method = db.Column(db.Boolean, default=False)
    show_delivery_date = db.Column(db.Boolean, default=False)
    show_extra_products = db.Column(db.Boolean, default=False)


class Store(db.Model):
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), name='fk_store_user_id')

    api_key = db.Column(db.String(100))
    api_secret = db.Column(db.String(100))
    store_url = db.Column(db.String(255))

    addons = db.Column(db.JSON, default=list)

    orders = db.relationship(
        "Order",
        backref="store",
        lazy=True,
        cascade="all, delete-orphan",
        passive_deletes=True
    )

class Order(db.Model):
    __tablename__ = 'orders'
    __table_args__ = (
        db.UniqueConstraint('fk_order_store_id', 'woo_order_id', name='uq_orders_store_woo_order'),
    )

    id = db.Column(db.Integer, primary_key=True)
    woo_order_id = db.Column(db.Integer, index=True, nullable=False)
    addons = db.Column(db.JSON, default=dict)

    status = db.Column(
        db.String(20),
        nullable=False,
        default="in_kitchen",
        server_default="in_kitchen"
    )

    store_id = db.Column(
        "fk_order_store_id",
        db.Integer,
        db.ForeignKey("stores.id", name="fk_order_store_id", ondelete="CASCADE"),
        nullable=False,
    )

    customer_name = db.Column(db.String(120))
    payment_method = db.Column(db.String(50))
    total = db.Column(db.Numeric(10, 2))
    line_items = db.Column(db.JSON)

