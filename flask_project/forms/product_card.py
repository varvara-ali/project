from flask_wtf import FlaskForm
from wtforms import  StringField, SubmitField, TextAreaField, FileField, FloatField, IntegerField, HiddenField
from flask_wtf.file import  FileField
from wtforms.validators import DataRequired, NumberRange

  
class ProductForm(FlaskForm):
    name = StringField('Название товара', validators=[DataRequired()])
    description = TextAreaField('Описание товара', validators=[DataRequired()])
    image = FileField('Изображение') # , validators=[FileRequired()]
    sku = StringField('Артикул', validators=[DataRequired()])
    price = FloatField('Цена', validators=[DataRequired(), NumberRange(min=1, max=999999999, message="Введите правильную цену")])
    submit = SubmitField('Добавить товар')
    
class ItemForm(FlaskForm):
    quantity = IntegerField("Количество", validators=[DataRequired()])
    product_id = HiddenField()
    submit = SubmitField('Добавить в корзину')