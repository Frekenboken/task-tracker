from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class TasksForm(FlaskForm):
    name = StringField('Имя задачи', validators=[DataRequired()])
    # desc = TextAreaField("Описание")
    day = StringField('День недели', validators=[DataRequired()])
    submit = SubmitField('Применить')