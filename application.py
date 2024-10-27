from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from flask_migrate import Migrate
import sqlite3
from datetime import datetime, timedelta, timezone
import os
import base64
import pdfkit


#Initializing the extension flask_sqlalchemy
class Base(DeclarativeBase):
    '''
    The base model class. When inherited it
    converts the camel-class type to a snake-class type witch 
    will be the name of the table in the database
    '''
    pass
#db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MY13424_SECRET23342_KEY_In_this_app_till_now_for_no000one-descovery'
#Configure the database:
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///csm_salon_and_barber_data.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://u3pdcv7rl74tkl:p85a1d0a972a27687149b85638b2374121480a33ead9d37e1065c94c276cc30a1@cat670aihdrkt1.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d6dbar3069o937'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#Initialize the app with rhe sql_alchemy extension:
#db.init_app(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
#Set duration of the users sessions
app.permanent_session_lifetime = timedelta(weeks=4)

#Database without using flask_sqlalchemy
#db = sqlite3.connect('csm_barber_data.db', check_same_thread=False)
#cursor = db.cursor()


################## Models classes #######################:
class Users(db.Model):
    '''
    It's creating the table users in database
    '''

    utc_plus_2 = datetime.utcnow() + timedelta(hours=2)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(150))
    telefone = db.Column(db.String(150), nullable=False, unique=True)
    senha = db.Column(db.String(150), nullable=False)
    data_registro = db.Column(db.DateTime, default=utc_plus_2)
    schedules = db.relationship('Schedules', backref='users')

class Establishments(db.Model):
    __tablename__ = 'establishments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False)
    apelido = db.Column(db.String(150), nullable=False, unique=True)
    msg_boas_vindas = db.Column(db.String(500))
    msg_secundaria = db.Column(db.String(1000))
    #logotipo = db.Column(db.String(500))
    horas_aberto = db.Column(db.String(50))
    horas_fechado = db.Column(db.String(50))
    dias_funcionamento = db.Column(db.String(150))
    descricao_do_bairro = db.Column(db.String(300))
    bairro = db.Column(db.String(100))
    provincia = db.Column(db.String(100))
    distrito = db.Column(db.String(100))
    telefone = db.Column(db.String(100))
    email = db.Column(db.String(150))
    agendas = db.relationship('Schedules', backref='establishments')
    servicos = db.relationship('Services', backref='establishments')
    funcionarios = db.relationship('Employers', backref='establishments')
    administrador = db.relationship('Admins', backref='establishments')
    imagens = db.relationship('Establishments_images', backref='establishments')

class Establishments_images(db.Model):
    #The place column can have 'hero, logo' values to help positioning in the correct place
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lugar = db.Column(db.Text, nullable=False)
    estabelecimento_id = db.Column(db.Integer, db.ForeignKey('establishments.id'))
    buffer_data = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimeType = db.Column(db.Text)

class Schedules(db.Model):
    '''
    It's creating the table schedules in database
    '''
    utc_plus_2 = datetime.utcnow() + timedelta(hours=2)
    utc_plus_2_str = utc_plus_2.strftime('%H:%M:%S')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    estabelecimento_id = db.Column(db.Integer, db.ForeignKey('establishments.id'))
    servico = db.Column(db.String(150), nullable=False)
    data = db.Column(db.String(150), nullable=False)
    hora = db.Column(db.String(150), nullable=False)
    processado = db.Column(db.String(10), default=utc_plus_2_str)
    estado = db.Column(db.String(100), default='-')
    messagem = db.Column(db.Text())

class Employers(db.Model):
    '''
    It's creating the table schedules in database
    '''
    utc_plus_2 = datetime.utcnow() + timedelta(hours=2)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(150))
    telefone = db.Column(db.String(150), unique=False)
    email = db.Column(db.String(150))
    senha = db.Column(db.String(150))
    tipo_documento = db.Column(db.String(150))
    numero_documento = db.Column(db.String(150))
    data_nascimento = db.Column(db.String(150))
    local_nascimento = db.Column(db.String(150))
    funcao = db.Column(db.String(150))
    contrato = db.Column(db.String(150))
    data_entrada = db.Column(db.DateTime, default=utc_plus_2)
    estabelecimento_id = db.Column(db.Integer, db.ForeignKey('establishments.id'))

class Admins(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False)
    telefone = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150))
    senha = db.Column(db.String(150), nullable=False)
    privilegios = db.Column(db.String(150))
    estabelecimento_id = db.Column(db.Integer, db.ForeignKey('establishments.id'))

class Services(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    servico = db.Column(db.String, nullable=False)
    preco = db.Column(db.String(150))
    estabelecimento_id = db.Column(db.Integer, db.ForeignKey('establishments.id'))

################## End Models classes #######################:

@app.route("/")
def index():
    if 'user_phone' in session:
        phone = session['user_phone']
        #cursor.execute("SELECT nome FROM users WHERE email == ?", [email])
        full_name = db.session.execute(db.select(Users.nome).filter_by(telefone=phone)).scalar_one()

        #full_name = cursor.fetchone()[0]
        first_name = full_name.split(' ')[0]
        #print(full_name)
        #print(first_name)
        #askin if the user is loged in to show his name

        return render_template("index.html", user= first_name, logout='sair', suas_agendas = 'Minhas Agendas')
    return render_template("index.html", user='Entrar')
    

@app.route("/cadastro", methods=['GET', 'POST'])
def signup():

    
    if request.method == 'POST':
        name = request.form.get('name')
        #email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        password_confirmation = request.form.get('password_confirmation')
        
        #cursor.execute("SELECT email, telefone FROM users")
        phones = db.session.execute(db.select(Users.nome, Users.telefone)).all()
        #emails = cursor.fetchall()

        for i in phones:
            if i[1] == phone:
                flash("Existe essa conta com o mesmo número. Use outro número de telefone!")
                return render_template('signup.html')
            '''
            elif i[1]== phone:
                flash("Existe essa conta com o mesmo número. Use outro número de telefone")
                return render_template('signup.html')
                '''

        if not name or not phone or not password:
            flash("Por favor, preencha todos os campos!")
            return render_template('signup.html')
        
        elif not phone:
            flash("Por favor, preencha o campo de 'telefone'!")
            return render_template('signup.html')
        
        elif not password:
            flash("Por favor, preencha o campo 'crie uma senha'!")
            return render_template('signup.html')

        elif  password != password_confirmation:
            flash("As senhas devem ser iguais!")
            return render_template('signup.html')    
        
        else:
            #Everything was okay and we can sava the info
            #Treating the name from the bad user spacing after the name and capitizing every part of name
            splited = name.split(' ')
            treated_name = ''

            
            if len(splited) > 1:
                #capitilizing each part of name ('firs ... last name') in splited
                for i in range(len(splited)-1):
                    treated_name = treated_name + splited[i].capitalize() + ' ' + splited[i+1].capitalize()

                #cursor.execute("INSERT INTO users (nome, email, telefone, senha) VALUES (?, ?, ?, ?)", (treated_name, email, phone, password))
                #db.commit()
                user = Users(
                    nome = name,
                    telefone = phone,
                    senha = password
                )
                db.session.add(user)
                db.session.commit()

                session['user_phone'] = phone
                session.permanent = True

                if 'schedule_details' in session:
                    #Asking if the user doesn't coming from scheduling --> login pages
                    #
    
                    schedule_details = session['schedule_details']
                    #Retrieving the schedule saved in the session from the schedule page

                    user_id = db.session.execute(db.select(Users.id).filter_by(telefone=phone)).scalar_one()
                        
                    schedule = Schedules(
                        servico = schedule_details['service'],
                        data = schedule_details['date'],
                        hora = schedule_details['time'],
                        estabelecimento_id = schedule_details['establishment_id'],
                        user_id = user_id
                    )
                    db.session.add(schedule)
                    db.session.commit()

                    #Remove the shedule info in the session
                    session.pop('schedule_details', None)
                    return redirect(url_for('schedules'))
                    
                return redirect(url_for('index'))
            
            #Inserting in to database the data if if the user gives only the first name
            name = name.capitalize()
            #cursor.execute("INSERT INTO users (nome, email, telefone, senha) VALUES (?, ?, ?, ?)", (name, email, phone, password))
            #db.commit()
            user = Users(
                nome = name,
                telefone = phone,
                senha = password
            )
            db.session.add(user)
            db.session.commit()

            #saving the email and name on session
            session['user_phone'] = phone
            session.permanent = True

            if 'schedule_details' in session:
                    #Asking if the user doesn't coming from scheduling --> login pages
                    #
    
                    schedule_details = session['schedule_details']
                    #Retrieving the schedule saved in the session from the schedule page

                    user_id = db.session.execute(db.select(Users.id).filter_by(telefone=phone)).scalar_one()
                        
                    schedule = Schedules(
                        servico = schedule_details['service'],
                        data = schedule_details['date'],
                        hora = schedule_details['time'],
                        estabelecimento_id = schedule_details['establishment_id'],
                        user_id = user_id
                    )
                    db.session.add(schedule)
                    db.session.commit()

                    #Remove the shedule info in the session
                    session.pop('schedule_details', None)
                    return redirect(url_for('schedules'))

            return redirect(url_for('index'))
        
    else:
        #if request.method == 'get'

        if 'schedule_details' in session:
            #if available a schedule saved in the session, write a message in the form
            flash('Você está quase terminando, Crie uma conta para salvar a sua agenda!')
        return render_template("signup.html")

@app.route("/login", methods=['GET', 'POST'])
def login():

    #Checking if we have a session of the user
    #we are askin if we have the key: user_name in session
    #if true, it's not necessary tu put login info
    if 'user_phone' in session:
        phone = session['user_phone']
        full_name = db.session.execute(db.select(Users.nome).filter_by(telefone=phone)).scalar_one()

        #full_name = cursor.fetchone()[0]
        first_name = full_name.split(' ')[0]
        #print(full_name)
        #print(first_name)
        #askin if the user is loged in to show his name

        return redirect(url_for("index"))
    
    elif request.method == 'POST':
        phone = request.form.get("phone")
        password = request.form.get("password")
        
        #cursor.execute("SELECT email, senha FROM users WHERE email == ? AND senha == ?", (email, password))
        #data = cursor.fetchall()
        data = db.session.execute(db.select(Users.telefone, Users.senha).filter_by(telefone=phone, senha=password)).all()
        #print(data[0])

        
        if phone and password:
            for i in data:
                if (i[0], i[1]) == (phone, password):
                    #we verify if the given email and password is registered in database'

                    #we save the user session for future auto login
                    session['user_phone'] = phone
                    session.permanent = True


                    user_id = db.session.execute(db.select(Users.id).filter_by(telefone=phone)).scalar_one()
                    
                    if 'schedule_details' in  session:
                        #we check if there has a schedule saved in the session
                        # if true, then it means that the user comes from sheduling page and he isn't logged in

                        schedule_details = session['schedule_details']
                        #Retrieving the schedule saved in the session from the schedule page
                        
                        schedule = Schedules(
                            servico = schedule_details['service'],
                            data = schedule_details['date'],
                            hora = schedule_details['time'],
                            estabelecimento_id = schedule_details['establishment_id'],
                            user_id = user_id
                        )
                        db.session.add(schedule)
                        db.session.commit()

                        #Remove the shedule info in the session
                        session.pop('schedule_details', None)
                        return redirect(url_for('schedules'))
                    
                    elif request.args.get('ask_login_from'):
                        #User clicked on login button from a specific establishment page
                        establishment_alias = request.args.get('ask_login_from')
                        return redirect(url_for('establishment_page', establishment_alias=establishment_alias))

                    # it means the user clicked the login button from the index page or via url direct
                    return redirect(url_for("index"))

        elif not phone or not password:
            flash("Por favor, preencha todos os campos!")
            return render_template("login.html")
        
        
        flash('Senha ou número de telefone inválido!')
        return render_template('login.html')
        
    else:
        #executed if request.method == get

        if 'schedule_details' in session:
            flash('Você está quase terminando, inicie sessão para salvar a sua agenda!')
            
        return render_template("login.html")

#------------------ Establishment Registration: ----------------------------# 
@app.route("/registro-de-estabelecimento", methods=['GET', 'POST'])
def register_establishment():

    
    if request.method == 'POST':
        establishment_name = request.form.get('Establishment_name')
        alias = request.form.get('alias')
        welcome_msg = request.form.get('welcome_msg')
        open_hour = request.form.get('open_hour')
        close_hour = request.form.get('close_hour')
        open_days = request.form.get('open_days')
        burgh = request.form.get('burgh')
        burgh_description = request.form.get('burgh_description')
        province = request.form.get('province')
        district = request.form.get('district')
        phone = request.form.get('phone')
        #email = request.form.get('email')



        #alias = request.files['alias']
        
        #cursor.execute("SELECT email, telefone FROM users")
        aliases = db.session.execute(db.select(Establishments.apelido,)).all()
        #emails = cursor.fetchall()

        for i in aliases:
            if i[0] == alias:
                flash("Existe estabelecimento com mesmo apelido. Tente outro apelido!")
                return redirect(url_for('register_establishment'))

        if not establishment_name or not alias:
            flash("Por favor, preencha o nome e apelido!")
            return render_template('establishment_registration.html')  
        
        else:
            # if everything okay, we save the new establishment info into a dictionary
            transfer_data = {
                'new_establishment_alias': alias,
                'new_establishment_name': establishment_name,
                'welcome_msg': welcome_msg,
                'open_hour': open_hour,
                'close_hour': close_hour,
                'open_days': open_days,
                'burgh': burgh,
                'burgh_description': burgh_description,
                'province': province,
                'district': district,
                'phone': phone
            }
            # transfer_data contain the information of the new establishment to be saved after providing other 
            # informations like 'admin info' in the other page

            session['new_establishment_data'] = transfer_data
            return render_template('admin_signup.html', transfer_data = transfer_data)
        
    else:
        #if request.method == 'get'
        return render_template("establishment_registration.html")
#------------End Establishment Registration -----------------------#
@app.route("/sucessfully", methods=['get', 'post'])
def new_establishment_sucessfully():
    if request.method == "POST":
        #it's the main entrance method

        # gathering the admin info from the admin_signup.html template embeded form
        admin_name = request.form.get('name')
        #admin_email = request.form.get('email')
        admin_phone = request.form.get('phone')
        admin_password = request.form.get('password')

        # Check admin in database
        try:
            existing_admin = db.session.execute(db.select(Admins.telefone).filter_by(telefone=admin_phone)).scalar_one()

            if admin_phone == existing_admin:
                flash('Existe esse administrador com o mesmo número de telefone. Tente com outro número!')
                return render_template('admin_signup.html')
        except:
            pass
        

        ############Saving all colected data to establishments and Admins tables:##########

        # first, saving about establishment
        new_establishment_data = session['new_establishment_data'] # Retrieving the info saved in the register_establishment page

        establishment = Establishments(
            nome = new_establishment_data['new_establishment_name'],
            apelido = new_establishment_data['new_establishment_alias'],
            msg_boas_vindas = new_establishment_data['welcome_msg'],
            horas_aberto = new_establishment_data['open_hour'],
            horas_fechado = new_establishment_data['close_hour'],
            dias_funcionamento = new_establishment_data['open_days'],
            bairro = new_establishment_data['burgh'],
            descricao_do_bairro = new_establishment_data['burgh_description'],
            provincia = new_establishment_data['province'],
            distrito = new_establishment_data['district'],
            telefone = new_establishment_data['phone']
            
        )
        session.pop('new_establishment_data', None)
        db.session.add(establishment)
        db.session.commit()

        # Second, saving about the admin info:
        establishment_id = db.session.execute(db.select(Establishments.id).filter_by(apelido=new_establishment_data['new_establishment_alias'])).scalar_one()
        new_admin = Admins(
            nome = admin_name,
            telefone = admin_phone,
            senha = admin_password,
            estabelecimento_id = establishment_id
        )

        db.session.add(new_admin)
        db.session.commit()

        admin_and_establishment_data = {
            'alias': new_establishment_data['new_establishment_alias'],
            'phone': admin_phone,
            'password': admin_password
        }
        return render_template('sucessfully_establishment_subscribed.html', data=admin_and_establishment_data)
    
    return 'Em desenvolvimento'

@app.route("/terminar_seccao")
def logout():
    if 'user_phone' in session:
        session.pop('user_phone', None)
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))
    
    
    
@app.route('/<establishment_alias>/agendamento', methods=['get', 'post'])
def scheduling(establishment_alias):
    establishment_alias=establishment_alias

    #We are treating potencial error caused by user injecting a inexistent establisment alias
    try:
        establishment_alias_in_db = db.session.execute(db.select(Establishments.apelido).filter_by(apelido=establishment_alias)).scalar_one()
        if establishment_alias_in_db:
            pass
    except:
        return redirect(url_for('index'))
    
    establishment_id = db.session.execute(db.select(Establishments.id).filter_by(apelido=establishment_alias)).scalar_one()

    #Bellow we set a tuples list to pass in frontend template
    #the tuples take a servive id, service name an the service price respectively
    '''
    services = [('1', 'Trançar mexas/cabelo', '250-300,00MT'),
                ('2', 'Escovinha/carreca...','30,00MT'),
                ('3', 'Corte francês/similar', '50,00MT'),
                ('id_wash_hair', 'Lavagem de cabelo', '100,00MT'),
                ('id_feed_hair', 'Alimentação de cabelo', '30,00MT'),
                ('id_retouch', 'Retocagem de cabelo', '250,00MT'),
                ('id_paint_hair', 'Pintar cabelo', '50,00MT'),
                ('id_diamante_pack', 'Look Elite', '810,00MT'),
                ('id_other', 'Explico no atendimento')]
    '''
    services = db.session.execute(db.select(Services.id, Services.servico, Services.preco).filter_by(estabelecimento_id=establishment_id)).all()
    
    time_list = [
        '07:00',
        '07:30',
        '08:00',
        '08:30',
        '09:00',
        '09:30',
        '10:00',
        '10:30',
        '11:00',
        '11:30',
        '12:00',
        '12:30',
        '13:00',
        '13:30',
        '14:00',
        '14:30',
        '15:00',
        '15:30',
        '16:00',
        '16:30',
        '17:00',
        '17:30',
        '18:00',
        '18:30',
        '19:00',
        '19:30'
    ]
    
    
    if request.method == 'POST':
        #gathering scheduling info
        service = request.form.get('service')
        date = request.form.get('date')
        time = request.form.get('time')


        #-------- checking availabity of the date and time that the user selected --------#
        scheduled = db.session.execute(db.select(Schedules.data, Schedules.hora).filter_by(estabelecimento_id=establishment_id, data=date, hora=time)).all()
        if date and time:
            for i in scheduled:
                if (i[0], i[1]) == (date, time):
                    flash('Horario ocupado! Tente outro horario')
                    return redirect(url_for('scheduling', establishment_alias=establishment_alias))


        if not service or not date or not time:
            flash('Você deve preencher todos os campos.')
            return redirect(url_for('scheduling', establishment_alias=establishment_alias))

        
        else:
            # Here was scheduled sucessfully
            
            #cursor.execute("INSERT INTO schedules (user_id, servico, data, hora) VALUES (?, ?, ?, ?)", (id, service, date, time))
            #db.commit()

            if 'user_phone' not in session:
            #it checks if the user has loged in
                data = {
                'service': service,
                'date': date,
                'time': time,
                'establishment_id': establishment_id,
                'establishment_alias': establishment_alias
                }
                #Saving the schedule info in the session to avoid losing during the signin or signup process
                #After user log in or sigup, the schedule is retrieved from session in the login page
                session['schedule_details'] = data
                return redirect(url_for("login"))
            
            #here theuse is lgged in
            phone_in_session = session['user_phone']
            #we're a taking the email from session to make a query asking name with it in our db

            #cursor.execute("SELECT id FROM users WHERE email == ?", [email_in_session])
            # Once you only gave the function (cursor.execute) a string, the string is being interpreted as list of characters.
            #id = cursor.fetchone()[0] #we gave [0] because it returns (n,) and we want n

            #Getting the ids of the user (based on his/her phone nr) and establisment id (based on its alias)
            #But we got the establishment id above (under function definition). in this case we comment the line of establishment_id 
            user_id = db.session.execute(db.select(Users.id).filter_by(telefone=phone_in_session)).scalar_one()
            #establishment_id = db.session.execute(db.select(Establishments.id).filter_by(apelido=establishment_alias)).scalar_one()

            schedule = Schedules(
                user_id = user_id,
                estabelecimento_id = establishment_id,
                servico = service,
                data = date,
                hora = time
            )
            db.session.add(schedule)
            db.session.commit()
            return redirect(url_for('schedules'))
        

    else:
        #executed if method==get


        #---------------Working with the time and date------------------------#

        time_now_in_the_machine = datetime.now()
        diference_time = timedelta(hours=2)
        #We are geting the difernce betwen UTC and the time zon we are creating
        #It give us the diference of 2h ahead the utc

        utc2 = timezone(diference_time)
        #Return UTC+02:00

        #Now we have to convert the machine time to the gmt+2 time (UTC+02:00)
        mozambican_date_time = time_now_in_the_machine.astimezone(utc2)

        #formating the date and time for the quite familiar
        minimum_date = mozambican_date_time.strftime('%Y-%m-%d')

        #Maximum date:
        stringdate_to_datetime_object = datetime.strptime(minimum_date, "%Y-%m-%d")
        #Converting the string date to daterime object.
        #strptime(string, format)

        maximum_date_not_formated = stringdate_to_datetime_object + timedelta(days=31)
        #We are forecasting the the future date from the actual date plus 31 days

        maximum_date = maximum_date_not_formated.strftime("%Y-%m-%d")


        curent_time_plus_10m = mozambican_date_time + timedelta(minutes=10)
        #We are adding 10 minutes to the current time for being the minimum time to make a schedule
        
        static_max_time = datetime(2024, 8, 4, 19, 30)
        static_max_time_str = static_max_time.strftime('%H:%M')
        static_max_time_obj = datetime.strptime(static_max_time_str, "%H:%M")
        #Above we were generating a static max hour

        static_min_hour = datetime(2024, 8, 4, 7, 0)
        static_min_hour_str = static_min_hour.strftime('%H:%M')
        static_min_hour_obj = datetime.strptime(static_min_hour_str, '%H:%M')
        
        

        curent_time_plus_10m_str = curent_time_plus_10m.strftime("%H:%M")
        curent_time_plus_10m_obj = datetime.strptime(curent_time_plus_10m_str, '%H:%M')
        
        static_minutes = datetime(2024, 8, 4, 19, 30)
        static_minutes_str = static_minutes.strftime('%M')
        static_minutes_obj = datetime.strptime(static_minutes_str, "%M")
        #Above we were generating a static minutes to be ou reference (30 in 30 minutes)
        
        curent_time = mozambican_date_time.strftime('%H:%M')
        curent_time_obj = datetime.strptime(curent_time, '%H:%M')

        curent_time_without_minutes_str = mozambican_date_time.strftime('%H')
        curent_time_without_minutes_obj = datetime.strptime(curent_time_without_minutes_str, '%H')

        current_minutes_str = mozambican_date_time.strftime('%M')
        current_minutes_obj = datetime.strptime(current_minutes_str, '%M')

        #------------End working with the time and date-------------------#
        if curent_time_obj > static_max_time_obj or curent_time_obj < static_min_hour_obj:
            closed_flag = True
            return render_template('scheduling.html', establishment_alias=establishment_alias, services = services, minimum_date = minimum_date, maximum_date = maximum_date, min_max_time=[static_min_hour_str, static_max_time_str], time_list=time_list, closed_flag = closed_flag)
        
        elif curent_time_plus_10m_obj <= static_max_time_obj:
            #It means tha the salon is not closed
            #And the user has 10 minutes to arrive in the salon
            open_flag = True
            if (current_minutes_obj + timedelta(minutes=5)) >= static_minutes_obj:
                #It means that the next available hour will be H:00min
                
                minimum_time = curent_time_without_minutes_obj + timedelta(minutes=60)
                minimum_time = minimum_time.strftime('%H:%M')
                
                return render_template('scheduling.html', establishment_alias=establishment_alias, services = services, minimum_date = minimum_date, maximum_date = maximum_date, min_max_time=[minimum_time, static_max_time_str], time_list=time_list, open_flag=open_flag)
            
            else:
                #It means the next time will be H:30min
                minimum_time = curent_time_without_minutes_obj + timedelta(minutes=30)
                minimum_time = minimum_time.strftime('%H:%M')
                return render_template('scheduling.html', establishment_alias=establishment_alias, services = services, minimum_date = minimum_date, maximum_date = maximum_date, min_max_time=[minimum_time, static_max_time_str], time_list=time_list, open_flag=open_flag)
        
        

        #return render_template('scheduling.html', services = services, minimum_date = minimum_date, maximum_date = maximum_date, min_max_time=['07:00', static_max_time_str], time_list=time_list)
        
@app.route("/agendamento/minhas_agendas")
def schedules():

    if 'user_phone' in session:
        phone = session['user_phone']

        # In the schedules table we have a foreign key 'user_id'
        # and we want to select only the schedules of this user_id
        #cursor.execute("SELECT id FROM users WHERE email == ?", [email])
        #id = cursor.fetchone()[0]
        id = db.session.execute(db.select(Users.id).filter_by(telefone=phone)).scalar_one()

        #We could use inner join instead of multiple queries like we are doin now

        # Now we can make a query from our schedules table filtering with the id above to get only the shedules of the curent user
        #cursor.execute("SELECT id, servico, data, hora FROM schedules WHERE user_id == ? ORDER BY data DESC, hora DESC;", [id])
        #schedules_list = cursor.fetchall()
        query=text(f"select Schedules.id, Schedules.servico, Schedules.data, Schedules.hora, Establishments.nome, Schedules.estado FROM Schedules INNER JOIN Establishments ON Schedules.estabelecimento_id = Establishments.id WHERE user_id = {id} ORDER BY data DESC, hora DESC")
        #schedules_list = db.session.execute(db.select(Schedules.id, Schedules.servico, Schedules.data, Schedules.hora, Schedules.estado, Schedules.processado).filter_by(user_id=id).order_by(Schedules.data.desc(), Schedules.hora.desc())).all()
        schedules_list = db.session.execute(query)
        return render_template('user_schedules.html', schedules = schedules_list)
    
    return redirect(url_for('login'))
    

@app.route('/<establishment_alias>')
def establishment_page(establishment_alias):
    try:
        establishment_id = db.session.execute(db.select(Establishments.id).filter_by(apelido=establishment_alias)).scalar_one()
        if establishment_id:
            pass
    except:
        return redirect(url_for('index'))

    
    #Bellow we're retrievin images of the establisment page
    logo_image = Establishments_images.query.filter_by(estabelecimento_id=establishment_id, lugar='logo').first()
    hero_image = Establishments_images.query.filter_by(estabelecimento_id=establishment_id, lugar='hero').first()

    if not hero_image or not logo_image:
        hero_data_uri = None
        logo_data_uri = None

    else:
        logo_image_buffer = logo_image.buffer_data
        logo_image_base64 = base64.b64encode(logo_image_buffer).decode('utf-8')
        logo_data_uri = f'data:{logo_image.mimeType};base64, {logo_image_base64}'

        hero_image_buffer = hero_image.buffer_data
        hero_image_base64 = base64.b64encode(hero_image_buffer).decode('utf-8')
        hero_data_uri = f'data:{logo_image.mimeType};base64, {hero_image_base64}'
    

    #Loading all services of the establisment to fill in the establisment page on the services section
    services = db.session.execute(db.select(Services.servico).filter_by(estabelecimento_id=establishment_id)).all()
    #Other informations of the establishment
    query = text(f"SELECT * FROM Establishments WHERE apelido = '{establishment_alias}'")
    establishment = db.session.execute(query).all()
    
    for detail in establishment:
        establishment_details = {
            'name': detail[1],
            'alias': detail[2],
            'hero_message': detail[3],
            'secundary_msg': detail[4],
            'logo_data_uri': logo_data_uri,
            'hero_data_uri': hero_data_uri,
            'open_hours': detail[5],
            'close_hours': detail[6],
            'open_days_interval': detail[7],
            'local_characterization': detail[8],
            'burgh': detail[9],
            'province': detail[10],
            'district': detail[11],
            'tel': detail[12],
            'email': detail[13]
        }
    
    if 'user_phone' in session:
        phone = session['user_phone']
        #cursor.execute("SELECT nome FROM users WHERE email == ?", [email])
        full_name = db.session.execute(db.select(Users.nome).filter_by(telefone=phone)).scalar_one()

        #full_name = cursor.fetchone()[0]
        first_name = full_name.split(' ')[0]
        #print(full_name)
        #print(first_name)
        #askin if the user is loged in to show his name

        return render_template("establishment.html", user= first_name, logout='sair', suas_agendas = 'Minhas Agendas', establishment_details=establishment_details, services=services)
    return render_template("establishment.html", user='Entrar', establishment_details=establishment_details, services=services)
    #return render_template('establishment.html',establishment_alias=establishment_alias, name=establishment, services=services)


@app.route("/<establishment_alias>/funcionarios", methods=['GET', 'POST'])
def employers_space(establishment_alias):
    try:
        establishment_id = db.session.execute(db.select(Establishments.id).filter_by(apelido=establishment_alias)).scalar_one()
        if not establishment_id:
            return redirect(url_for('index'))
    except:
        return 'URL invalida, verifique o enderco da url'
    
    if 'employer_phone' in session:
        #Employer name on header
        phone = session['employer_phone']
        #cursor.execute("SELECT nome FROM employers WHERE email == ?", [email])
        #full_name = cursor.fetchone()[0]
        full_name = db.session.execute(db.select(Employers.nome).filter_by(telefone=phone, estabelecimento_id=establishment_id)).scalar_one()
        first_name = full_name.split(' ')[-1]

        if request.method == 'POST':
            query_date = request.form.get('search_by_date')
            query_today = request.form.get('get_today_schedules')

            if query_date:
                #cursor.execute("SELECT schedules.id,  schedules.servico, schedules.data, schedules.hora, users.nome FROM schedules INNER JOIN users ON schedules.user_id = users.id WHERE data == ? ORDER BY data, hora DESC;", [query_date])
                #date_schedules = cursor.fetchall()
                #date_schedules = db.session.execute(db.select(Schedules).join(Users, Schedules.user_id == Users.id).filter_by(Schedules.data == query_date).order_by(Schedules.data.asc(), Schedules.hora.desc())).all()
                query = text(f"SELECT Schedules.id,  Schedules.servico, Schedules.data, Schedules.hora, Users.nome FROM Schedules INNER JOIN users ON Schedules.user_id = Users.id WHERE data = '{query_date}'AND estabelecimento_id = {establishment_id} ORDER BY data, hora DESC;")
                date_schedules = db.session.execute(query).all()
                return render_template('employers_space.html', data = date_schedules, employer = first_name, logout='sair', establishment_alias=establishment_alias)
            
            if query_today:
                #----------------------------getting the current date--------------------------------#

                time_now_in_the_machine = datetime.now()
                diference_time = timedelta(hours=2)
                #We are geting the difernce betwen UTC and the time zon we are creating
                #It give us the diference of 2h ahead the utc

                utc2 = timezone(diference_time)
                #Return UTC+02:00

                #Now we have to convert the machine time to the gmt+2 time (UTC+02:00)
                mozambican_date_time = time_now_in_the_machine.astimezone(utc2)

                #formating the date and time for the quite familiar
                today_date = mozambican_date_time.strftime('%Y-%m-%d')

                #-----------------end current date---------------------------------------#

                #Shedules list
                #cursor.execute("SELECT schedules.id,  schedules.servico, schedules.data, schedules.hora, users.nome FROM schedules INNER JOIN users ON schedules.user_id = users.id WHERE data == ? ORDER BY data, hora DESC;", [today_date])
                #today_schedules = cursor.fetchall()
                #today_schedules = db.session.execute(db.select(Schedules).join(Users, Schedules.user_id == Users.id).filter_by(Schedules.data == today_date).order_by(Schedules.data.asc(), Schedules.hora.desc())).all()
                query = text(f"SELECT Schedules.id,  Schedules.servico, Schedules.data, Schedules.hora, Users.nome FROM Schedules INNER JOIN users ON Schedules.user_id = Users.id WHERE data = '{today_date}' AND estabelecimento_id = {establishment_id} ORDER BY data, hora DESC;")
                today_schedules = db.session.execute(query).all()

                return render_template('employers_space.html', data = today_schedules, employer = first_name, logout='sair', establishment_alias=establishment_alias)
            
        #cursor.execute("SELECT schedules.id,  schedules.servico, schedules.data, schedules.hora, users.nome FROM schedules INNER JOIN users ON schedules.user_id = users.id ORDER BY data DESC, hora DESC;")
        #all_schedules = cursor.fetchall()
        #all_schedules = db.session.execute(db.select(Schedules).join(Users, Schedules.user_id == Users.id).order_by(Schedules.data.asc(), Schedules.hora.desc())).all()
        query = text(f"SELECT Schedules.id,  Schedules.servico, Schedules.data, Schedules.hora, Users.nome FROM Schedules INNER JOIN Users ON Schedules.user_id = Users.id WHERE estabelecimento_id = {establishment_id} ORDER BY data DESC, hora DESC;")
        all_schedules = db.session.execute(query).all()
        return render_template('employers_space.html', data = all_schedules, employer = first_name, logout='sair', establishment_alias=establishment_alias)


    return redirect(url_for('employer_login', establishment_alias=establishment_alias))




@app.route('/<establishment_alias>/login_funcionario', methods=['GET', 'POST'])
def employer_login(establishment_alias):
    try:
        establishment_id = db.session.execute(db.select(Establishments.id).filter_by(apelido=establishment_alias)).scalar_one()
    except:
        return 'Something get wrong, please check you url'

    if 'employer_phone' in session:
        return redirect(url_for('employers_space', establishment_alias=establishment_alias))
    
    elif request.method == 'POST':
        phone = request.form.get("phone")
        password = request.form.get("password")

        
        #cursor.execute("SELECT email, senha FROM employers WHERE email == ? AND senha == ?", (email, password))
        #data = cursor.fetchall()
        data = db.session.execute(db.select(Employers.telefone, Employers.senha).filter_by(telefone=phone, senha=password, estabelecimento_id=establishment_id))

        
        if phone and password:
            for i in data:
                if (i[0], i[1]) == (phone, password):
                    #we verify if the given email and password is registered in database'

                    #we save the session for future auto login
                    session['employer_phone'] = phone
                    session.permanent = True
                    return redirect(url_for('employers_space', establishment_alias=establishment_alias))

        elif not phone or not password:
            flash("Por favor, preencha todos os campos!")
            return render_template("employer_login.html", establishment_alias=establishment_alias)
                
        
        flash("Telefone ou senha Inválida!")
        return redirect(url_for("employer_login", establishment_alias=establishment_alias))
        
    else:
        #executed if request.method == get
        return render_template("employer_login.html")

@app.route('/<establishment_alias>/employer_logout')
def employer_logout(establishment_alias):
    if 'employer_phone' in session:
        session.pop('employer_phone', None)
        return redirect(url_for('employer_login', establishment_alias=establishment_alias))
    
    return redirect(url_for('employer_login', establishment_alias=establishment_alias))



@app.route("/<establishment_alias>/admin", methods=["GET", "POST"])
def admin(establishment_alias):
    try:
        establishment_id = db.session.execute(db.select(Establishments.id).filter_by(apelido=establishment_alias)).scalar_one()
    except:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        phone = request.form.get("phone")
        password = request.form.get("password")
        #cursor.execute("SELECT email, password FROM admin WHERE email == ? AND password == ?", (email, password))
        #data = cursor.fetchall()

        data = db.session.execute(db.select(Admins.telefone, Admins.senha).filter_by(telefone=phone, senha=password, estabelecimento_id=establishment_id)).all()
        

        if phone and password:
            
            for i in data:
                if (i[0], i[1]) == (phone, password):
                    #we verify if the given email and password is registered in database'

                    session['admin_phone'] = phone
                    
                    return render_template('admin.html', establishment_alias=establishment_alias)

        elif not phone or not password:
            flash("Por favor, preencha todos os campos!")
            return render_template("login_admin.html")
                
        
        flash("Email ou senha Inválida!")
        return render_template("login_admin.html")
        
    else:
        #executed if request.method == get
        if 'admin_phone' in session:
            
            phone = session['admin_phone']

            admin_id_belongs = db.session.execute(db.select(Admins.estabelecimento_id).filter_by(telefone=phone)).scalar_one()
            if admin_id_belongs == establishment_id:
                #It means that the admin belongs to that establishment,
                # because the estabelecimento_ saved with him is iguals to the current page id

                #Gathering all the get query of admin page (list user, shedule...)
                list_employers = request.args.get('list_employers')
                client_id = request.args.get('client_id')
                client_name = request.args.get('client_name')
                schedule_id = request.args.get('schedule_id')
                employer_id = request.args.get('remove_employer')

                new_service = request.args.get('new_service')
                new_service_price = request.args.get('new_service_price')





                '''
                Working with adming queries
                The sequence of if elif is execucted when the admin loged in
                '''
                #We check if the admin makes a query with the method get

                if list_employers:
                    #rendering employers
                    table_title = 'Lista de Funcionários'

                    #Getting the columns name
                    columns_name = ('ID', 'Nome', 'Telefone', 'Email', 'Função', 'Contrato')

                    #cursor.execute("SELECT * FROM employers")
                    #employers = cursor.fetchall()
                    #employers = db.session.execute(db.select(Employers)).all(),
                    query = text(f"SELECT Employers.id, Employers.nome, Employers.telefone, Employers.email, Employers.funcao, Employers.contrato FROM Employers WHERE estabelecimento_id = {establishment_id}")
                    employers = db.session.execute(query).all()
                    return render_template("admin.html", table_title=table_title, columns_name=columns_name, data=employers, establishment_alias=establishment_alias)
                
                elif employer_id:
                    #Getting the columns name
                    #cursor.execute("SELECT nome FROM employers WHERE id == ?", [employer_id])
                    #nome = cursor.fetchone()[0]
                    try:
                        funcionario = db.session.execute(db.select(Employers).filter_by(id=employer_id, estabelecimento_id=establishment_id)).scalar_one()
                        nome = funcionario.nome
                        table_title = 'Eliminado funcionário/a ' + nome

                        #cursor.execute("DELETE FROM employers WHERE id == ?", [employer_id])
                        #db.commit()
                        db.session.delete(funcionario)
                        db.session.commit()
                        return render_template("admin.html", table_title=table_title, establishment_alias=establishment_alias)
                    except:
                        flash('Não existe funcionário com o id ' + employer_id)
                        return render_template("admin.html", establishment_alias=establishment_alias)

                
                    '''
                elif client_id:
                    table_title = 'Pesquisa de cliente por id'

                    #Getting the columns name
                    columns_name = ('ID', 'Nome', 'Email', 'Telefone', 'Senha', 'Inscrito desde')

                    #cursor.execute("SELECT * FROM users WHERE id == ?", [client_id])
                    #client = cursor.fetchall()
                    #client = db.session.execute(db.select(Users).filter_by(id=client_id)).all()
                    query = text(f"SELECT * FROM Users WHERE id = {client_id}")
                    client = db.session.execute(query).all()
                    return render_template("admin.html", table_title=table_title, columns_name=columns_name, data=client)
                
                
                elif client_name:
                    table_title = 'Pesquisa cliente por nome'

                    #Getting the columns name
                    columns_name = ('ID', 'Nome', 'Email', 'Telefone', 'Senha', 'Inscrito desde')

                    #cursor.execute("SELECT * FROM users WHERE nome LIKE ?", ['%'+client_name+'%'])
                    #schedules = cursor.fetchall()
                    query = text(f"SELECT * FROM users WHERE nome LIKE '%{client_name}%'")
                    schedules = db.session.execute(query).all()
                    return render_template("admin.html", table_title=table_title, columns_name=columns_name, data=schedules)
                    '''

                elif schedule_id:
                    table_title = 'Consulta de agenda'

                    #Getting the columns name
                    columns_name = ('ID agenda', 'Serviço', 'Data', 'Hora', 'Cliente', 'Telefone')

                    #cursor.execute("SELECT * FROM schedules WHERE id == ?", [schedule_id])
                    #schedules = cursor.fetchall()
                    #query = text(f"SELECT * FROM Schedules WHERE id = {schedule_id} AND estabelecimento_id = {establishment_id}")
                    query = text(f"SELECT Schedules.id,  Schedules.servico, Schedules.data, Schedules.hora, Users.nome, Users.telefone FROM Schedules INNER JOIN users ON Schedules.user_id = Users.id WHERE Schedules.id = '{schedule_id}' AND estabelecimento_id = {establishment_id} ORDER BY data, hora DESC;")
                    schedules = db.session.execute(query).all()
                    if not schedules:
                        flash('Não tem nenhuma agenda com o id ' + schedule_id)
                        return  render_template('admin.html', establishment_alias=establishment_alias)
                    return render_template("admin.html", table_title=table_title, columns_name=columns_name, data=schedules, establishment_alias=establishment_alias)
                
                elif new_service:
                    #admin requested to add a new service
                    try:
                        existing_service = db.session.execute(db.select(Services.servico, Services.preco).filter_by(estabelecimento_id=establishment_id)).scalar()
                        if existing_service:
                            flash('Existe este serviço no seu estabelecimento! Você pode estar vendo esta mensagem por duas razoes: tentou adicionar um serviço que já tem no seu estabelecimento ou actualizou a pagina depois de adicionar um serviço.')
                            return  render_template('admin.html', establishment_alias=establishment_alias)
                    except:
                        pass
                    service = Services(
                        servico = new_service,
                        preco = new_service_price,
                        estabelecimento_id = establishment_id
                    )

                    db.session.add(service)
                    db.session.commit()

                    table_title = 'Serviço adicionado com sucesso'

                    #Getting the columns name
                    columns_name = ('ID', 'Serviço', 'Preço')

    
                    services = db.session.execute(db.select(Services.id, Services.servico, Services.preco).filter_by(estabelecimento_id=establishment_id)).all()
                    return render_template('admin.html', table_title=table_title, columns_name=columns_name, data=services)
        
        
        
        #If the admin have not given his email and password
        # or admin does'nt beleong to the establishment (maybe he made an url injection )
        return render_template("login_admin.html")

@app.route("/<establishment_alias>/admin/subscribe_employer", methods=['GET', 'POST'])
def subscribe_employer(establishment_alias):
    try:
        establishment_id = db.session.execute(db.select(Establishments.id).filter_by(apelido=establishment_alias)).scalar_one()
        if not establishment_id:
            return redirect(url_for('admin'))
    except:
        return 'URL inválida, verifique o endereço da url'
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        document_type = request.form.get('document_type')
        document_number = request.form.get('document_number')
        birth_date = request.form.get('birth_date')
        birth_place = request.form.get('birth_place')
        functionalite = request.form.get('functionalite')
        contrat = request.form.get('contrat')
        
        #cursor.execute("SELECT email, telefone, numero_documento FROM employers")
        #available_info = cursor.fetchall()
        #query = text("SELECT email, telefone, numero_documento FROM Employers")
        #available_info = db.session.execute(query).all()
        available_info = db.session.execute(db.select(Employers.email, Employers.telefone).filter_by(estabelecimento_id=establishment_id)).all()

        for i in available_info:
            if i[0] == email or i[1] == phone:
                flash("Existe esse funcionário. Use outro e-mail ou número de telefone.")
                return render_template('subscribe_employer.html')
            
        if not name or not email or not phone or not password or not document_type or not  document_number or not birth_date or not birth_place or not functionalite or not contrat:
            flash("Por favor, preencha todos os campos!")
            return render_template('subscribe_employer.html')
        
        else:
            #Treating the name from the bad user spacing after the name and capitizing every part of name
            splited = name.split(' ')
            treated_name = ''
            #Store the first midle and last name in one string but capitalized
            
            if len(splited) > 1:
                for i in range(len(splited)):
                    treated_name += ' ' + splited[i].capitalize()
                #cursor.execute("INSERT INTO employers (nome, telefone, email, senha, tipo_documento, numero_documento, data_nascimento, local_nascimento, funcao, contrato) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (treated_name, phone, email, password, document_type, document_number, birth_date, birth_place, functionalite, contrat))
                #db.commit()
                employer = Employers(
                    nome = treated_name,
                    telefone = phone,
                    email = email,
                    senha = password,
                    tipo_documento = document_type,
                    numero_documento = document_number,
                    data_nascimento = birth_date,
                    local_nascimento = birth_place,
                    funcao = functionalite,
                    contrato = contrat,
                    estabelecimento_id = establishment_id
                )
                db.session.add(employer)
                db.session.commit()
                return redirect(url_for('admin', establishment_alias=establishment_alias))
            
            #Inserting in to database the data
            name = name.capitalize()
            #cursor.execute("INSERT INTO employers (nome, telefone, email, senha, tipo_documento, numero_documento, data_nascimento, local_nascimento, funcao, contrato) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, phone, email, password, document_type, document_number, birth_date, birth_place, functionalite, contrat))
            #db.commit()
            employer = Employers(
                nome = name,
                telefone = phone,
                email = email,
                senha = password,
                tipo_documento = document_type,
                numero_documento = document_number,
                data_nascimento = birth_date,
                local_nascimento = birth_place,
                funcao = functionalite,
                contrato = contrat,
                estabelecimento_id = establishment_id
            )
            db.session.add(employer)
            db.session.commit()

            #saving the email and name on session
            return redirect(url_for('admin', establishment_alias=establishment_alias))
        
    
    
    else:
        #When the methods is get
        #Must be the admin making subscription
        if 'admin' in session:
            return render_template('subscribe_employer.html', establishment_alias=establishment_alias)
        
        return redirect(url_for('admin', establishment_alias=establishment_alias))



if __name__ == "__main__":

    port = int(os.getenv('PORT'), '5000')
    #We are getting the port where our server is running, else we use the 5000
    app.run(host='0.0.0.0', port=port)

    
    #app.run(debug=True)