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


class Day(db.Model):
    __tablename__ = 'days'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    vocation = db.Column(db.Boolean, nullable=False)
    busy = db.relationship('Busy', backref='day', lazy=True)


@app.route("/")
def index():
    db.create_all()

    return render_template('index.html')


@app.route("/month/")
def month():
    month_value = int(request.args['month'])
    year_value = int(request.args['year'])

    days = Day.query.filter(Day.date.between(f'{year_value}-{month_value}-01',
                                             f'{year_value}-{month_value}-31')).all()

    if len(days) == 0:
        for i in range(1, 32):
            try:
                date = datetime.date(year_value, month_value, i)
                new_day = Day(date=date, vocation=False)
                db.session.add(new_day)
            except:
                break
        db.session.commit()

    for day in days:
        print(day.date)

    return 'ok'
