from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app, db_file):
    if not db_file or not db_file.strip():
        raise Exception("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    app.config['SQLALCHEMY_DATABASE_URI'] = conn_str
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()