from __future__ import annotations

from sqlalchemy import (
    INTEGER,
    SMALLINT,
    TIMESTAMP,
    VARCHAR,
    Column,
    ForeignKey,
    Identity,
    Integer,
    Table,
    func,
    text,
)
from sqlalchemy.orm import registry, relationship
from sqlalchemy.sql import expression

from entities.models.order import Order
from entities.models.order_item import OrderItem
from entities.models.product import Product
from entities.models.user import User

mapper_registry = registry()


class Model:
    __init__ = mapper_registry.constructor
    __table__: Table


@mapper_registry.mapped
class OrderModel(Order, Model):
    __table__ = Table(
        "orders",
        mapper_registry.metadata,
        Column(
            "id",
            INTEGER,
            Identity(always=True, cache=5),
            nullable=False,
            primary_key=True,
        ),
        Column(
            "created_at",
            TIMESTAMP(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        Column("order_date", TIMESTAMP(timezone=True), nullable=False),
        Column(
            "user_id",
            ForeignKey(
                "users.id",
                name="FK__order_items_user",
            ),
        ),
    )

    __mapper_args__ = {  # type: ignore
        "properties": {
            "products": relationship(
                "ProductModel",
                secondary=lambda: OrderItemModel.__table__,
                back_populates="orders",
                enable_typechecks=True,
                lazy="joined",
            ),
            "user": relationship(
                "UserModel",
                back_populates="orders",
                enable_typechecks=True,
                lazy="joined",
                uselist=False,
            ),
        }
    }


@mapper_registry.mapped
class ProductModel(Product, Model):
    __table__ = Table(
        "products",
        mapper_registry.metadata,
        Column(
            "id",
            INTEGER,
            Identity(always=True, cache=5),
            nullable=False,
            primary_key=True,
        ),
        Column(
            "created_at",
            TIMESTAMP(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
        Column("price", INTEGER, nullable=False),  # store price in cents
        Column("weight", SMALLINT, nullable=False, server_default=text("1")),
    )

    __mapper_args__ = {  # type: ignore
        "properties": {
            "orders": relationship(
                "OrderModel",
                secondary=lambda: OrderItemModel.__table__,  # type: ignore
                back_populates="products",
                enable_typechecks=True,
            )
        }
    }


@mapper_registry.mapped
class OrderItemModel(OrderItem, Model):
    __table__ = Table(
        "order_items",
        mapper_registry.metadata,
        Column(
            "id",
            INTEGER,
            Identity(always=True, cache=5),
            nullable=False,
            primary_key=True,
        ),
        Column(
            "order_id",
            INTEGER,
            ForeignKey(
                "orders.id",
                ondelete="CASCADE",
                onupdate="CASCADE",
                name="FK__order_items__order_item_order",
            ),
            nullable=False,
            unique=True,
        ),
        Column(
            "product_id",
            Integer,
            ForeignKey(
                "products.id",
                ondelete="CASCADE",
                onupdate="CASCADE",
                name="FK__order_items__order_item_product",
            ),
        ),
        Column("quantity", SMALLINT, nullable=False, server_default=text("1")),
    )


@mapper_registry.mapped
class UserModel(User, Model):
    __table__ = Table(
        "users",
        mapper_registry.metadata,
        Column(
            "id",
            INTEGER,
            Identity(always=True, cache=5),
            nullable=False,
            primary_key=True,
        ),
        Column("first_name", VARCHAR(200), nullable=False),
        Column("last_name", VARCHAR(200), nullable=False),
        Column("username", VARCHAR(200), nullable=False),
        Column(
            "hashed_password",
            VARCHAR(200),
            server_default=expression.null(),
            nullable=True,
        ),
    )

    __mapper_args__ = {  # type: ignore
        "properties": {
            "orders": relationship(
                "OrderModel",
                back_populates="user",
                enable_typechecks=True,
            )
        }
    }
