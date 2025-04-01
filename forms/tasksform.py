from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, TimeField, HiddenField
from wtforms.validators import DataRequired, Optional, ValidationError


def validate_times(form, field):
    # Если оба времени заполнены
    if form.start_time.data and form.end_time.data:
        if form.start_time.data >= form.end_time.data:
            raise ValidationError('Время окончания должно быть позже времени начала')


class TimeTaskForm(FlaskForm):
    form_type = HiddenField(default='time_task')

    name = StringField('Имя', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[])
    start_time = TimeField('Время начала', validators=[DataRequired()])
    end_time = TimeField('Время завершения', validators=[Optional(), validate_times])
    submit = SubmitField('Добавить')


class ShortTaskForm(FlaskForm):
    form_type = HiddenField(default='short_task')

    name = StringField('Имя', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[])
    submit = SubmitField('Добавить')


class CommonTaskForm(FlaskForm):
    form_type = HiddenField(default='common_task')

    name = StringField('Имя', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[])
    submit = SubmitField('Добавить')
