from email.policy import default
import sqlalchemy
from datetime import datetime
from .db_session import SqlAlchemyBase


class OrderContent(SqlAlchemyBase):
    __tablename__ = "orders_content"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    order_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("orders.id"))
    product_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("products.id"))
    quantity = sqlalchemy.Column(sqlalchemy.Integer)
    
    order = sqlalchemy.orm.relation("Order")
    proudct = sqlalchemy.orm.relation("Product")
