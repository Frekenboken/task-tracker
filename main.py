import secrets
import time

from flask import Flask, render_template, redirect, request, make_response, session, abort
from data import db_session
from data.users import User
from data.news import News
from data.tasks import Tasks
from forms.newsform import NewsForm
from forms.loginform import LoginForm
from forms.tasksform import TasksForm
from forms.registerform import RegisterForm
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = secrets.token_hex(16)
db_session.global_init("data/database.db")
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def hello():
    db_sess = db_session.create_session()
    return render_template("hello.html")


@app.route("/home")
def home_base():
    return redirect("/home/123")


@app.route("/homeGetTime")
def home_with_local_time():
    return render_template("homeGetTime.html")


@app.route("/getTime", methods=['GET'])
def get_time():
    print("browser time: ", request.args.get("time"))
    print("server time : ", time.strftime('%A %B, %d %Y %H:%M:%S'))

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == current_user.email).first()
    user.time_zone = int(request.args.get("time")) // 60
    db_sess.commit()

    print(db_sess.query(User).filter(User.email == current_user.email).first().to_dict())

    return "Done"


@app.route("/home/<string:date>", methods=['GET', 'POST'])
def home(date):
    if not current_user.is_authenticated:
        return redirect("/login")

    form = TasksForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        task = Tasks(
            name=form.name.data,
            day=form.day.data
        )
        db_sess.add(task)
        db_sess.commit()
        return redirect("/home")

    tasks = [x.to_dict() for x in db_sess.query(Tasks).all()]
    return render_template("home.html", form=form, tasks=tasks)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/homeGetTime")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


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
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)
