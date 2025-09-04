from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    woo_order_id = db.Column(db.Integer, unique=True, index=True, nullable=False)

    status = db.Column(
        db.Enum("in_kitchen", "ready", "delivered", name="kds_status_enum"),
        nullable=False,
        default="in_kitchen",
        server_default="in_kitchen"
    )

    customer_name = db.Column(db.String(120))
    payment_method = db.Column(db.String(50))

    delivery_method = db.Column(db.String(50))
    delivery_date = db.Column(db.String(12))
    delivery_time_slot = db.Column(db.String(50))

    time_slot_start_time = db.Column(db.String(50))
    time_slot_end_time = db.Column(db.String(50))
    time_slot_fee = db.Column(db.String(50))

    total = db.Column(db.Numeric(10, 2))
    line_items = db.Column(db.JSON)
