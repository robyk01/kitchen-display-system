"""orders unique per store

Revision ID: 2148f8677d45
Revises: d185e95223d9
Create Date: 2025-12-30 18:46:57.246548

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2148f8677d45'
down_revision = 'd185e95223d9'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("orders")

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("woo_order_id", sa.Integer(), nullable=False),
        sa.Column("fk_order_store_id", sa.Integer(), nullable=False),
        sa.Column("addons", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="in_kitchen", nullable=False),
        sa.Column("customer_name", sa.String(length=120), nullable=True),
        sa.Column("payment_method", sa.String(length=50), nullable=True),
        sa.Column("total", sa.Numeric(10, 2), nullable=True),
        sa.Column("line_items", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["fk_order_store_id"],
            ["stores.id"],
            name="fk_order_store_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("fk_order_store_id", "woo_order_id", name="uq_orders_store_woo_order"),
    )

    op.create_index("ix_orders_woo_order_id", "orders", ["woo_order_id"])


def downgrade():
    op.drop_index("ix_orders_woo_order_id", table_name="orders")
    op.drop_table("orders")

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("woo_order_id", sa.Integer(), nullable=False),
        sa.Column("fk_order_store_id", sa.Integer(), nullable=False),
        sa.Column("addons", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="in_kitchen", nullable=False),
        sa.Column("customer_name", sa.String(length=120), nullable=True),
        sa.Column("payment_method", sa.String(length=50), nullable=True),
        sa.Column("total", sa.Numeric(10, 2), nullable=True),
        sa.Column("line_items", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["fk_order_store_id"],
            ["stores.id"],
            name="fk_order_store_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("woo_order_id", name="uq_orders_woo_order_id"),
    )

    op.create_index("ix_orders_woo_order_id", "orders", ["woo_order_id"])