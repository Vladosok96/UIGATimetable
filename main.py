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
    approved = db.Column(db.Integer, nullable=False)
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
    caption = db.Column(db.String(1024), nullable=False)
    auditory = db.Column(db.String(100), nullable=False)
    busy = db.relationship('Busy', backref='flight_simulator', lazy=True)


@app.route("/")
def index():
    if session.get('id') == None:
        return redirect('/auth', 301)
    
    db.create_all()

    return redirect('/simulators_list', 301)


@app.route("/register_user/", methods=['GET', 'POST'])
def user_registration():
    if session.get('id') != None:
        return redirect('/simulators_list', 301)

    message = ''
    if request.method == 'POST' and request.form.get('login'):
        login = request.form.get('login')
        password = request.form.get('password')
        company_name = request.form.get('company_name')
        mail = request.form.get('mail')

        user = Company.query.filter(Company.login == login).first()
        if user:
            message = "Компания с таким логином уже зарегистрирована или ожидает подтверждения!"
        else:
            new_user = Company(name=company_name, login=login, document_id_hash=password, mail=mail, admin=0, approved=0)
            message = 'Заявка отправлена'

            if len(Company.query.all()) == 0:
                new_user.admin = 1
                new_user.approved = 1
                message = 'Зарегистрирован аккаунт администратора'
            
            db.session.add(new_user)
            db.session.commit()

    return render_template('register_user.html', message=message)


@app.route("/auth/", methods=['GET', 'POST'])
def auth():
    if session.get('id') != None:
        return redirect('/simulators_list', 301)

    db.create_all()

    message = ''
    if request.method == 'POST' and request.form.get('login'):
        login = request.form.get('login')
        password = request.form.get('password')

        user = Company.query.filter(Company.document_id_hash == password).filter(Company.login == login).first()
        if user and user.approved == 0:
            message = 'Аккаунт ожидает подтверждения!'
        elif user:
            session['id'] = user.id
            return redirect('/simulators_list', 301)
        else:
            message = 'Неверный логин или пароль!'

    return render_template('auth.html', message=message)


@app.route('/logout/')
def logout():
    session.pop('id', None)
    return redirect('/auth')


@app.route('/send_simulator/')
def send_simulator():
    if session.get('id') == None:
        return redirect('/auth', 301)

    user = Company.query.filter(Company.id == session.get('id')).first()
    if user.admin == 0:
        return {'error': True, 'response': 'Недостаточно прав для данной операции'}

    action = request.args.get('action')

    if action == 'add':
        name = request.args.get('name')
        caption = request.args.get('caption')
        auditory = request.args.get('auditory')

        simulators_count = FlightSimulator.query.filter(FlightSimulator.name == name).count()
        if simulators_count > 0:
            return {'error': True, 'response': 'Тренажер с таким именем уже существует'}

        new_simulator = FlightSimulator(name=name, caption=caption, auditory=auditory)
        db.session.add(new_simulator)
        db.session.commit()

        return {'error': False, 'response': 'Успешно добавлено'}
    elif action == 'delete':
        simulator_id = int(request.args.get('simulator_id'))

        busies = Busy.query.filter(Busy.simulator_id == simulator_id).all()
        simulator = FlightSimulator.query.filter(FlightSimulator.id == simulator_id).first()

        for busy in busies:
            db.session.delete(busy)

        db.session.delete(simulator)
        db.session.commit()

        return {'error': False, 'response': 'Успешно удалено'}


@app.route("/get_simulators_list/")
def get_simulators_list():
    if session.get('id') == None:
        return redirect('/auth', 301)

    simulators = FlightSimulator.query.all()

    response = {}
    for simulator in simulators:
        simulator_dict = {
            'id': simulator.id,
            'name': simulator.name,
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

    company_name = Company.query.filter(Company.id == session.get('id')).first().name

    user = Company.query.filter(Company.id == session.get('id')).first()
    is_admin = False
    if user.admin > 0:
        is_admin = True

    return render_template('simulators_list.html', is_admin=is_admin, company_name=company_name)


@app.route("/send_approve/")
def send_approve():
    if session.get('id') == None:
        return redirect('/auth', 301)

    user = Company.query.filter(Company.id == session.get('id')).first()
    if user.admin == 0:
        return {'error': True, 'response': 'Недостаточно прав для данной операции'}

    busy_id = request.args.get('id')
    approved = int(request.args.get('approved'))

    busy = Busy.query.filter(Busy.id == busy_id).first()
    if approved == 1:
        busy.approved = 1
    else:
        busy.company_id = None
        busy.approved = 1

    db.session.commit()

    return {'error': False, 'response': 'Изменения сохранены'}


@app.route("/get_approval/")
def get_approval():
    if session.get('id') == None:
        return redirect('/auth', 301)

    user = Company.query.filter(Company.id == session.get('id')).first()
    if user.admin == 0:
        return {'error': True, 'response': 'Недостаточно прав для данной операции'}

    busies = Busy.query.filter(Busy.approved == 0).all()

    response = {}
    for busy in busies:
        company_name = ""
        if busy.company_id != None:
            company_name = Company.query.filter(Company.id == busy.company_id).first().name

        busy_day = Day.query.filter(Day.id == busy.day_id).first().date
        simulator_name = FlightSimulator.query.filter(FlightSimulator.id == busy.simulator_id).first().name

        busy_dictionary = {
            'id': busy.id,
            'start_time': busy.start_time.strftime('%H:%M:%S'),
            'end_time': busy.end_time.strftime('%H:%M:%S'),
            'day': busy_day.strftime('%d.%m.%Y'),
            'company_name': company_name,
            'simulator_name': simulator_name
        }
        response[busy.id] = busy_dictionary

    return response


@app.route("/send_user_approve/")
def send_user_approve():
    if session.get('id') == None:
        return redirect('/auth', 301)

    user = Company.query.filter(Company.id == session.get('id')).first()
    if user.admin == 0:
        return {'error': True, 'response': 'Недостаточно прав для данной операции'}

    user_id = request.args.get('id')
    approved = int(request.args.get('approved'))

    user = Company.query.filter(Company.id == user_id).first()
    if approved == 1:
        user.approved = 1
    else:
        db.session.delete(user)

    db.session.commit()

    return {'error': False, 'response': 'Изменения сохранены'}


@app.route("/get_user_approval/")
def get_user_approval():
    if session.get('id') == None:
        return redirect('/auth', 301)

    user = Company.query.filter(Company.id == session.get('id')).first()
    if user.admin == 0:
        return {'error': True, 'response': 'Недостаточно прав для данной операции'}

    users = Company.query.all()

    response = {}
    for user in users:
        user_dictionary = {
            'id': user.id,
            'login': user.login,
            'mail': user.mail,
            'document_id_hash': user.document_id_hash,
            'name': user.name,
            'approved': user.approved
        }
        response[user.id] = user_dictionary

    return response


@app.route("/admin_panel/")
def admin_panel():
    if session.get('id') == None:
        return redirect('/auth', 301)

    company_name = Company.query.filter(Company.id == session.get('id')).first().name

    user = Company.query.filter(Company.id == session.get('id')).first()
    if user.admin == 0:
        return redirect('/', 301)

    return render_template('admin_panel.html', company_name=company_name)


@app.route("/register_train/<simulator_id>")
def register_train(simulator_id):
    db.create_all()

    if session.get('id') == None:
        return redirect('/auth', 301)

    company_name = Company.query.filter(Company.id == session.get('id')).first().name

    simulator_name = FlightSimulator.query.filter(FlightSimulator.id == int(simulator_id)).first().name
    is_admin = Company.query.filter(Company.id == session.get('id')).first().admin

    return render_template('register_train.html', simulator_id=simulator_id, simulator_name=simulator_name, company_name=company_name, is_admin=is_admin)


@app.route("/send_busies_list/")
def send_busies_list():
    if session.get('id') == None:
        return redirect('/auth', 301)

    user = Company.query.filter(Company.id == session.get('id')).first()
    if user.admin > 0:
        return {'error': True, 'response': 'Администратор не может зарегистрировать полет на себя'}

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


@app.route("/send_admin_busies_list/")
def send_admin_busies_list():
    if session.get('id') == None:
        return redirect('/auth', 301)

    user = Company.query.filter(Company.id == session.get('id')).first()
    if user.admin == 0:
        return {'error': True, 'response': 'Недостаточно прав для данной операции'}

    action = request.args.get('action')

    if action == 'delete':
        busy_id = request.args.get('id')

        busy = Busy.query.filter(Busy.id == busy_id).first()
        busy.company_id = None
        busy.approved = 1

    db.session.commit()

    return {'error': False, 'response': 'Запрос отправлен'}


@app.route("/month/")
def month():
    if session.get('id') == None:
        return redirect('/auth', 301)

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
    if session.get('id') == None:
        return redirect('/auth', 301)

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
