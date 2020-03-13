import json
import datetime
from random import sample
from flask import Flask, render_template, request
from data import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template(
        "index.html",
        goals=goals,
        teachers_random=teachers_random,
        teachers=teachers,
        year=year
    )

@app.route('/all')
def all():
    return render_template("all.html", goals=goals, teachers=teachers, year=year)

@app.route('/goal/<goal_name>/')
def goal(goal_name):
    teachers_goal = []
    for teacher in teachers:
        if goal_name in teacher['goals']:
            teachers_goal.append(teacher)
    return render_template(
        "goal.html",
        goals=goals,
        teachers_goal=teachers_goal,
        goal_name=goal_name,
        year=year
    )


@app.route('/profile/<int:uin>')
def profile(uin):
    work_week = {}
    days_week = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    num = 0
    for i in range(1):
        for day in teachers[uin]['free']:
            days_new = {x: True for x in teachers[uin]['free'][day].keys() if teachers[uin]['free'][day][x] == True}
            work_week[days_week[num]] = days_new
            num += 1
    return render_template(
        "profile.html",
        teachers=teachers,
        uin=uin,
        teachers_number=[1],
        goals=goals,
        weekdays=weekdays,
        work_week=work_week,
        year=year
    )


@app.route('/request')
def request_client():
    return render_template("request.html", year=year)


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
    with open("request.json", "w") as f:
        json.dump(request_client, f)
    return render_template(
        "request_done.html",
        goals_teachers=goals,
        goal=goal,
        time=time,
        client_name_request=client_name_request,
        client_phone_request=client_phone_request,
        year=year
    )


@app.route('/booking/<int:teacher_id>/<day>/<time>')
def booking(teacher_id, day, time):
    return render_template(
        "booking.html",
        teachers=teachers,
        teacher_id=teacher_id,
        weekdays=weekdays,
        day=day,
        time=time,
        year=year
    )


@app.route('/booking_done', methods=['POST'])
def booking_done():
    client_weekday = request.form.get("clientWeekday")
    client_time = request.form.get("clientTime")
    client_teacher = request.form.get("clientTeacher")
    client_name = request.form.get("clientName")
    client_phone = request.form.get("clientPhone")
    client = dict(weekday=client_weekday,
                  time=client_time,
                  teacher=int(client_teacher),
                  name=client_name,
                  phone=client_phone)
    with open("booking.json", "w") as f:
        json.dump(client, f)
    return render_template(
        "booking_done.html",
        weekdays=weekdays,
        client_time=client_time,
        client_teacher=client_teacher,
        client_weekday=client_weekday,
        client_name=client_name,
        client_phone=client_phone,
        year=year
    )

@app.errorhandler(500)
def render_server_error(error):
    return render_template(
        "500.html",
        goals=goals,
        year=year
    ), 500


@app.errorhandler(404)
def render_not_found(error):
    return render_template(
        "404.html",
        goals=goals,
        year=year
    ), 404


teachers_random = sample(teachers, 6)

year = datetime.datetime.now().year

if __name__ == '__main__':
    app.run()