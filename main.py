import datetime

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timetable.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    document_id = db.Column(db.String(100), nullable=False)
    busy = db.relationship('Busy', backref='company', lazy=True)


class Busy(db.Model):
    __tablename__ = 'busies'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    day_id = db.Column(db.Integer, db.ForeignKey('days.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    simulator_id = db.Column(db.Integer, db.ForeignKey('flight_simulators.id'))


class Day(db.Model):
    __tablename__ = 'days'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    vocation = db.Column(db.Boolean, nullable=False)
    busy = db.relationship('Busy', backref='day', lazy=True)


class FlightSimulator(db.Model):
    __tablename__ = 'flight_simulators'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    english_name = db.Column(db.String(100), nullable=False)
    caption = db.Column(db.String(1024), nullable=False)
    auditory = db.Column(db.String(100), nullable=False)
    busy = db.relationship('Busy', backref='flight_simulator', lazy=True)


@app.route("/get_simulators_list/")
def get_simulators_list():
    simulators = FlightSimulator.query.all()

    response = {}
    for simulator in simulators:
        simulator_dict = {
            'id': simulator.id,
            'name': simulator.name,
            'english_name': simulator.english_name,
            'caption': simulator.caption,
            'auditory': simulator.auditory
        }
        response[simulator.id] = simulator_dict

    return response


@app.route("/simulators_list/")
def simulators_list():
    db.create_all()

    return render_template('simulators_list.html')


@app.route("/register_train/<simulator_id>")
def register_train(simulator_id):
    db.create_all()
    return render_template('register_train.html', simulator_id=simulator_id)


@app.route("/month/")
def month():
    month_value = int(request.args['month'])
    year_value = int(request.args['year'])
    simulator_id = int(request.args['simulator_id'])

    days = Day.query.filter(Day.date.between(f'{year_value}-{month_value:02}-01',
                                             f'{year_value}-{month_value:02}-31')).all()

    if len(days) == 0:
        for i in range(1, 32):
            try:
                date = datetime.date(year_value, month_value, i)
                new_day = Day(date=date, vocation=False)
                db.session.add(new_day)
                days.append(new_day)
            except:
                break
        db.session.commit()

    days = Day.query.filter(Day.date.between(f'{year_value}-{month_value:02}-01',
                                             f'{year_value}-{month_value:02}-31')).all()

    response = {}

    for day in days:
        day_dictionary = {
            'date': day.date.strftime('%d.%m.%Y'),
            'vocation': day.vocation,
            'busies': {}}
        busies = Busy.query.filter(Busy.day_id == day.id).filter(Busy.simulator_id == simulator_id).all()
        for busy in busies:
            busy_dictionary = {
                'company_name': Company.query.filter(Company.id == busy.company_id).first().name,
                'start_time': busy.start_time.strftime('%H:%M:%S'),
                'end_time': busy.end_time.strftime('%H:%M:%S')}
            day_dictionary['busies'][busy.id] = busy_dictionary
        response[day.date.day] = day_dictionary
    return response


app.run()
