from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flaskext.mysql import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
#from passlib.hash import sha256_crypt
from functools import wraps


app = Flask(__name__)

app.config.from_object('config')


mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Tonio123'
app.config['MYSQL_DATABASE_DB'] = 'airline'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
connection = mysql.connect()


# Index
@app.route('/')
def index():


    return render_template('index.html')


# About
@app.route('/about')
def about():
    return render_template('about.html')


# Register Form Class
class RegisterForm(Form):
    surname =  StringField('Surname', [validators.Length(min=1, max=50)])
    firstname = StringField('First Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    adresse = StringField('Adresse',[validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        surname = form.surname.data
        firstname = form.firstname.data
        username = form.username.data
        email = form.email.data
        adresse = form.adresse.data
        password = form.password.data

        print("---------------------------"+str(adresse))

        # Create cursor
        cur = connection.cursor()

        # Execute query
        cur.execute("INSERT INTO clients(surname, firstname, email, username, address, password) VALUES(%s, %s, %s, %s, %s, %s)", (surname, firstname, email, username, adresse, password))

        # Commit to DB
        connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = connection.cursor()

        # check if the username and password exist
        result = cur.execute("SELECT * FROM clients WHERE username = %s AND password = %s", (username, password_candidate))

        if result == 1:

            session['logged_in'] = True
            session['username'] = username

            # check if the user is an admin 
            if username == 'admin' and password_candidate == 'admin':
                session['admin'] = True

            flash('You are now logged in', 'success')
            return redirect(url_for('profil'))
            
            # Close connection
            cur.close()
        else:
           
            error = 'Incorrect username or password'
            return render_template('login.html', error=error)

    
    return render_template('login.html')


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Only for admin', 'danger')
            return redirect(url_for('profil'))
    return wrap



@app.route('/profil')
@is_logged_in
def profil():
    
    return render_template('profil.html')




# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))  

@app.route('/add_airport', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def add_airport():
    if request.method == 'POST':
        # Get Form Fields
        name = request.form['name']
        code = request.form['code']
        city = request.form['city']


        # Create cursor
        cur = connection.cursor()

        cur.execute("INSERT INTO airports(name, code, city) VALUES(%s, %s, %s)", (name, code, city))

        # Commit to DB
        connection.commit()

        # Close connection
        cur.close()

        flash('Airport added succefuly', 'success')

        return redirect(url_for('profil'))


    return render_template('add_airport.html')



@app.route('/add_links', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def add_link():

    # Create cursor
    cur = connection.cursor()

    result = cur.execute("SELECT * FROM airports")
    data = cur.fetchall()

    list_aircraft = list(data)

    if request.method == 'POST':
        # Get Form Fields
        departure = request.form['departure'].strip('()').split(',')
        arrival = request.form['arrival'].strip('()').split(',')


        id1 = departure[0]
        id2 = arrival[0]

        cur.execute("INSERT INTO links(departure_airportID, arrival_airportID) VALUES(%s, %s)", (id1, id2))

        # Commit to DB
        connection.commit()

        # Close connection
        cur.close()

        flash('Link added succefuly', 'success')

        return redirect(url_for('profil'))


    return render_template('add_links.html', list_aircraft=list_aircraft)


@app.route('/add_aircraft', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def add_aircraft():


    if request.method == 'POST':
        # Get Form Fields
        immatriculation = request.form['immatriculation']
        type_ = request.form['type']
        seats = request.form['seats']

        # Create cursor
        cur = connection.cursor()
       

        cur.execute("INSERT INTO aircrafts(immatriculation, type, seats) VALUES(%s, %s, %s)", (immatriculation, type_, seats))

        # Commit to DB
        connection.commit()

        # Close connection
        cur.close()

        flash('Aircraft added succefuly', 'success')

        return redirect(url_for('profil'))


    return render_template('add_aircraft.html')


@app.route('/add_flight', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def add_flight():

    # Create cursor
    cur = connection.cursor()

    cur.execute("SELECT * FROM aircrafts")
    data = cur.fetchall()
    list_aircrafts = list(data)

    cur.execute("SELECT * FROM links")
    data = cur.fetchall()
    list_links = list(data)

    list_link = []

    for x in list_links:
        id1 = x[1]
        id2 = x[2]
        cur.execute("SELECT name FROM airports WHERE airportID = %s",(id1))
        data = cur.fetchone()
        
        cur.execute("SELECT name FROM airports WHERE airportID = %s",(id2))
        data2 = cur.fetchone()
        str1 = str(x[0])+' : from ' + data[0]+' to '+data2[0]
    
        list_link.append(str1)

    if request.method == 'POST':
        # Get Form Fields
        date1 = request.form['date1']
        date2 = request.form['date2']
        time1 = request.form['time1']
        time2 = request.form['time2']

        try :
            aircraft = request.form['aircraft'].strip('()').split(',')[0]
            link = request.form['link'].split(':')[0]
        except:
            flash('Aircraft or link missed', 'danger')
            return redirect(url_for('add_flight'))

        print(aircraft)
        print(link)

        if date1 == '' or date2 == '' or time1 == '' or time2 == '':
            flash('Complete Form', 'danger')
            return redirect(url_for('add_flight'))

        cur.execute("INSERT INTO flights(date1, date2, departure_time, arrival_time, aircraftID, linkID) VALUES(%s, %s, %s, %s, %s, %s)", (date1, date2, time1, time2, aircraft, link))

        # Commit to DB
        connection.commit()

        # Close connection
        cur.close()

        flash('Link added succefuly', 'success')

        return redirect(url_for('profil'))


    return render_template('add_flight.html',list_aircraft=list_aircrafts, list_link = list_link )



@app.route('/all_flights')
@is_logged_in
@is_admin
def all_flights():

    # Create cursor
    cur = connection.cursor()
    result = cur.execute("SELECT * FROM flights")
    flights = cur.fetchall()
    print(str(result)+'----------')
    if result > 0:
        return render_template('all_flights.html',flights=flights)
        
    
    else:
        msg = "No flights found"
        return render_template('all_flights.html',msg = msg)

    cur.close()


@app.route('/edit_flight/<string:id>', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def edit_flight(id):

    # Create cursor
    cur = connection.cursor()

    cur.execute("SELECT * FROM aircrafts")
    data = cur.fetchall()
    list_aircrafts = list(data)

    cur.execute("SELECT * FROM links")
    data = cur.fetchall()
    list_links = list(data)

    list_link = []

    for x in list_links:
        id1 = x[1]
        id2 = x[2]
        cur.execute("SELECT name FROM airports WHERE airportID = %s",(id1))
        data = cur.fetchone()
        
        cur.execute("SELECT name FROM airports WHERE airportID = %s",(id2))
        data2 = cur.fetchone()
        str1 = str(x[0])+' : from ' + data[0]+' to '+data2[0]
    
        list_link.append(str1)

        cur.execute("SELECT * FROM flights WHERE flightID = %s",(id))

        edit_one = cur.fetchone()

    if request.method == 'POST':
        # Get Form Fields
        date1 = request.form['date1']
        date2 = request.form['date2']
        time1 = request.form['time1']
        time2 = request.form['time2']

        try :
            aircraft = request.form['aircraft'].strip('()').split(',')[0]
            link = request.form['link'].split(':')[0]
        except:
            flash('Aircraft or link missed', 'danger')
            return redirect(url_for('add_flight'))

        print(aircraft)
        print(link)

        if date1 == '' or date2 == '' or time1 == '' or time2 == '':
            flash('Complete Form', 'danger')
            return redirect(url_for('add_flight'))

        cur.execute("UPDATE flights SET date1=%s, date2=%s,departure_time=%s,arrival_time=%s,aircraftID=%s,linkID=%s WHERE flightID=%s", (date1, date2, time1, time2, aircraft, link,id))

        # Commit to DB
        connection.commit()

        # Close connection
        cur.close()

        flash('Flight updated succefuly', 'success')

        return redirect(url_for('profil'))


    return render_template('edit_flight.html',list_aircraft=list_aircrafts, list_link = list_link , edit_one = edit_one )


@app.route('/my-tickets')
@is_logged_in
def my_tickets():

    cur = connection.cursor()
    result = cur.execute("""
        SELECT t.* FROM tickets t
        LEFT JOIN clients c ON t.clients_clientID = c.clientID
        WHERE c.username=%s""",(session['username']))
        # Sort by date
        # Get aircraft type
        #
    tickets = cur.fetchall()
    cur.close()
    if result > 0:
        for t in tickets:
            #separate date / time
            pass
        return render_template('my-tickets.html',tickets=tickets)
        
    else:
        msg = "No tickets found"
        return render_template('my-tickets.html',msg = msg)

@app.route('/cancel/<ticketID>')
@is_logged_in
def cancel(ticketID):

    cur = connection.cursor()
    result = cur.execute("""
        DELETE FROM tickets
        WHERE ticketID = %s""",(ticketID))
    tickets = cur.fetchall()
    cur.close()
    if result > 0:
        msg = "Your ticket was successfully canceled"
        return render_template('my-tickets.html',tickets=tickets, msg = msg)
        
    else:
        msg = "No tickets found"
        return render_template('my-tickets.html',msg = msg)

    
@app.route('/add_employee', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def add_employee():


    # Create cursor
    cur = connection.cursor()

    cur.execute("SELECT * FROM role")
    data = cur.fetchall()
    list_role = list(data)

    if request.method == 'POST':
        # Get Form Fields
        firstname = request.form['firstname']
        surname = request.form['surname']
        address = request.form['address']
        salary = request.form['salary']
        flight_hours = request.form['flight_hours']
        social_security_number = request.form['social_security_number']

        # Create cursor
        cur = connection.cursor()
        
        try :
            role = request.form['role'].strip('()').split(',')[0]
            
        except:
            flash('Role missed', 'danger')
            return redirect(url_for('add_employee'))

        try:
            cur.execute("INSERT INTO employees(salary, address, firstname, surname, flight_hours, social_security_number, roleID) VALUES(%s, %s, %s, %s, %s, %s, %s)", (int(salary), address, firstname, surname, int(flight_hours), int(social_security_number), role))

        except :
            flash('Error, check the form fields', 'danger')
            return redirect(url_for('add_employee'))
            

        # Commit to DB
        connection.commit()

        # Close connection
        cur.close()

        flash('Employee added succefuly', 'success')

        return redirect(url_for('profil'))


    return render_template('add_employee.html',list_role = list_role)



@app.route('/add_role', methods=['GET', 'POST'])
@is_logged_in
@is_admin

def add_role():

    if request.method == 'POST':
        # Get Form Fields
        name = request.form['name']

        # Create cursor
        cur = connection.cursor()


        if name != '':
            cur.execute("INSERT INTO role(name) VALUES(%s)", (name))
        else:
            flash('Name mised', 'danger')
            return redirect(url_for('add_role'))

        # Commit to DB
        connection.commit()

        # Close connection
        cur.close()

        flash('Role added succefuly', 'success')

        return redirect(url_for('profil'))


    return render_template('add_role.html')
