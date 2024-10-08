"""import sqlite3


db = sqlite3.connect("csm_barber_data.db")
cur = db.cursor()

def create_users_table():
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, email TEXT NOT NULL, telefone TEXT NOT NULL, senha TEXT NOT NULL)")

def insert_user():
    cur.execute("INSERT INTO users (nome, email, telefone, senha) VALUES (?, ?, ?, ?)", ('Oscar Namicano', 'onamicanosail01@gmail.com', '+258842244136', '1234567890'))
    db.commit()

def show_data():
    cur.execute("SELECT * FROM schedules")
    print(cur.fetchall())


#insert_data()


def create_schedule_table():
    cur.execute("CREATE TABLE IF NOT EXISTS schedules (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, servico TEXT NOT NULL, data TEXT NOT NULL, hora TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id))")


def insert_schedule(data):
    cur.execute("INSERT INTO schedules (user_id, servico, data, hora) VALUES (?, ?, ?, ?)")
    db.commit()

def create_employers_table():
    cur.execute("CREATE TABLE IF NOT EXISTS employers (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, telefone TEXT NOT NULL, email TEXT NOT NULL, senha TEXT NOT NULL, tipo_documento TEXT NOT NULL, numero_documento TEXT NOT NULL, data_nascimento TEXT NOT NULL, local_nascimento TEXT NOT NULL, funcao TEXT NOT NULL, contrato TEXT NOT NULL)")

def insert_employer(info_tuple):
    cur.execute("INSERT INTO employers (nome, telefone, email, senha, tipo_documento, numero_documento, data_nascimento, local_nascimento, funcao, contrato) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", info_tuple)
    db.commit()


def create_admin_table():
    cur.execute("CREATE TABLE IF NOT EXISTS admin (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, email TEXT NOT NULL, password TEXT NOT NULL)")

def insert_admin():
    cur.execute("INSERT INTO admin (nome, email, password) VALUES (?, ?, ?)", ('Oscar Namicano', 'onamicanosail01@gmail.com', 'senhasalaoebarbeariacsm2024'))


#cur.execute("DROP TABLE admin")
create_users_table()
create_schedule_table()
create_employers_table()
create_admin_table()

#insert_admin()
#funcionario = ('Oscar', '842244136', 'onamicanosail@gmail.com', '1234567890', 'bi', '12345', '06-09-2000', 'Parta', 'CEO', 'Tempo inteiro') 
#insert_employer(funcionario)
#insert_admin()
"""



from datetime import datetime, timedelta, timezone


class GetDateTime():
    time_now_in_the_machine = datetime.now()
    diference_time = timedelta(hours=2)
    #We are geting the difernce betwen UTC and the time zon we are creating
    #It give us the diference of 2h ahead the utc

    utc2 = timezone(diference_time)
    #Return UTC+02:00

    #Now we have to convert the machine time to the gmt+2 time (UTC+02:00)
    mozambican_date_time = time_now_in_the_machine.astimezone(utc2)

    def datenow(self):
        date_now = self.mozambican_date_time.strftime('%Y:%m:%d')
        return date_now

    def timenow(self):
        time_now = self.mozambican_date_time.strftime('%H:%M:%S')
        return time_now
    
tm = GetDateTime()

a = tm.datenow
utcnow_str = datetime.now(datetime.UTC)
#utcnow_obj = datetime.strptime(utcnow_str, '%Y-%m-%d %H:%M:%S')
sum = datetime.utcnow() + timedelta(hours=2)
print(utcnow_str)