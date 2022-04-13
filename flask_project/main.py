from flask import Flask, render_template
from data import db_session


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db\shop.db")
    app.run()


@app.route("/")
def index():
    #db_sess = db_session.create_session()
    return render_template("index.html")

@app.route("/card/<int:id>")
def card(id):
    #db_sess = db_session.create_session()
    return render_template("card.html")

@app.route("/register")
def register():
    #db_sess = db_session.create_session()
    return render_template("register.html")

@app.route("/login")
def login():
    #db_sess = db_session.create_session()
    return render_template("login.html")

@app.route("/checkout")
def checkout():
    #db_sess = db_session.create_session()
    return render_template("cart.html")


@app.route("/add")
def add():
    #db_sess = db_session.create_session()
    return render_template("add_product.html")
      
if __name__ == '__main__':

    main()