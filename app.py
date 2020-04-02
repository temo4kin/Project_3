import json
from datetime import datetime
from os import path
from random import sample
from flask import Flask, render_template, request
from data import goals_all, weekdays, teachers
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField

year = datetime.now().year


app = Flask(__name__)
app.secret_key = 'randomstring'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teachers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    about = db.Column(db.Text)
    rating = db.Column(db.Float)
    picture = db.Column(db.String)
    price = db.Column(db.Integer)
    goals = db.Column(db.String)
    free = db.Column(db.Text)

    bookings = db.relationship('Booking', back_populates='teacher_booking')


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    weekday = db.Column(db.String(10))
    time = db.Column(db.String)
    name = db.Column(db.String)
    phone = db.Column(db.String)

    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    teacher_booking = db.relationship('Teacher', back_populates='bookings')


class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String)
    time = db.Column(db.String)
    name = db.Column(db.String)
    phone = db.Column(db.String)


class Goal(db.Model):
    __tablename__ = 'goals'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    emoji = db.Column(db.String(1))
    name_rus = db.Column(db.String(20))


db.create_all()


class MyForm(FlaskForm):
    weekday = HiddenField('День недели')
    time = HiddenField('Время занятия')
    name = StringField('Вас зовут')
    phone = StringField('Ваш телефон')
    teacher_id = HiddenField('ID преподавателя')

check_file = path.exists('teachers.db')
if not check_file:
    for teacher in teachers:
        goals = json.dumps(teacher['goals'])
        free = json.dumps(teacher['free'])
        teacher = Teacher(id=teacher['id'], name=teacher['name'],
                          about=teacher['about'], rating=teacher['rating'],
                          picture=teacher['picture'], price=teacher['price'],
                          goals=goals, free=free)
        db.session.add(teacher)

        number = 0

    db.session.commit()

    for key, goal in goals_all.items():
        goal = Goal(id=number, name=key, emoji=goal[0], name_rus=goal[1])
        number += 1
        db.session.add(goal)

    db.session.commit()

teachers = db.session.query(Teacher).all()
goals_all = db.session.query(Goal).all()


@app.route('/')
def index():
    teachers_random = sample(teachers, 6)
    return render_template(
        'index.html',
        goals_all=goals_all,
        teachers_random=teachers_random,
        teachers=teachers,
        year=year
    )

@app.route('/all')
def all():
    return render_template('all.html', goals_all=goals_all, teachers=teachers, year=year)

@app.route('/goal/<goal_name>/')
def goal(goal_name):
    teachers_goal = []
    for teacher in teachers:
        if goal_name in teacher.goals:
            teachers_goal.append(teacher)
    goals_query = db.session.query(Goal).filter(Goal.name == goal_name).all()
    return render_template(
        'goal.html',
        goals_all=goals_query,
        teachers_goal=teachers_goal,
        year=year
    )


@app.route('/profile/<int:uin>')
def profile(uin):
    work_week = {}
    days_week = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    num = 0
    free = json.loads(teachers[uin].free)
    teacher_goals = json.loads(teachers[uin].goals)
    for day in free:
        free_slots = {x: True for x in free[day].keys() if free[day][x] == True}
        work_week[days_week[num]] = free_slots
        num += 1

    teacher_goals_numbers = []

    for t in teacher_goals:
        k = 0
        for i in goals_all:
            if t == i.name:
                teacher_goals_numbers.append(k)
            k += 1
    teacher_goals_numbers.sort()

    return render_template(
        'profile.html',
        teachers=teachers,
        uin=uin,
        goals_all=goals_all,
        teacher_goals_numbers=teacher_goals_numbers,
        weekdays=weekdays,
        work_week=work_week,
        year=year
    )


@app.route('/request')
def request_client():
    return render_template('request.html', year=year)


@app.route('/request_done', methods=['POST'])
def request_done():
    goal = request.form.get('goal')
    time = request.form.get('time')
    client_name_request = request.form.get('clientName')
    client_phone_request = request.form.get('clientPhone')
    request_client = dict(goal=goal,
                          time=time,
                          name=client_name_request,
                          phone=client_phone_request)
    with open('request.json', 'a') as f:
        json.dump(request_client, f)
    return render_template(
        'request_done.html',
        goals_teachers=goals_all,
        goal=goal,
        time=time,
        client_name_request=client_name_request,
        client_phone_request=client_phone_request,
        year=year
    )


@app.route('/booking/<int:teacher_id>/<day>/<time>', methods=["GET", "POST"])
def booking(teacher_id, day, time):


    print(teacher_id, day, time, weekdays[day])

    if request.method == "POST":
        form = MyForm()
        booking_new = Booking()

        form.populate_obj(booking_new)

        print(teacher_id, day, time, weekdays[day])


        db.session.add(booking_new)
        db.session.commit()


        
        return render_template(
            'booking_done.html',
            weekday=weekdays[day],
            time=time,
            teacher_id=teacher_id,
            name=name,
            phone=phone,
            year=year,
        )
    else:
        form = MyForm()
        print('Демонстрация формы')
        return render_template(
            'booking.html',
            form=form,
            teachers=teachers,
            teacher_id=teacher_id,
            weekdays=weekdays,
            day=day,
            time=time,
            year=year
        )

@app.errorhandler(500)
def render_server_error(error):
    return render_template(
        '500.html',
        goals_all=goals_all,
        year=year
    ), 500


@app.errorhandler(404)
def render_not_found(error):
    return render_template(
        '404.html',
        goals_all=goals_all,
        year=year
    ), 404


if __name__ == '__main__':
    app.run()
