import math
import secrets
from flask import Flask, render_template, redirect, request, make_response, session, abort
from data import db_session
from data.users import User
from data.news import News
from data.tasks import ShortTask, TimeTask, CommonTask
from forms.newsform import NewsForm
from forms.loginform import LoginForm
from forms.tasksform import TimeTaskForm, ShortTaskForm, CommonTaskForm
from forms.registerform import RegisterForm
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_restful import reqparse, abort, Api, Resource

from datetime import datetime, time
import pytz

from utils import group_time_tasks, delta_times

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
    if not current_user.is_authenticated:
        return redirect("/login")

    db_sess = db_session.create_session()
    user_time_zone = str(db_sess.query(User.time_zone).filter(User.email == current_user.email).first()[0])

    time_zone = pytz.timezone(user_time_zone)
    current_time = datetime.now(time_zone)
    current_time_str = current_time.strftime('%Y-%m-%d')
    return redirect(f"/home/{current_time_str}")


@app.route("/home/<string:date>", methods=['GET', 'POST'])
def home(date):
    if not current_user.is_authenticated:
        return redirect("/login")

    time_task_form = TimeTaskForm()
    short_task_form = ShortTaskForm()
    common_task_form = CommonTaskForm()

    db_sess = db_session.create_session()

    if request.form.get('form_type') == 'time_task' and time_task_form.validate_on_submit():
        print(type(time_task_form.start_time.data))
        task = TimeTask(
            name=time_task_form.name.data,
            description=time_task_form.description.data,
            start_time=time_task_form.start_time.data,
            end_time=time_task_form.end_time.data if time_task_form.end_time.data else time_task_form.start_time.data,
            duration=delta_times(time_task_form.start_time.data,
                                 time_task_form.end_time.data) if time_task_form.end_time.data else time(0, 0),
            date=datetime.strptime(date, "%Y-%m-%d").date(),
        )
        db_sess.add(task)
        db_sess.commit()
        return redirect("/home")

    elif request.form.get('form_type') == 'short_task' and short_task_form.validate_on_submit():
        task = ShortTask(
            name=short_task_form.name.data,
            description=short_task_form.description.data,
            date=datetime.strptime(date, "%Y-%m-%d").date(),
        )
        db_sess.add(task)
        db_sess.commit()
        return redirect("/home")

    elif request.form.get('form_type') == 'common_task' and common_task_form.validate_on_submit():
        task = CommonTask(
            name=common_task_form.name.data,
            description=common_task_form.description.data,
        )
        db_sess.add(task)
        db_sess.commit()
        return redirect("/home")

    time_tasks = [x.to_dict() for x in db_sess.query(TimeTask).filter(TimeTask.date == date).all()]

    tasks = {
        'time': {
            'all': time_tasks,
            'grouped': group_time_tasks(time_tasks)
        },
        'short': {
            'all': [x.to_dict() for x in db_sess.query(ShortTask).filter(ShortTask.date == date).all()],
        },
        'common': {
            'all': [x.to_dict() for x in db_sess.query(CommonTask).all()],
        }
    }

    forms = {
        'time': time_task_form,
        'short': short_task_form,
        'common': common_task_form
    }

    form_errors = {
        'time': time_task_form.errors,
        'short': short_task_form.errors,
        'common': common_task_form.errors
    }

    return render_template("home.html",
                           tasks=tasks,
                           forms=forms,
                           form_errors=form_errors)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)

            user.time_zone = form.time_zone.data
            db_sess.commit()

            return redirect("/home")

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
