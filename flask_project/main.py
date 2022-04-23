import os
from datetime import datetime
from transliterate import translit
from flask import Flask, render_template, redirect, session, abort, request, make_response, jsonify
from data import db_session, order_api
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from data.users import User
from data.products import Product
from data.orders import OrderContent, Order
from forms.loginform import LoginForm, RegisterForm
from forms.product_card import ProductForm, ItemForm
from werkzeug.utils import secure_filename
from sqlalchemy import func
from sqlalchemy import desc

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith('/api/'):
        return make_response(jsonify({'error': 'Not found'}), 404)
    return render_template('404.html'), 404


def main():
    db_session.global_init(r"/home/varvara/flask-master/flask_project/db/shop.db")
    app.register_blueprint(order_api.blueprint)
    app.run()


@app.route("/")
def index():
    db_sess = db_session.create_session()
    items = db_sess.query(Product).order_by(Product.id).all()
    # db_sess = db_session.create_session()
    return render_template("index.html",
                           title='Магазин Шмагазин',
                           items=items)


@app.route("/new")
def new():
    db_sess = db_session.create_session()
    items = db_sess.query(Product).order_by(Product.arrival_date.desc()).all()
    # db_sess = db_session.create_session()
    return render_template("index.html",
                           title='Магазин Шмагазин',
                           items=items)


@app.route("/popular")
def popular():
    db_sess = db_session.create_session()
    items = (db_sess
             .query(OrderContent, func.count(Product.id).label('total'))
             .join(Product)
             .group_by(Product)
             .order_by(desc('total'))
             .limit(4)
             .all()
    )
    return render_template("index.html",
                           title='Магазин Шмагазин',
                           items=[i[0].product for i in items])


@app.route("/about")
def about():
    return render_template("about.html",
                           title='О Магазине Шмагазине')


@app.route("/card/<int:id>")
def card(id):
    form = ItemForm(product_id=id)
    db_sess = db_session.create_session()
    item = db_sess.query(Product).filter(Product.id == id).first()
    if not item:
        abort(404)

    related = db_sess.query(Product).filter(Product.id >= id - 2, Product.id < id).all() + db_sess.query(
        Product).filter(Product.id <= id + 2, Product.id > id).all()

    return render_template("card.html",
                           title=f'{item.name} - купить за {item.price} с доставкой',
                           item=item,
                           related=related,
                           form=form
                           )


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        user.role = 0
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    form = ItemForm()
    db_sess = db_session.create_session()
    if db_sess.query(Product).filter(Product.id == form.product_id.data).first():
        print(type(form.product_id.data))
        if 'order' in session:
            if form.product_id.data in session['order']:
                session['order'][form.product_id.data] += form.quantity.data
            else:
                session['order'][form.product_id.data] = form.quantity.data
            session['order_volume'] += form.quantity.data
        else:
            session['order'] = {form.product_id.data: form.quantity.data}
            session['order_volume'] = form.quantity.data
        print(session['order'])
    return redirect(f'/card/{form.product_id.data}')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               title='Авторизация',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/checkout", methods=['GET', 'POST'])
def checkout():
    if not current_user.is_authenticated:
        return redirect("/login")

    result = []
    state = None
    if request.method == 'GET':
        if 'order' in session:
            db_sess = db_session.create_session()
            items = db_sess.query(Product).filter(Product.id.in_(session['order'].keys())).all()
        else:
            state = 'emptycart'
            items = []

        for item in items:
            print(item.id)
            result.append(
                {
                    'id': str(item.id),
                    'name': item.name,
                    'image': item.image,
                    'price': item.price,
                    'quantity': session['order'][str(item.id)]
                }
            )
    else:
        db_sess = db_session.create_session()
        order = Order(user_id=current_user.id)
        db_sess.add(order)
        for product_id in request.form.keys():
            order_content = OrderContent(
                order=order,
                product_id=int(product_id),
                quantity=int(request.form[product_id])
            )
            db_sess.add(order_content)
            db_sess.commit()
        if 'order' in session:
            session.pop('order')
            session.pop('order_volume')

        state = 'order'
    return render_template("cart.html",
                           title='Корзина',
                           state=state,
                           items=result)


@app.route("/add", methods=['GET', 'POST'])
@login_required
def add():
    if current_user.role != 1:
        return redirect('/')

    form = ProductForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        same_product = db_sess.query(Product).filter(Product.sku == form.sku.data).first()
        if same_product:
            return render_template('add_product.html', title='Добавление товара',
                                   form=form,
                                   message=f"Товар с таким артикулом уже есть в базе <a href = '/card/{same_product.id}'>{same_product.name}</a>")

        if form.image.data:
            f = form.image.data
            filename = secure_filename(translit(form.sku.data, "ru", reversed=True) + f.filename)
            f.save(f'static/products_images/{filename}')
        else:
            filename = 'dummy.png'

        product = Product(
            name=form.name.data,
            description=form.description.data,
            image=filename,
            sku=form.sku.data,
            price=form.price.data,
            arrival_date=datetime.now()
        )
        db_sess.add(product)
        db_sess.commit()
        db_sess.refresh(product)
        return redirect(f'/card/{product.id}')
    return render_template('add_product.html', title='Добавление товара', form=form)


@app.route("/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def edit(id):
    if current_user.role != 1:
        return redirect('/')
    photo = None
    form = ProductForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        product = db_sess.query(Product).filter(Product.id == id).first()
        if product:
            form.name.data = product.name
            form.description.data = product.description
            form.sku.data = product.sku
            form.price.data = product.price
            photo = product.image
        else:
            abort(404)

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        product = db_sess.query(Product).filter(Product.id == id).first()
        if product:
            if form.image.data:
                f = form.image.data
                filename = secure_filename(translit(form.sku.data, "ru", reversed=True) + f.filename)
                f.save(f'static/products_images/{filename}')
                product.image = filename

            product.name = form.name.data
            product.description = form.description.data
            product.sku = form.sku.data
            product.price = form.price.data
            product.arrival_date = datetime.now()
            db_sess.commit()
            return redirect(f'/card/{product.id}')
        else:
            abort(404)
    return render_template('add_product.html', title='Изменение товара', form=form, photo=photo)


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    if current_user.role != 1:
        return redirect('/')
    db_sess = db_session.create_session()
    product = db_sess.query(Product).filter(Product.id == id).first()
    if product:
        if product.image != "dummy.png":
            os.remove(f'static/products_images/{product.image}')
        db_sess.delete(product)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


if __name__ == '__main__':
    main()
