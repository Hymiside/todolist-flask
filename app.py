from flask import Flask, render_template, request, redirect, url_for, make_response
from hashlib import sha256
from uuid import uuid4
from models import db
from models import User, Task

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.app = app
db.init_app(app)


@app.route('/')
def home_login():
    return render_template('new_base.html')


@app.route('/choose', methods=["POST"])
def choose_action():
    index = request.form['index']
    if index == '1':
        return render_template('login.html')
    elif index == '2':
        return render_template('signup.html')
    return render_template('new_base.html')


@app.route('/login', methods=["POST", "GET"])
def user_login():
    login_username = request.form.get('username')
    login_password = request.form.get('password')

    if not login_username or not login_password:
        return render_template('login.html')

    rows = User.query.filter_by(username=login_username).all()
    if len(rows) == 0:
        return False

    s = rows[0].salt
    h = rows[0].hash

    if h == sha256((str(login_password + s)).encode('utf-8')).hexdigest():
        res = make_response(render_template('base.html'))
        res.set_cookie('user_id', login_username, max_age=10)
        return res

    return render_template('login.html')


@app.route('/registration', methods=["POST"])
def user_registration():
    login_username = request.form.get('username')
    login_password = request.form.get('password')

    if not login_username or not login_password:
        return render_template('signup.html')

    salt = str(uuid4().int)
    h = sha256((str(login_password + salt)).encode('utf-8')).hexdigest()

    new_user = User(username=login_username, hash=str(h), salt=salt)
    db.session.add(new_user)
    db.session.commit()

    return render_template('successful.html')


@app.route("/tasks")
def home():
    user_id = request.cookies.get('user_id')
    if user_id == '':
        return render_template('login.html')
    todo_list = Task.query.filter_by(user_id=user_id).all()
    return render_template("base.html", todo_list=todo_list)


@app.route("/tasks/add", methods=["POST", "GET"])
def add():
    user_id = request.cookies.get('user_id')
    if user_id == '':
        return render_template('login.html')

    title = request.form.get("title")
    if title != '':
        new_todo = Task(title=title, complete=False, user_id=user_id)
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for("home"))
    return redirect(url_for("home"))


@app.route("/tasks/update/<int:todo_id>")
def update(todo_id):
    todo = Task.query.filter_by(id=todo_id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/tasks/delete/<int:todo_id>")
def delete(todo_id):
    todo = Task.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))


if __name__ == "__main__":
    db.create_all()
    app.run()
