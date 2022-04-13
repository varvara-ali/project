from email.policy import default
import sqlalchemy
from datetime import datetime
from .db_session import SqlAlchemyBase


class Order(SqlAlchemyBase):
    __tablename__ = "orders"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    order_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now())
    
    user = sqlalchemy.orm.relation("User")
    order_content = sqlalchemy.orm.relation("OrderContent", back_populates='order')
