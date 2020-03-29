import json
import datetime
from os import path
from random import sample
from flask import Flask, render_template, request
from data import goals_all, weekdays, teachers
from flask_sqlalchemy import SQLAlchemy

teachers_random = sample(teachers, 6)
year = datetime.datetime.now().year


app = Flask(__name__)
app.secret_key = 'randomstring'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///teachers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

check_file = path.exists('teachers.db')
if not check_file:
    class Teacher(db.Model):
        __tablename__ = 'teachers'

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))
        about = db.Column(db.Text)
        rating = db.Column(db.Float)
        picture = db.Column(db.String)
        price = db.Column(db.Integer)
        goals = db.Column(db.String)
        # free = db.Column(db.Text)

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


    class Free(db.Model):
        __tablename__ = 'teachers_free'

        id = db.Column(db.Integer, primary_key=True)
        teacher_id = db.Column(db.Integer)
        weekday = db.Column(db.String(5))
        time8 = db.Column(db.Boolean)
        time10 = db.Column(db.Boolean)
        time12 = db.Column(db.Boolean)
        time14 = db.Column(db.Boolean)
        time16 = db.Column(db.Boolean)
        time18 = db.Column(db.Boolean)
        time20 = db.Column(db.Boolean)
        time22 = db.Column(db.Boolean)


    db.create_all()

    for teacher in teachers:
        goals = json.dumps(teacher['goals'])
        free = json.dumps(teacher['free'])
        teacher = Teacher(id=teacher['id'], name=teacher['name'],
                          about=teacher['about'], rating=teacher['rating'],
                          picture=teacher['picture'], price=teacher['price'],
                          goals=goals,
                          )
        db.session.add(teacher)

    db.session.commit()

    number = 0

    for key, goal in goals_all.items():
        goal = Goal(id=number, name=key, emoji=goal[0], name_rus=goal[1])
        number += 1
        db.session.add(goal)

    number = 0

    for teacher in teachers:
        for key, free in teacher['free'].items():
            free = Free(teacher_id=number, weekday=key, time8=free['8:00'],
                        time10=free['10:00'], time12=free['12:00'],
                        time14=free['14:00'], time16=free['16:00'],
                        time18=free['18:00'], time20=free['20:00'],
                        time22=free['22:00']
                        )
            db.session.add(free)
        number += 1

    db.session.commit()


@app.route('/')
def index():
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
        if goal_name in teacher['goals']:
            teachers_goal.append(teacher)
    return render_template(
        'goal.html',
        goals_all=goals_all,
        teachers_goal=teachers_goal,
        goal_name=goal_name,
        year=year
    )


@app.route('/profile/<int:uin>')
def profile(uin):
    work_week = {}
    days_week = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    num = 0
    for day in teachers[uin]['free']:
        free_slots = {x: True for x in teachers[uin]['free'][day].keys() if teachers[uin]['free'][day][x] == True}
        work_week[days_week[num]] = free_slots
        num += 1

    return render_template(
        'profile.html',
        teachers=teachers,
        uin=uin,
        goals_all=goals_all,
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


@app.route('/booking/<int:teacher_id>/<day>/<time>')
def booking(teacher_id, day, time):
    return render_template(
        'booking.html',
        teachers=teachers,
        teacher_id=teacher_id,
        weekdays=weekdays,
        day=day,
        time=time,
        year=year
    )


@app.route('/booking_done', methods=['POST'])
def booking_done():
    client_weekday = request.form.get('clientWeekday')
    client_time = request.form.get('clientTime')
    client_teacher = request.form.get('clientTeacher')
    client_name = request.form.get('clientName')
    client_phone = request.form.get('clientPhone')
    client = dict(weekday=client_weekday,
                  time=client_time,
                  teacher=int(client_teacher),
                  name=client_name,
                  phone=client_phone)
    with open('booking.json', 'a') as f:
        json.dump(client, f)
    return render_template(
        'booking_done.html',
        weekdays=weekdays,
        client=client,
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
