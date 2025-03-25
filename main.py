from flask import Flask


def create_app():
    app = Flask(__name__)

    # Импортируем и регистрируем маршруты
    with app.app_context():
        from routes import init_app_routes
        init_app_routes(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
    app.run(debug=True)
