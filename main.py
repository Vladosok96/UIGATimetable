import datetime

from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timetable.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'bruhbruh'

db = SQLAlchemy(app)


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    document_id_hash = db.Column(db.String(200), nullable=False)
    mail = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.Integer, nullable=False)
    busy = db.relationship('Busy', backref='company', lazy=True)


class Busy(db.Model):
    __tablename__ = 'busies'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    approved = db.Column(db.Integer, nullable=False)
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


@app.route("/")
def index():
    if session.get('id') == None:
        return redirect('/auth', 301)
    return redirect('/simulators_list', 301)


@app.route("/register/")
def register():
    return ''


@app.route("/auth/", methods=['GET', 'POST'])
def auth():
    if session.get('id') != None:
        return redirect('/simulators_list', 301)

    message = ''
    if request.method == 'POST' and request.form.get('login'):
        login = request.form.get('login')
        password = request.form.get('password')

        user = Company.query.filter(Company.document_id_hash == password and Company.login == login).first()
        if user:
            session['id'] = user.id
            return redirect('/simulators_list', 301)
        else:
            message = "Неверный логин или пароль!"

    return render_template('auth.html', message=message)


@app.route('/logout/')
def logout():
    session.pop('id', None)
    return redirect('/login')


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

    if session.get('id') == None:
        return redirect('/auth', 301)

    return render_template('simulators_list.html')


@app.route("/register_train/<simulator_id>")
def register_train(simulator_id):
    db.create_all()

    simulator_name = FlightSimulator.query.filter(FlightSimulator.id == int(simulator_id)).first().name

    return render_template('register_train.html', simulator_id=simulator_id, simulator_name=simulator_name)


@app.route("/send_busies_list/")
def send_busies_list():
    if session.get('id') == None:
        return redirect('/auth', 301)

    ids = request.args
    busies_id = []
    for checkbox in ids:
        if ids[checkbox] == 'on':
            try:
                busy_id = int(checkbox)
                busies_id.append(busy_id)
            except:
                pass

    for busy_id in busies_id:
        busy = Busy.query.filter(Busy.id == busy_id).first()

        if busy.company_id != None:
            return {'error': True, 'response': 'Выбранные слоты уже заняты'}

        busy.company_id = session.get('id')
        busy.approved = 0
    db.session.commit()

    return {'error': False, 'response': 'Запрос отправлен'}


@app.route("/month/")
def month():
    month_value = int(request.args['month'])
    year_value = int(request.args['year'])

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
        }
        response[day.date.day] = day_dictionary
    return response


@app.route("/day/")
def day():
    day_value = datetime.datetime.strptime(request.args['day'], '%d.%m.%Y').date()
    simulator_id = int(request.args['simulator_id'])

    day_id = Day.query.filter(Day.date == day_value).first().id
    busies = Busy.query.filter(Busy.day_id == day_id).filter(Busy.simulator_id == simulator_id).all()

    if len(busies) == 0:
        slots = [
            (datetime.time(0, 10), datetime.time(4, 10)),
            (datetime.time(7, 30), datetime.time(11, 30)),
            (datetime.time(11, 40), datetime.time(15, 40)),
            (datetime.time(15, 50), datetime.time(19, 50)),
            (datetime.time(20, 0), datetime.time(0, 0))
        ]
        for slot in slots:
            new_busy = Busy(start_time=slot[0],
                            end_time=slot[1],
                            day_id=day_id,
                            simulator_id=simulator_id,
                            approved=1)
            db.session.add(new_busy)
        db.session.commit()

    busies = Busy.query.filter(Busy.day_id == day_id).filter(Busy.simulator_id == simulator_id).all()

    response = {}
    for busy in busies:
        company_name = ""
        if busy.company_id != None:
            company_name = Company.query.filter(Company.id == busy.company_id).first().name

        busy_dictionary = {
            'id': busy.id,
            'start_time': busy.start_time.strftime('%H:%M:%S'),
            'end_time': busy.end_time.strftime('%H:%M:%S'),
            'day_id': busy.day_id,
            'company_name': company_name,
            'simulator_id': busy.simulator_id,
            'approved': busy.approved
        }
        response[busy.id] = busy_dictionary

    return response


app.run(debug=True)
