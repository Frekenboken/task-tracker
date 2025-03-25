from flask import render_template, url_for, redirect

from forms import LoginForm


def init_app_routes(app):
    """Инициализация маршрутов для Flask приложения."""

    @app.route('/')
    def home():
        """Обработчик для главной страницы."""
        return render_template('index.html', style=url_for('static', filename='css/style.css'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            return redirect('/success')
        return render_template('login.html', title='Авторизация', form=form)
