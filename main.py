import locale
import math
import os
import secrets
from flask import Flask, render_template, redirect, request, make_response, session, abort, flash
from data import db_session
from data.users import User
from data.tasks import ShortTask, TimeTask, CommonTask
from data.db_session import init_db
from data.db_session import db
from forms.loginform import LoginForm
from forms.tasksform import TimeTaskForm, ShortTaskForm, CommonTaskForm
from forms.registerform import RegisterForm
from forms.settingsform import SettingsForm
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_restful import reqparse, abort, Api, Resource
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime, time, timedelta
import pytz
from werkzeug.utils import secure_filename

from utils import group_time_tasks, delta_times, get_random_quote

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = secrets.token_hex(16)

init_db(app, "../data/database.db")

login_manager = LoginManager()
login_manager.init_app(app)

if os.name == 'nt':  # Windows
    locale.setlocale(locale.LC_TIME, 'rus')
else:  # Linux/MacOS/Unix
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


@app.route("/hello")
def hello():
    return render_template("hello.html")


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect("/home")
    return render_template("hello.html")


@app.route("/home")
def home_base():
    if not current_user.is_authenticated:
        return redirect("/login")

    user_time_zone = str(db.session.query(User.time_zone).filter(User.email == current_user.email).first()[0])

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

    if request.form.get('form_type') == 'time_task' and time_task_form.validate_on_submit():
        print(time_task_form.data)
        if not time_task_form.edit_id.data:
            task = TimeTask()

            task.name = time_task_form.name.data
            task.description = time_task_form.description.data
            task.start_time = time_task_form.start_time.data
            task.end_time = time_task_form.end_time.data if time_task_form.end_time.data else time_task_form.start_time.data
            task.duration = delta_times(time_task_form.start_time.data,
                                        time_task_form.end_time.data) if time_task_form.end_time.data else time(0, 0)
            task.date = datetime.strptime(date, "%Y-%m-%d").date()
            current_user.time_tasks.append(task)
            db.session.merge(current_user)
        else:
            task = db.session.query(TimeTask).filter(TimeTask.id == time_task_form.edit_id.data,
                                                     TimeTask.user == current_user
                                                     ).first()

            task.name = time_task_form.name.data
            task.description = time_task_form.description.data
            task.start_time = time_task_form.start_time.data
            task.end_time = time_task_form.end_time.data if time_task_form.end_time.data else time_task_form.start_time.data
            task.duration = delta_times(time_task_form.start_time.data,
                                        time_task_form.end_time.data) if time_task_form.end_time.data else time(0, 0)

        db.session.commit()

        return redirect(f"/home/{date}")

    elif request.form.get('form_type') == 'short_task' and short_task_form.validate_on_submit():
        if not short_task_form.edit_id.data:
            task = ShortTask()
            task.name = short_task_form.name.data
            task.description = short_task_form.description.data
            task.date = datetime.strptime(date, "%Y-%m-%d").date()
            current_user.short_tasks.append(task)
            db.session.merge(current_user)
        else:
            task = db.session.query(ShortTask).filter(ShortTask.id == short_task_form.edit_id.data,
                                                      ShortTask.user == current_user
                                                      ).first()
            task.name = short_task_form.name.data
            task.description = short_task_form.description.data

        db.session.commit()

        return redirect(f"/home/{date}")

    elif request.form.get('form_type') == 'common_task' and common_task_form.validate_on_submit():
        if not common_task_form.edit_id.data:
            task = CommonTask()

            task.name = common_task_form.name.data
            task.description = common_task_form.description.data
            current_user.common_tasks.append(task)
            db.session.merge(current_user)
        else:
            task = db.session.query(CommonTask).filter(CommonTask.id == common_task_form.edit_id.data,
                                                       CommonTask.user == current_user
                                                       ).first()
            task.name = common_task_form.name.data
            task.description = common_task_form.description.data

        db.session.commit()

        return redirect(f"/home/{date}")

    if request.args.get('edit_task'):
        edit_task_type, edit_task_id = request.args.get('edit_task').split('.')

        if edit_task_type == 'time':
            task = db.session.query(TimeTask).filter(TimeTask.id == int(edit_task_id),
                                                     TimeTask.user == current_user
                                                     ).first()
            time_task_form.edit_id.data = task.id
            time_task_form.name.data = task.name
            time_task_form.description.data = task.description
            time_task_form.start_time.data = task.start_time
            time_task_form.end_time.data = task.end_time

        elif edit_task_type == 'short':
            task = db.session.query(ShortTask).filter(ShortTask.id == int(edit_task_id),
                                                      ShortTask.user == current_user
                                                      ).first()
            short_task_form.edit_id.data = task.id
            short_task_form.name.data = task.name
            short_task_form.description.data = task.description

        elif edit_task_type == 'common':
            task = db.session.query(CommonTask).filter(CommonTask.id == int(edit_task_id),
                                                       CommonTask.user == current_user
                                                       ).first()
            common_task_form.edit_id.data = task.id
            common_task_form.name.data = task.name
            common_task_form.description.data = task.description

    time_tasks = [x.to_dict() for x in
                  db.session.query(TimeTask).filter(TimeTask.date == date, TimeTask.user == current_user).all()]

    tasks = {
        'time': {
            'all': time_tasks,
            'grouped': group_time_tasks(time_tasks)
        },
        'short': {
            'all': [x.to_dict() for x in
                    db.session.query(ShortTask).filter(ShortTask.date == date, ShortTask.user == current_user).all()],
        },
        'common': {
            'all': [x.to_dict() for x in db.session.query(CommonTask).filter(CommonTask.user == current_user).all()],
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
                           date=date,
                           fdate=datetime.strptime(date, "%Y-%m-%d").date().strftime("%A, %d %B %Y"),
                           tasks=tasks,
                           forms=forms,
                           form_errors=form_errors)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)

            user.time_zone = form.time_zone.data
            db.session.commit()

            return redirect("/home")

        flash('Неправильный логин или пароль')
        return render_template('login.html',
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            flash('Пароли не совпадают')
            return render_template('register.html', title='Регистрация',
                                   form=form)
        if db.session.query(User).filter(User.email == form.email.data).first():
            flash('Такой пользователь уже есть')
            return render_template('register.html', title='Регистрация',
                                   form=form)
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/delete_time_task')
@app.route('/delete_short_task')
@app.route('/delete_common_task')
@login_required
def tasks_delete():
    page_date = request.args.get('page_date', default=None)
    task_id = request.args.get('task_id', default=None)

    if request.path == '/delete_time_task':
        task = db.session.query(TimeTask).filter(TimeTask.id == task_id, TimeTask.user == current_user).first()
    elif request.path == '/delete_short_task':
        task = db.session.query(ShortTask).filter(ShortTask.id == task_id, ShortTask.user == current_user).first()
    else:
        task = db.session.query(CommonTask).filter(CommonTask.id == task_id, CommonTask.user == current_user).first()

    if task:
        db.session.delete(task)
        db.session.commit()
    else:
        abort(404)
    return redirect(f'/home/{page_date}')


@app.route('/move_time_task')
@app.route('/move_short_task')
@login_required
def tasks_move():
    page_date = request.args.get('page_date', default=None)

    if request.path == '/move_time_task':
        tasks = db.session.query(TimeTask).filter(TimeTask.user == current_user, TimeTask.done.is_(False)).all()
    elif request.path == '/move_short_task':
        tasks = db.session.query(ShortTask).filter(ShortTask.user == current_user, ShortTask.done.is_(False)).all()

    if tasks:
        for task in tasks:
            # Перемещаем дату задачи на следующий день
            task.date = task.date + timedelta(days=1)
        db.session.commit()  # Сохраняем изменения для всех задач
    else:
        return redirect(f'/home/{page_date}')
    return redirect(
        f'/home/{(datetime.strptime(page_date, "%Y-%m-%d").date() + timedelta(days=1)).strftime('%Y-%m-%d')}')


@app.route('/check_time_task')
@app.route('/check_short_task')
@app.route('/check_common_task')
@login_required
def tasks_check():
    page_date = request.args.get('page_date', default=None)
    task_id = request.args.get('task_id', default=None)

    if request.path == '/check_time_task':
        task = db.session.query(TimeTask).filter(TimeTask.id == task_id, TimeTask.user == current_user).first()
    elif request.path == '/check_short_task':
        task = db.session.query(ShortTask).filter(ShortTask.id == task_id, ShortTask.user == current_user).first()
    else:
        task = db.session.query(CommonTask).filter(CommonTask.id == task_id, CommonTask.user == current_user).first()

    if task:
        task.done = not task.done
        db.session.commit()
    else:
        abort(404)
    return redirect(f'/home/{page_date}')


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if not current_user.is_authenticated:
        return redirect("/login")

    form = SettingsForm()
    if form.validate_on_submit():
        if form.avatar.data:
            try:
                current_user.avatar = form.avatar.data.read()
                db.session.merge(current_user)
                db.session.commit()

                flash('Аватар успешно обновлен!', 'success')
            except Exception as e:
                flash(f'Ошибка при сохранении файла', 'error')

    return render_template('settings.html', form=form, quote=get_random_quote())


@app.route('/user_avatar')
def user_avatar():
    response = make_response(current_user.avatar)
    response.headers.set('Content-Type', 'image/jpeg')
    response.headers.set('Content-Disposition', 'inline', filename='avatar.jpg')
    return response


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)
