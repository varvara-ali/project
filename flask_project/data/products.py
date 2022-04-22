from email.policy import default
import sqlalchemy
from datetime import datetime
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Product(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "products"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    image = sqlalchemy.Column(sqlalchemy.String, default = 'dummy.png')
    sku = sqlalchemy.Column(sqlalchemy.String)
    price = sqlalchemy.Column(sqlalchemy.Float)
    arrival_date = sqlalchemy.Column(sqlalchemy.DateTime, default = datetime.now())
    
    order_content = sqlalchemy.orm.relation("OrderContent", back_populates='product')
