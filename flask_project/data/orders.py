from email.policy import default
import sqlalchemy
from datetime import datetime
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Order(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "orders"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    order_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now())
    
    user = sqlalchemy.orm.relation("User")
    order_content = sqlalchemy.orm.relation("OrderContent", back_populates='order')


class OrderContent(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "orders_content"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    order_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("orders.id"))
    product_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("products.id"))
    quantity = sqlalchemy.Column(sqlalchemy.Integer)
    
    order = sqlalchemy.orm.relation("Order")
    product = sqlalchemy.orm.relation("Product")