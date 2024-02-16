import datetime
import csv
import os

from flask import Flask, render_template, request, session, redirect, send_file
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timetable.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'bruhbruh'
app.config['UPLOAD_FOLDER'] = 'static\\uploads'

db = SQLAlchemy(app)


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    short_name = db.Column(db.String(100), nullable=False)
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
    customer_name = db.Column(db.String(100))
    customer_phone = db.Column(db.String(100))
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
    floating = db.Column(db.Integer, nullable=False)
    busy = db.relationship('Busy', backref='flight_simulator', lazy=True)


@app.route("/")
def index():
    if session.get('id') == None:
        return redirect('/auth', 301)
    
    db.create_all()

    return redirect('/simulators_list', 301)


@app.route("/admin_auth/", methods=['GET', 'POST'])
def admin_auth():
    if session.get('id') != None:
        return redirect('/simulators_list', 301)

    db.create_all()

    message = ''
    if request.method == 'POST' and request.form.get('login'):
        login = request.form.get('login')
        password = request.form.get('password')

        if len(Company.query.all()) == 0:
            new_user = Company(login=login, name='Администратор', short_name='', document_id_hash=password, mail='', admin=1, approved=1)
            db.session.add(new_user)
            db.session.commit()
            message = 'Зарегистрирован аккаунт администратора'
        
        user = Company.query.filter(Company.document_id_hash == password).filter(Company.login == login).first()
        if user and user.approved == 0:
            message = 'Аккаунт ожидает подтверждения!'
        elif user:
            session['id'] = user.id
            return redirect('/simulators_list', 301)
        else:
            message = 'Неверный логин или пароль!'

    return render_template('admin_auth.html', message=message)


@app.route("/auth/", methods=['GET', 'POST'])
def auth():
    if session.get('id') != None:
        return redirect('/simulators_list', 301)

    db.create_all()

    message = ''
    if request.method == 'POST' and request.form.get('login'):
        login = request.form.get('login')
        password = request.form.get('password')
        
        user = Company.query.filter(Company.document_id_hash == password).filter(Company.id == login).first()
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
        schedule = request.args.get('schedule')

        simulators_count = FlightSimulator.query.filter(FlightSimulator.name == name).count()
        if simulators_count > 0:
            return {'error': True, 'response': 'Тренажер с таким именем уже существует'}

        new_simulator = FlightSimulator(name=name, caption=caption, auditory=auditory, floating=int(schedule))
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
    simulators = FlightSimulator.query.all()

    response = {}
    for simulator in simulators:
        simulator_dict = {
            'id': simulator.id,
            'name': simulator.name,
            'caption': simulator.caption,
            'auditory': simulator.auditory,
            'floating': simulator.floating
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


@app.route("/unauthorized_simulators_list/")
def unauthorized_simulators_list():
    db.create_all()

    return render_template('unauthorized_simulators_list.html')


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
        busy.customer_name = None
        busy.customer_phone = None

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
            'start_time': busy.start_time.strftime('%H:%M'),
            'end_time': busy.end_time.strftime('%H:%M'),
            'day': busy_day.strftime('%d.%m.%Y'),
            'company_name': company_name,
            'customer_name': busy.customer_name,
            'customer_phone': busy.customer_phone,
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
        if user.admin == 0:
            user_dictionary = {
                'id': user.id,
                'login': user.login,
                'mail': user.mail,
                'document_id_hash': user.document_id_hash,
                'name': user.name,
                'short_name': user.short_name,
                'approved': user.approved
            }
            response[user.id] = user_dictionary

    return response


@app.route("/send_user/")
def send_user():
    if session.get('id') == None:
        return redirect('/auth', 301)

    user = Company.query.filter(Company.id == session.get('id')).first()
    if user.admin == 0:
        return redirect('/', 301)

    action = request.args.get('action')

    if action == 'add':
        name = request.args.get('name')
        short_name = request.args.get('short_name')
        document_id = request.args.get('document_id')
        mail = request.args.get('mail')

        company_count = Company.query.filter(Company.name == name).count()
        if company_count > 0:
            return {'error': True, 'response': 'Компания с таким именем уже зарегистрирована'}

        new_company = Company(name=name, short_name=short_name, document_id_hash=document_id, login='login', mail=mail, admin=0, approved=1)
        db.session.add(new_company)
        db.session.commit()
    elif action == 'delete':
        company_id = request.args.get('user_id')

        company = Company.query.filter(Company.id == company_id).first()

        db.session.delete(company)
        db.session.commit()

    return {'error': False, 'response': 'Успешно изменено'}


@app.route("/admin_panel/")
def admin_panel():
    if session.get('id') == None:
        return redirect('/auth', 301)

    user = Company.query.filter(Company.id == session.get('id')).first()
    if user.admin == 0:
        return redirect('/', 301)

    company_name = Company.query.filter(Company.id == session.get('id')).first().name

    return render_template('admin_panel.html', company_name=company_name)


@app.route("/edit_company/<company_id>", methods=['GET', 'POST'])
def edit_company(company_id):
    if session.get('id') == None:
        return redirect('/auth', 301)

    user = Company.query.filter(Company.id == session.get('id')).first()
    if user.admin == 0:
        return redirect('/', 301)

    message = None

    if request.method == 'POST':
        user_company_name = request.form.get('company_name')
        user_short_company_name = request.form.get('short_company_name')
        user_mail = request.form.get('mail')
        user_password = request.form.get('password')

        company = Company.query.filter(Company.id == int(company_id)).first()

        company.name = user_company_name
        company.short_name = user_short_company_name
        company.mail = user_mail
        company.document_id_hash = user_password

        db.session.commit()

        message = 'Успешно изменено'

    company_name = Company.query.filter(Company.id == session.get('id')).first().name
    company = Company.query.filter(Company.id == int(company_id)).first()

    return render_template('edit_company.html',
                           company_name=company_name,
                           message=message,
                           company_id=company_id,
                           name=company.name,
                           short_name=company.short_name,
                           mail=company.mail,
                           document_id_hash=company.document_id_hash)


@app.route("/register_train/<simulator_id>")
def register_train(simulator_id):
    db.create_all()

    if session.get('id') == None:
        return redirect('/auth', 301)

    company = Company.query.filter(Company.id == session.get('id')).first()
    company_id = company.id
    company_name = company.name

    simulator = FlightSimulator.query.filter(FlightSimulator.id == int(simulator_id)).first()
    simulator_name = simulator.name
    simulator_floating = simulator.floating
    is_admin = Company.query.filter(Company.id == session.get('id')).first().admin

    return render_template('register_train.html', simulator_id=simulator_id, simulator_name=simulator_name, company_name=company_name, is_admin=is_admin, company_id=company_id, is_floating=simulator_floating)


@app.route("/unauthorized_timetable/<simulator_id>")
def unauthorized_timetable(simulator_id):
    db.create_all()

    simulator_name = FlightSimulator.query.filter(FlightSimulator.id == int(simulator_id)).first().name

    return render_template('unauthorized_timetable.html', simulator_id=simulator_id, simulator_name=simulator_name)


@app.route("/send_busies/")
def send_busies():
    if session.get('id') == None:
        return redirect('/auth', 301)

    user = Company.query.filter(Company.id == session.get('id')).first()
    if user.admin > 0:
        return {'error': True, 'response': 'Администратор не может зарегистрировать полет на себя'}

    simulator_id = request.args.get('simulator_id')
    simulator = FlightSimulator.query.filter(FlightSimulator.id == simulator_id).first()

    customer_name = request.args.get('name')
    customer_phone = request.args.get('phone')

    if simulator.floating == 0:
        busies_id = request.args.getlist('ids[]')
        for busy_id in busies_id:
            busy = Busy.query.filter(Busy.id == busy_id).first()

            if busy.company_id != None:
                return {'error': True, 'response': 'Выбранные слоты уже заняты'}

            busy.company_id = session.get('id')
            busy.approved = 0
            busy.customer_name = customer_name
            busy.customer_phone = customer_phone
    else:
        start_time = request.args.get('time_from')
        end_time = request.args.get('time_to')

        day_value = datetime.datetime.strptime(request.args.get('day'), '%d.%m.%Y').date()
        day_id = Day.query.filter(Day.date == day_value).first().id

        start_time = datetime.datetime.strptime(start_time, '%H:%M').time()
        end_time = datetime.datetime.strptime(end_time, '%H:%M').time()

        if start_time >= end_time:
            return {'error': True, 'response': 'Неправильно введено время'}

        if start_time < datetime.time(9, 0) or start_time > datetime.time(20, 0) or end_time < datetime.time(9, 0) or end_time > datetime.time(20, 0):
            return {'error': True, 'response': 'Тренажер работает с 9 до 20 часов'}

        last_busy_time = datetime.time(8, 50)
        busies = Busy.query.filter(Busy.day_id == day_id).filter(Busy.simulator_id == simulator_id).all()
        for busy in busies:
            last_busy_time = max(busy.end_time, last_busy_time)
        last_busy_datetime = datetime.datetime.combine(datetime.date.today(), last_busy_time) + datetime.timedelta(minutes=10)
        if start_time != last_busy_datetime.time():
            return {'error': True, 'response': 'Начало бронирования должно быть через 10 минут после последнего бронирования'}

        new_busy = Busy(start_time=start_time,
                        end_time=end_time,
                        day_id=day_id,
                        simulator_id=simulator_id,
                        approved=0,
                        company_id=session.get('id'),
                        customer_name=customer_name,
                        customer_phone=customer_phone)
        db.session.add(new_busy)
    db.session.commit()

    return {'error': False, 'response': 'Запрос отправлен'}


@app.route("/generate_csv/")
def generate_csv():
    month_value = int(request.args['month'])
    year_value = int(request.args['year'])
    simulator_id = int(request.args['simulator_id'])

    days = Day.query.filter(Day.date.between(f'{year_value}-{month_value:02}-01',
                                             f'{year_value}-{month_value:02}-31')).all()

    simulator = FlightSimulator.query.filter(FlightSimulator.id == simulator_id).first()

    csv_dir = "static\\csv"
    try:
        os.mkdir(csv_dir)
    except:
        pass
    csv_file = f"{simulator.name[:3]}_{month_value}_{year_value}.csv"
    csv_path = os.path.join(csv_dir, csv_file)

    with open(csv_path, 'w', newline='') as file:
        writer = csv.writer(file, dialect='excel', delimiter=';')

        table_header = [simulator.name]
        for i in range(len(days)):
            table_header.append(i)
        writer.writerow(table_header)

        rows = [
            ['00.10-04.10'],
            ['04.30-11.30'],
            ['11.40-15.40'],
            ['15.50-19.50'],
            ['20.00-00.00']
        ]

        for day in days:
            busies = Busy.query.filter(Busy.day_id == day.id).filter(Busy.simulator_id == simulator_id).all()

            if len(busies) > 0:
                for i in range(len(busies)):
                    if busies[i].company != None:
                        rows[i].append(busies[i].company.short_name)
                    else:
                        rows[i].append('')
            else:
                for i in range(5):
                    rows[i].append('')
        writer.writerows(rows)

    return send_file(csv_path, as_attachment=True, download_name=csv_file)


@app.route("/generate_csv_all/")
def generate_csv_all():
    csv_month = request.args['csv-month'].split('-')
    year_value = int(csv_month[0])
    month_value = int(csv_month[1])

    days = Day.query.filter(Day.date.between(f'{year_value}-{month_value:02}-01',
                                             f'{year_value}-{month_value:02}-31')).all()

    simulators = FlightSimulator.query.filter(FlightSimulator.floating == 0).all()

    csv_dir = "static\\csv"
    try:
        os.mkdir(csv_dir)
    except:
        pass

    csv_file = f"{month_value}_{year_value}.csv"
    csv_path = os.path.join(csv_dir, csv_file)

    with open(csv_path, 'w', newline='', encoding='ANSI') as file:
        for simulator in simulators:
            writer = csv.writer(file, dialect='excel', delimiter=';')

            table_header = [simulator.name]
            for i in range(len(days)):
                table_header.append(i + 1)
            writer.writerow(table_header)

            rows = [
                ['00.10-04.10'],
                ['04.30-11.30'],
                ['11.40-15.40'],
                ['15.50-19.50'],
                ['20.00-00.00']
            ]

            for day in days:
                busies = Busy.query.filter(Busy.day_id == day.id).filter(Busy.simulator_id == simulator.id).all()
                if len(busies) > 0:
                    for i in range(len(busies)):
                        if busies[i].company != None:
                            rows[i].append(busies[i].company.short_name)
                        else:
                            rows[i].append('')
                else:
                    for i in range(5):
                        rows[i].append('')
            writer.writerows(rows)

            writer.writerow([])

    return send_file(csv_path, as_attachment=True, download_name=csv_file)


@app.route("/delete_busy/")
def delete_busy():
    if session.get('id') == None:
        return redirect('/auth', 301)

    busy_id = request.args.get('id')

    busy = Busy.query.filter(Busy.id == busy_id).first()

    user = Company.query.filter(Company.id == session.get('id')).first()

    if user.admin == 0 and session.get('id') != busy.company_id:
        print(session.get('id'), busy_id)
        return {'error': True, 'response': 'Вы не можете отменить чужие слоты'}

    if busy.flight_simulator.floating == 0:
        busy.company_id = None
        busy.approved = 1
        busy.customer_name = None
        busy.customer_phone = None
    else:
        db.session.delete(busy)

    db.session.commit()

    return {'error': False, 'response': 'Успешно удалено'}


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
    simulator = FlightSimulator.query.filter(FlightSimulator.id == simulator_id).first()

    if len(busies) == 0 and simulator.floating == 0:
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
        company_id = -1
        self_booked = False
        if busy.company_id != None:
            user = Company.query.filter(Company.id == session.get('id')).first()
            if user != None and (user.id == busy.company_id or user.admin > 0):
                self_booked = True
                company_name = Company.query.filter(Company.id == busy.company_id).first().name
                company_id = Company.query.filter(Company.id == busy.company_id).first().id
            else:
                company_name = 'Забронированно'

        busy_dictionary = {
            'id': busy.id,
            'start_time': busy.start_time.strftime('%H:%M'),
            'end_time': busy.end_time.strftime('%H:%M'),
            'day_id': busy.day_id,
            'company_id': company_id,
            'company_name': company_name,
            'simulator_id': busy.simulator_id,
            'approved': busy.approved,
            'self_booked': self_booked
        }
        response[busy.id] = busy_dictionary

    return response


@app.route("/get_logins/")
def get_logins():
    users = Company.query.all()
    response = {}

    for user in users:
        if user.admin > 0:
            continue
        response[user.id] = {
            'id': user.id,
            'name': user.name
        }

    return response
