from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
import sqlite3
from datetime import datetime, timedelta, timezone
import os


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
app.config['SECRET_KEY'] = 'MY_SECRET_KEY_In_this_app_till_now_for_n00ne-descovery'
#Configure the database:
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///csm_salon_and_barber_data.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://u3pdcv7rl74tkl:p85a1d0a972a27687149b85638b2374121480a33ead9d37e1065c94c276cc30a1@cat670aihdrkt1.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d6dbar3069o937'
#Initialize the app with rhe sql_alchemy extension:
#db.init_app(app)
#Set duration of the users sessions
db = SQLAlchemy(app)
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
    email = db.Column(db.String(150), unique=True)
    telefone = db.Column(db.String(150), nullable=False, unique=True)
    senha = db.Column(db.String(150), nullable=False)
    data_registro = db.Column(db.DateTime, default=utc_plus_2)
    schedules = db.relationship('Schedules', backref='users')

class Schedules(db.Model):
    '''
    It's creating the table schedules in database
    '''
    utc_plus_2 = datetime.utcnow() + timedelta(hours=2)
    utc_plus_2_str = utc_plus_2.strftime('%H:%M:%S')

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    servico = db.Column(db.String(150), nullable=False)
    data = db.Column(db.String(150), nullable=False)
    hora = db.Column(db.String(150), nullable=False)
    processado = db.Column(db.String(10), default=utc_plus_2_str)
    estado = db.Column(db.String(100), default='-')
    messagem = db.Column(db.Text)

class Employers(db.Model):
    '''
    It's creating the table schedules in database
    '''
    utc_plus_2 = datetime.utcnow() + timedelta(hours=2)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False)
    telefone = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    senha = db.Column(db.String(150), nullable=False)
    tipo_documento = db.Column(db.String(150), nullable=False)
    numero_documento = db.Column(db.String(150), nullable=False)
    data_nascimento = db.Column(db.String(150), nullable=False)
    local_nascimento = db.Column(db.String(150), nullable=False)
    funcao = db.Column(db.String(150), nullable=False)
    contrato = db.Column(db.String(150), nullable=False)
    data_entrada = db.Column(db.DateTime, default=utc_plus_2)

class Admins(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False)
    telefone = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    senha = db.Column(db.String(150), nullable=False)
    privilegios = db.Column(db.String(150))


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
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        password_confirmation = request.form.get('password_confirmation')
        
        #cursor.execute("SELECT email, telefone FROM users")
        emails = db.session.execute(db.select(Users.email, Users.telefone)).all()
        #emails = cursor.fetchall()

        for i in emails:
            if i[0] == email:
                flash("Existe essa conta com o mesmo e-mail. Use outro e-mail!")
                return render_template('signup.html')
            
            elif i[1]== phone:
                flash("Existe essa conta com o mesmo número. Use outro número de telefone")
                return render_template('signup.html')

        if not name or not email or not phone or not password:
            flash("Por favor, o campo de nome!")
            return render_template('signup.html')
        
        elif not phone:
            flash("Por favor, preencha o campo de telefone!")
            return render_template('signup.html')
        
        elif not password:
            flash("Por favor, preencha crie uma sena!")
            return render_template('signup.html')

        elif  password != password_confirmation:
            flash("As senhas devem ser iguais!")
            return render_template('signup.html')    
        
        else:
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
                    email = email,
                    telefone = phone,
                    senha = password
                )
                db.session.add(user)
                db.session.commit()

                session['user_phone'] = phone
                session.permanent = True
                return redirect(url_for('index'))
            
            #Inserting in to database the data if if the user gives only the first name
            name = name.capitalize()
            #cursor.execute("INSERT INTO users (nome, email, telefone, senha) VALUES (?, ?, ?, ?)", (name, email, phone, password))
            #db.commit()
            user = Users(
                nome = name,
                email = email,
                telefone = phone,
                senha = password
            )
            db.session.add(user)
            db.session.commit()

            #saving the email and name on session
            session['user_phone'] = phone
            session.permanent = True
            return redirect(url_for('index'))
        
    else:
        #if request.method == 'get'
        return render_template("signup.html")

@app.route("/login", methods=['GET', 'POST'])
def login():

    #Checking if we have a session of the user
    #we are askin if we have the key: user_name in session
    #if true, it's not necessary tu put login info
    if 'user_phone' in session:
        return redirect(url_for('index'))
    
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

                    #we save the session for future auto login
                    session['user_phone'] = phone
                    session.permanent = True
                    return redirect(url_for('index'))

        elif not phone or not password:
            flash("Por favor, preencha todos os campos!")
            return render_template("login.html")
                
        
        flash("E-mail ou senha inválida!")
        return redirect(url_for("login"))
        
    else:
        #executed if request.method == get
        return render_template("login.html")
    

@app.route("/terminar_seccao")
def logout():
    if 'user_phone' in session:
        session.pop('user_phone', None)
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))
    
    
    
@app.route('/agendamento', methods=['get', 'post'])
def scheduling():

    #Bellow we set a tuples list to pass in frontend template
    #the tuples take a servive id, service name an the service price respectively

    services = [('id_tranca', 'Trançar mexas/cabelo', '250-300,00MT'),
                ('id_simple_cut', 'Escovinha/carreca...','30,00MT'),
                ('id_france', 'Corte francês/similar', '50,00MT'),
                ('id_wash_hair', 'Lavagem de cabelo', '100,00MT'),
                ('id_feed_hair', 'Alimentação de cabelo', '30,00MT'),
                ('id_retouch', 'Retocagem de cabelo', '250,00MT'),
                ('id_paint_hair', 'Pintar cabelo', '50,00MT'),
                ('id_diamante_pack', 'Look Elite', '810,00MT'),
                ('id_other', 'Explico no atendimento')]
    
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
        scheduled = db.session.execute(db.select(Schedules.data, Schedules.hora).filter_by(data=date, hora=time)).all()
        if date and time:
            for i in scheduled:
                if (i[0], i[1]) == (date, time):
                    flash('Horario ocupado! Tente outro horario')
                    return redirect(url_for('scheduling'))

        phone_in_session = session['user_phone']
        #we're a taking the email from session to make a query asking name with it in our db

        #cursor.execute("SELECT id FROM users WHERE email == ?", [email_in_session])
        # Once you only gave the function (cursor.execute) a string, the string is being interpreted as list of characters.

        #id = cursor.fetchone()[0] #we gave [0] because it returns (n,) and we want n
        id = db.session.execute(db.select(Users.id).filter_by(telefone=phone_in_session)).scalar_one()



        if not service or not date or not time:
            flash('Você deve preencher todos os campos.')
            return render_template('scheduling.html')

        
        else:
            # Here was scheduled sucessfully Sucess
            
            #cursor.execute("INSERT INTO schedules (user_id, servico, data, hora) VALUES (?, ?, ?, ?)", (id, service, date, time))
            #db.commit()
            schedule = Schedules(
                user_id = id,
                servico = service,
                data = date,
                hora = time
            )
            db.session.add(schedule)
            db.session.commit()
            return redirect(url_for('schedules'))
        

    else:
        #executed if method==get

        if 'user_phone' not in session:
            #it checks if the user has loged in
            return redirect(url_for('login'))


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
            return render_template('scheduling.html', services = services, minimum_date = minimum_date, maximum_date = maximum_date, min_max_time=[static_min_hour_str, static_max_time_str], time_list=time_list, closed_flag = closed_flag)
        
        elif curent_time_plus_10m_obj <= static_max_time_obj:
            #It means tha the salon is not closed
            #And the user has 10 minutes to arrive in the salon
            open_flag = True
            if (current_minutes_obj + timedelta(minutes=5)) >= static_minutes_obj:
                #It means that the next available hour will be H:00min
                
                minimum_time = curent_time_without_minutes_obj + timedelta(minutes=60)
                minimum_time = minimum_time.strftime('%H:%M')
                
                return render_template('scheduling.html', services = services, minimum_date = minimum_date, maximum_date = maximum_date, min_max_time=[minimum_time, static_max_time_str], time_list=time_list, open_flag=open_flag)
            
            else:
                #It means the next time will be H:30min
                minimum_time = curent_time_without_minutes_obj + timedelta(minutes=30)
                minimum_time = minimum_time.strftime('%H:%M')
                return render_template('scheduling.html', services = services, minimum_date = minimum_date, maximum_date = maximum_date, min_max_time=[minimum_time, static_max_time_str], time_list=time_list, open_flag=open_flag)
        
        

        #return render_template('scheduling.html', services = services, minimum_date = minimum_date, maximum_date = maximum_date, min_max_time=['07:00', static_max_time_str], time_list=time_list)
        
@app.route("/agendamento/minhas_gendas")
def schedules():

    if 'user_phone' in session:
        phone = session['user_phone']

        # In the schedules table we have a foreign key 'user_id'
        # and we want to select only the schedules of this user_id
        #cursor.execute("SELECT id FROM users WHERE email == ?", [email])
        #id = cursor.fetchone()[0]
        id = db.session.execute(db.select(Users.id).filter_by(telefone=phone)).scalar_one()

        #We could use inner join instead of multiple queries like we are doin now

        # Now we can make a query from our shedukeles table filtering with the id above to get only the shedules of the curent user
        #cursor.execute("SELECT id, servico, data, hora FROM schedules WHERE user_id == ? ORDER BY data DESC, hora DESC;", [id])
        #schedules_list = cursor.fetchall()
        schedules_list = db.session.execute(db.select(Schedules.id, Schedules.servico, Schedules.data, Schedules.hora, Schedules.estado, Schedules.processado).filter_by(user_id=id).order_by(Schedules.data.desc(), Schedules.hora.desc())).all()
        
        return render_template('user_schedules.html', schedules = schedules_list)
    
    return redirect(url_for('login'))
    

@app.route("/funcionarios", methods=['GET', 'POST'])
def employers_space():
    if 'employer_email' in session:
        #Employer name on header
        email = session['employer_email']
        #cursor.execute("SELECT nome FROM employers WHERE email == ?", [email])
        #full_name = cursor.fetchone()[0]
        full_name = db.session.execute(db.select(Employers.nome).filter_by(email=email)).scalar_one()
        first_name = full_name.split(' ')[-1]
        print(full_name)
        print(first_name)

        if request.method == 'POST':
            query_date = request.form.get('search_by_date')
            query_today = request.form.get('get_today_schedules')

            if query_date:
                #cursor.execute("SELECT schedules.id,  schedules.servico, schedules.data, schedules.hora, users.nome FROM schedules INNER JOIN users ON schedules.user_id = users.id WHERE data == ? ORDER BY data, hora DESC;", [query_date])
                #date_schedules = cursor.fetchall()
                #date_schedules = db.session.execute(db.select(Schedules).join(Users, Schedules.user_id == Users.id).filter_by(Schedules.data == query_date).order_by(Schedules.data.asc(), Schedules.hora.desc())).all()
                query = text(f"SELECT Schedules.id,  Schedules.servico, Schedules.data, Schedules.hora, Users.nome FROM Schedules INNER JOIN users ON Schedules.user_id = Users.id WHERE data = '{query_date}' ORDER BY data, hora DESC;")
                date_schedules = db.session.execute(query).all()
                print(query)
                return render_template('employers_space.html', data = date_schedules, employer = first_name, logout='sair')
            
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
                query = text(f"SELECT Schedules.id,  Schedules.servico, Schedules.data, Schedules.hora, Users.nome FROM Schedules INNER JOIN users ON Schedules.user_id = Users.id WHERE data = '{today_date}' ORDER BY data, hora DESC;")
                today_schedules = db.session.execute(query).all()

                return render_template('employers_space.html', data = today_schedules, employer = first_name, logout='sair')
            
        #cursor.execute("SELECT schedules.id,  schedules.servico, schedules.data, schedules.hora, users.nome FROM schedules INNER JOIN users ON schedules.user_id = users.id ORDER BY data DESC, hora DESC;")
        #all_schedules = cursor.fetchall()
        #all_schedules = db.session.execute(db.select(Schedules).join(Users, Schedules.user_id == Users.id).order_by(Schedules.data.asc(), Schedules.hora.desc())).all()
        query = text("SELECT Schedules.id,  Schedules.servico, Schedules.data, Schedules.hora, Users.nome FROM Schedules INNER JOIN Users ON Schedules.user_id = Users.id ORDER BY data DESC, hora DESC;")
        all_schedules = db.session.execute(query).all()
        return render_template('employers_space.html', data = all_schedules, employer = first_name, logout='sair')


    return redirect(url_for('employer_login'))




@app.route('/login_funcionario', methods=['GET', 'POST'])
def employer_login():
    if 'employer_email' in session:
        return redirect(url_for('employers_space'))
    
    elif request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        
        #cursor.execute("SELECT email, senha FROM employers WHERE email == ? AND senha == ?", (email, password))
        #data = cursor.fetchall()y
        data = db.session.execute(db.select(Employers.email, Employers.senha).filter_by(email=email, senha=password))

        
        if email and password:
            for i in data:
                if (i[0], i[1]) == (email, password):
                    #we verify if the given email and password is registered in database'

                    #we save the session for future auto login
                    session['employer_email'] = email
                    session.permanent = True
                    return redirect(url_for('employers_space'))

        elif not email or not password:
            flash("Por favor, preencha todos os campos!")
            return render_template("employer_login.html")
                
        
        flash("E-mail ou senha Inválida!")
        return redirect(url_for("employer_login"))
        
    else:
        #executed if request.method == get
        return render_template("employer_login.html")

@app.route('/employer_logout')
def employer_logout():
    if 'employer_email' in session:
        session.pop('employer_email', None)
        return redirect(url_for('employer_login'))
    
    return redirect(url_for('employer_login'))



@app.route("/admin", methods=["GET", "POST"])
def admin():
    
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        #cursor.execute("SELECT email, password FROM admin WHERE email == ? AND password == ?", (email, password))
        #data = cursor.fetchall()
        

        
        if email and password:
            '''
            for i in data:
                if (i[0], i[1]) == (email, password):
                    #we verify if the given email and password is registered in database'

                    session['admin'] = email
                    session.permanent = True
                    return render_template('admin.html')
            '''
            if (email, password) == ('onamicanosail01@gmail.com', 'AdminNamicano'):
                return render_template('admin.html')

        elif not email or not password:
            flash("Por favor, preencha todos os campos!")
            return render_template("login_admin.html")
                
        
        flash("Email ou senha Inválida!")
        return render_template("login_admin.html")
        
    else:
        #executed if request.method == get

        #Gathering all the get query of admin pagr (list user, shedule...)
        list_employers = request.args.get('list_employers')
        client_id = request.args.get('client_id')
        client_name = request.args.get('client_name')
        schedule_id = request.args.get('schedule_id')

        employer_id = request.args.get('remove_employer')





        '''
        Working with adming queries
        The sequence of if elif is execucted when the admin loged in
        '''
        #We check if the admin makes a query with the method get

        if list_employers:
            #rendering employers
            table_title = 'Lista de Funcionarios'

            #Getting the columns name
            columns_name = ('ID', 'Nome', 'Telefone', 'Email', 'Senha', 'Tipo_documento', 'Numero_documento', 'Data_nascimento', 'Local_nascimento', 'Funcao', 'Contrato')

            #cursor.execute("SELECT * FROM employers")
            #employers = cursor.fetchall()
            #employers = db.session.execute(db.select(Employers)).all(),
            query = text(f"SELECT * FROM Employers")
            employers = db.session.execute(query).all()
            return render_template("admin.html", table_title=table_title, columns_name=columns_name, data=employers)
        
        elif employer_id:
            #Getting the columns name
            #cursor.execute("SELECT nome FROM employers WHERE id == ?", [employer_id])
            #nome = cursor.fetchone()[0]
            funcionario = db.session.execute(db.select(Employers).filter_by(id=employer_id)).scalar_one()
            nome = funcionario.nome
            table_title = 'Eliminado funcionario/a ' + nome

            #cursor.execute("DELETE FROM employers WHERE id == ?", [employer_id])
            #db.commit()
            db.session.delete(funcionario)
            db.session.commit()
            return render_template("admin.html", table_title=table_title)
        
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
        
        elif schedule_id:
            table_title = 'Consulta de agenda'

            #Getting the columns name
            columns_name = ('ID', 'Cliente id', 'Servico', 'Data', 'Hora')

            #cursor.execute("SELECT * FROM schedules WHERE id == ?", [schedule_id])
            #schedules = cursor.fetchall()
            query = text(f"SELECT * FROM Schedules WHERE id = {schedule_id}")
            schedules = db.session.execute(query).all()
            return render_template("admin.html", table_title=table_title, columns_name=columns_name, data=schedules)
        
        
        
        #If the admin have not given the his email and password
        return render_template("login_admin.html")
    
    


@app.route("/admin/subscribe_employer", methods=['GET', 'POST'])
def subscribe_employer():
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
        query = text("SELECT email, telefone, numero_documento FROM Employers")
        available_info = db.session.execute(query).all()

        for i in available_info:
            if i[0] == email or i[1] == phone or i[2] == document_number:
                flash("Existe esse funcionário. Use outro e-mail ou número de telefone ou Numero de documento.")
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
                    contrato = contrat
                )
                db.session.add(employer)
                db.session.commit()
                return redirect(url_for('admin'))
            
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
                contrato = contrat
            )
            db.session.add(employer)
            db.session.commit()

            #saving the email and name on session
            return redirect(url_for('admin'))
        
    
    
    else:
        #When the methods is get
        #Must be the admin making subscription
        if 'admin' in session:
            return render_template('subscribe_employer.html')
        
        return redirect(url_for('admin'))



if __name__ == "__main__":
    
    port = int(os.getenv('PORT'), '5000')
    #We are getting the port where our server is running, else we use the 5000
    app.run(host='0.0.0.0', port=port)
    '''
    
    app.run(host = '0.0.0.0', port='5000', debug=True)
    '''