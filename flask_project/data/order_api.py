from flask_restful import reqparse, abort, Api, Resource
from flask import Blueprint, jsonify, request
from . import db_session
from .products import Product


# этот файл в магазине не используется. Сделан, чтобы просто сделать и повторить

blueprint = Blueprint(
    'orders_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/orders')
def get_orders():
    db_sess = db_session.create_session()
    products = db_sess.query(Product).all()
    return jsonify(
        {
            'news':
                [item.to_dict(only=('name', 'description')) 
                 for item in products]
        }
    )


@blueprint.route('/api/orders/<int:product_id>', methods=['GET'])
def get_one_news(product_id):
    db_sess = db_session.create_session()
    product = db_sess.query(Product).get(product_id)
    if not product:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'product': product.to_dict(only=(
                'name', 'description', 'price', 'arrival_date'))
        }
    )
    
    
@blueprint.route('/api/orders', methods=['POST'])
def create_news():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['name', 'description', 'sku', 'price']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    product = Product(
        name=request.json['name'],
        description=request.json['description'],
        sku=request.json['sku'],
        price=request.json['price'],
    )
    db_sess.add(product)
    db_sess.commit()
    return jsonify({'success': 'OK'})
    
