from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired, FileSize
from wtforms.fields.simple import EmailField, PasswordField, BooleanField, SubmitField, StringField
from wtforms.validators import DataRequired


class SettingsForm(FlaskForm):
    avatar = FileField('Загрузить новый аватар', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Тип файла не поддерживается'),
        FileSize(max_size=2 * 1024 * 1024, message='Размер файла не должен превышать 2MB')
    ])
    submit = SubmitField('Сохранить изменения')