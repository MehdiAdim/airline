from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flaskext.mysql import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
#from passlib.hash import sha256_crypt
from functools import wraps
import datetime
from config import *


from .forms import RegisterForm
from .forms import EmployeeForm

app = Flask(__name__)

app.config.from_object('config')


mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = MYSQL_DATABASE_USER
app.config['MYSQL_DATABASE_PASSWORD'] = MYSQL_DATABASE_PASSWORD
app.config['MYSQL_DATABASE_DB'] = MYSQL_DATABASE_DB
app.config['MYSQL_DATABASE_HOST'] = MYSQL_DATABASE_HOST
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

        # Create cursor
        cur = connection.cursor()

        # Execute query
        cur.execute("""INSERT INTO clients(surname, firstname, email, username, address, password) 
            VALUES(%s, %s, %s, %s, %s, %s)""",
            (surname, firstname, email, username, adresse, password))

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
        result = cur.execute("""SELECT * 
            FROM clients
            WHERE username = %s AND password = %s""",
            (username, password_candidate))

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

@app.route('/edit/airport/<airportID>', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def edit_airport(airportID):
    cur = connection.cursor()
    if request.method == 'POST':
        # Get Form Fields
        name = request.form['name']
        code = request.form['code']
        city = request.form['city']

        if ( name == '' or code == '' or city ==''):
            flash('Missing fields', 'danger')
            return redirect(url_for('edit_airport', airportID=airportID ))
        try:    
            cur.execute(
                """UPDATE airports 
                SET name=%s, code=%s, city=%s
                WHERE airportID=%s""", (name, code, city, airportID))
        except:
            flash('Check fields format', 'danger')
            return redirect(url_for('edit_airport', airportID=airportID ))

        connection.commit()
        cur.close()

        flash('Airport edited succefuly', 'success')

        return redirect(url_for('airports'))

    cur.execute(
        """SELECT * FROM airports 
        WHERE airportID=%s""", (airportID))
    airport = cur.fetchone()
    return render_template('edit_airport.html', airport=airport)


@app.route('/airports', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def airports():


    cur = connection.cursor()
    result = cur.execute("SELECT * FROM airports")
    airports = cur.fetchall()
    first_time = True
    if request.method == 'POST':
        first_time = False
        # Get Form Fields
        name = request.form['name']
        code = request.form['code']
        city = request.form['city']

        if(name == '' or code == '' or city == ''):
            flash('Missing Fields', 'danger')
            return render_template('airports.html',airports=airports, first_time = first_time)
        
        cur = connection.cursor()
        try:
            cur.execute("INSERT INTO airports(name, code, city) VALUES(%s, %s, %s)", (name, code, city))
        except:
            flash('Check the fields format', 'danger')
            return render_template('airports.html',airports=airports, first_time = first_time)

        connection.commit()
        cur.close()

        flash('Airport added succefuly', 'success')

        return redirect(url_for('airports'))

    
    cur.close()
    if result > 0:
        return render_template('airports.html',airports=airports, first_time = first_time)
        
    
    else:
        msg = "No airports found"
        return render_template('airports.html',msg = msg,first_time =first_time)



@app.route('/edit/link/<linkID>', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def edit_link(linkID):

    cur = connection.cursor()
    if request.method == 'POST':
        # Get Form Fields
        departure = request.form['departure']
        arrival = request.form['arrival']

        cur.execute(
            """UPDATE links 
            SET departure_airportID=%s, arrival_airportID=%s
            WHERE linkID=%s""", (departure, arrival, linkID))
        connection.commit()
        cur.close()

        flash('Link edited succefuly', 'success')

        return redirect(url_for('links'))

    result = cur.execute(
        """SELECT * FROM links
        WHERE linkID=%s""", (linkID))
    link = cur.fetchone()
    cur.close()
    cur = connection.cursor()
    result = cur.execute("SELECT * FROM airports")
    airports = cur.fetchall()
    cur.close()
    return render_template('edit_link.html', link=link, airports=airports)


@app.route('/links', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def links():
    if request.method == 'POST':
        # Get Form Fields
        departure = request.form['departure']
        arrival = request.form['arrival']

        cur = connection.cursor()
        cur.execute("INSERT INTO links(departure_airportID, arrival_airportID) VALUES(%s, %s)",
            (departure, arrival))
        connection.commit()
        cur.close()
        print('ok')
        flash('Link added succefuly', 'success')

        return redirect(url_for('links'))

    cur = connection.cursor()
    result = cur.execute(
        """SELECT l.linkID, da.*, aa.*
        FROM links AS l
        LEFT JOIN airports AS da on da.airportID = l.departure_airportID
        LEFT JOIN airports AS aa on aa.airportID = l.arrival_airportID""")
    links = cur.fetchall()
    cur.close()
    print(links)
    cur = connection.cursor()
    result = cur.execute("SELECT * FROM airports")
    airports = cur.fetchall()
    cur.close()
    if result > 0:
        return render_template('links.html',links=links, airports=airports)
        
    
    else:
        msg = "No links found"
        return render_template('links.html',msg = msg)


@app.route('/aircrafts', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def aircrafts():

    cur = connection.cursor()
    result = cur.execute("SELECT * FROM aircrafts")
    aircrafts = cur.fetchall()
    first_time = True
    if request.method == 'POST':
        first_time = False
        # Get Form Fields
        immatriculation = request.form['immatriculation']
        aircraft_type = request.form['type']
        seats = request.form['seats']

        if(immatriculation=='' or aircraft_type=='' or seats==''):
            
            flash('Missing fields', 'danger')

            return render_template('aircrafts.html',aircrafts=aircrafts,first_time = first_time)
        

        cur = connection.cursor()
        try:
            cur.execute("INSERT INTO aircrafts(immatriculation, type, seats) VALUES(%s, %s, %s)",
                (immatriculation, aircraft_type, seats))
            connection.commit()
        except:
            flash('Check fields format', 'danger')

            return render_template('aircrafts.html',aircrafts=aircrafts,first_time = first_time)

        cur.close()

        flash('Aircraft added succefuly', 'success')

        return redirect(url_for('aircrafts'))

    
    cur.close()
    if result > 0:
        return render_template('aircrafts.html',aircrafts=aircrafts,first_time = first_time)
        
    
    else:
        msg = "No aircrafts found"
        return render_template('aircrafts.html',msg = msg, first_time = first_time)


@app.route('/edit/aircraft/<aircraftID>', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def edit_aircraft(aircraftID):
    cur = connection.cursor()
    if request.method == 'POST':
        # Get Form Fields
        immatriculation = request.form['immatriculation']
        aircraft_type = request.form['type']
        seats = request.form['seats']

        if (immatriculation =='' or aircraft_type == '' or seats ==''):
            flash('Missing fields', 'danger')
            return redirect(url_for('edit_aircraft',aircraftID = aircraftID))

        try:
            cur.execute(
                """UPDATE aircrafts 
                SET immatriculation=%s, type=%s, seats=%s
                WHERE aircraftID=%s""", (immatriculation, aircraft_type, seats, aircraftID))
        except:
            flash('Check the fields format', 'danger')
            return redirect(url_for('edit_aircraft',aircraftID = aircraftID))

        connection.commit()
        cur.close()

        flash('Aircraft edited succefuly', 'success')

        return redirect(url_for('aircrafts'))

    cur.execute(
        """SELECT * FROM aircrafts 
        WHERE aircraftID=%s""", (aircraftID))
    aircraft = cur.fetchone()
    return render_template('edit_aircraft.html', aircraft=aircraft)



@app.route('/flights', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def flights():

    first_time = True
    # Create cursor
    cur = connection.cursor()
    result = cur.execute("SELECT * FROM flights")
    flights = cur.fetchall()
    cur.close()
    
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
        first_time = False
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
            return render_template('flights.html',
                flights = flights,
                list_aircraft=list_aircrafts,
                list_link = list_link ,
                first_time=first_time)

        if date1 == '' or date2 == '' or time1 == '' or time2 == '':
            flash('Complete Form', 'danger')
            return render_template('flights.html',
                flights = flights,
                list_aircraft=list_aircrafts,
                list_link = list_link ,
                first_time = first_time)

        try:
            cur.execute("""INSERT INTO flights(date1, date2, departure_time, arrival_time, aircraftID, linkID)
                VALUES(%s, %s, %s, %s, %s, %s)""",
                (date1, date2, time1, time2, aircraft, link))
        except:
            flash('Check fields format', 'danger')
            return render_template('flights.html',
                flights = flights,
                list_aircraft=list_aircrafts,
                list_link = list_link,
                first_time=first_time)


        # Commit to DB
        connection.commit()

        # Close connection
        cur.close()

        flash('Flight added succefuly', 'success')

        return redirect(url_for('flights'))


    return render_template('flights.html',
        flights = flights,
        list_aircraft=list_aircrafts,
        list_link = list_link ,
        first_time=first_time)

    


@app.route('/edit/flight/<string:id>', methods=['GET', 'POST'])
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
            return redirect(url_for('edit_flight', id = id))

        print(aircraft)
        print(link)

        if date1 == '' or date2 == '' or time1 == '' or time2 == '':
            flash('Complete Form', 'danger')
            return redirect(url_for('edit_flight',id= id))
        try:
            cur.execute("""UPDATE flights
                SET date1=%s, date2=%s,departure_time=%s,arrival_time=%s,aircraftID=%s,linkID=%s WHERE flightID=%s""",
                (date1, date2, time1, time2, aircraft, link,id))
        except:
            flash('Check fields format', 'danger')
            return redirect(url_for('edit_flight',id= id))
        # Commit to DB
        connection.commit()

        # Close connection
        cur.close()

        flash('Flight updated succefuly', 'success')

        return redirect(url_for('flights'))


    return render_template('edit_flight.html',
        list_aircraft=list_aircrafts,
        list_link = list_link,
        edit_one = edit_one)


def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    if d["hours"] > 12:
        d["hours"] -= 12
        d["AMPM"] = "PM"
    else:
        d["AMPM"] = "AM"
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


@app.route('/my-tickets')
@is_logged_in
def my_tickets():

    cur = connection.cursor()
    result = cur.execute("""
        SELECT t.ticketID, t.date_of_issue, t.price,
            f.departure_time, f.arrival_time,
            d.departure_date,
            da.*, aa.*
        FROM tickets t
        LEFT JOIN departures d ON d.departureID = t.departureID
        LEFT JOIN flights f ON f.flightID = d.flightID
        LEFT JOIN links l ON l.linkID = f.linkID
        LEFT JOIN airports da ON da.airportID = l.departure_airportID
        LEFT JOIN airports aa ON aa.airportID = l.arrival_airportID
        LEFT JOIN clients c ON t.clientID = c.clientID
        WHERE c.username=%s""",(session['username']))
        # Sort by date
        # Get aircraft type
        #
    tickets = cur.fetchall()
    cur.close()
    formated_tickets = []
    for t in tickets:
        ticket = {
            'ticketID': t[0],
            'date_of_issue': t[1],
            'price': t[2],
            'departure_time': strfdelta(t[3], "{hours:0>2d}:{minutes:0>2d} {AMPM}"),
            'arrival_time': strfdelta(t[4], "{hours:0>2d}:{minutes:0>2d} {AMPM}"),
            'departure_date': t[5],
            'departure_airport':{
                'name': t[7],
                'code': t[8],
                'city': t[9],
            },
            'arrival_airport':{
                'name': t[11],
                'code': t[12],
                'city': t[13],
            }
        }
        formated_tickets.append(ticket)

    if result > 0:
        for t in tickets:
            #separate date / time
            pass
        return render_template('my-tickets.html',tickets=formated_tickets)
        
    else:
        msg = "No tickets found"
        return render_template('my-tickets.html',msg = msg)

@app.route('/cancel/<ticketID>')
@is_logged_in
def cancel(ticketID):

    cur = connection.cursor()
    cur.execute("""
        DELETE FROM tickets
        WHERE ticketID = %s""",(ticketID))
    connection.commit()
    tickets = cur.fetchall()
    cur.close()
     
    flash("Your ticket was successfully canceled", 'success')
    return redirect(url_for('my_tickets'))


@app.route('/edit/role/<roleID>', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def edit_role(roleID):

    cur = connection.cursor()
    if request.method == 'POST':
        # Get Form Fields
        name = request.form['name']

        cur.execute(
            """UPDATE role 
            SET name=%s
            WHERE roleID=%s""", (name, roleID))
        connection.commit()
        cur.close()

        flash('Role edited succefuly', 'success')

        return redirect(url_for('roles'))

    cur.execute(
        """SELECT * FROM role
        WHERE roleID=%s""", (roleID))
    role = cur.fetchone()
    return render_template('edit_role.html', role=role)


@app.route('/roles', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def roles():

    first_time = True
    cur = connection.cursor()
    result = cur.execute("SELECT * FROM role")
    roles = cur.fetchall()
    cur.close()
    
    
    if request.method == 'POST':
        first_time = False
        # Get Form Fields
        name = request.form['role']

        if name == '':

            flash("Role's name missing", 'danger')

            return render_template('roles.html',roles=roles, first_time = first_time)

        cur = connection.cursor()
        cur.execute("INSERT INTO role(name) VALUES(%s)", (name))
        connection.commit()
        cur.close()

        flash('Role added succefuly', 'success')

        return redirect(url_for('roles'))

    if result > 0:
        return render_template('roles.html',roles=roles, first_time = first_time)
        
    else:
        msg = "No roles found"
        return render_template('roles.html',msg = msg, first_time = first_time)

    


@app.route('/employees', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def employees():

    cur = connection.cursor()
    result = cur.execute("SELECT * FROM role")
    roles = cur.fetchall()
    cur.close()

    form = EmployeeForm(request.form)
    form.role.choices = roles

    first_time = True

    if request.method == 'POST' :
        first_time = False

        if  form.validate():
            firstname = form.firstname.data
            surname = form.surname.data
            address = form.address.data
            salary = form.salary.data
            flight_hours = form.flight_hours.data
            social_security_number = form.social_security_number.data
            role = form.role.data
            
            cur = connection.cursor()
            cur.execute("""INSERT INTO employees(salary, address, firstname, surname, flight_hours, social_security_number, roleID)
                VALUES(%s, %s, %s, %s, %s, %s, %s)""",
                (salary, address, firstname, surname, flight_hours, social_security_number, role))
            connection.commit()
            cur.close()

            flash('Employee added succefuly', 'success')

            return redirect(url_for('employees'))


    cur = connection.cursor()
    result = cur.execute("""SELECT *
        FROM employees
        LEFT JOIN role on role.roleID = employees.roleID""")
    employees = cur.fetchall()
    cur.close()
    if result > 0:
        return render_template('employees.html',employees=employees, form=form, first_time = first_time)
        
    else:
        msg = "No employees found"
        return render_template('employees.html',msg = msg, form=form, first_time = first_time)


@app.route('/edit/employee/<id>', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def edit_employee(id):
    if request.method == 'POST':
        # Get Form Fields
        firstname = request.form['firstname']
        surname = request.form['surname']
        address = request.form['address']
        salary = request.form['salary']
        flight_hours = request.form['flight_hours']
        social_security_number = request.form['social_security_number']
        role_name = request.form['role']

        cur = connection.cursor()
        cur.execute("Select roleID FROM role WHERE name = %s",(role_name))
        id_role = cur.fetchone()[0]


        if (firstname == '' or surname == '' or address== '' or  salary=='' or flight_hours == '' or social_security_number==''):
            
            flash('Missing fields', 'danger')
            return redirect(url_for('edit_employee',id=id))
        try :
            cur.execute("""UPDATE employees 
                SET firstname=%s, surname=%s,address=%s,salary=%s,flight_hours=%s,social_security_number=%s, roleID=%s WHERE employeeID=%s""", 
                (firstname, surname, address, salary, flight_hours, social_security_number,id_role,id))
            connection.commit()        
        except :
            flash('Error in fields', 'danger')
            return redirect(url_for('edit_employee',id=id))

        cur.close()

        flash('Employee edited succefuly', 'success')

        return redirect(url_for('employees'))
    

    

    cur = connection.cursor()
    result = cur.execute("""SELECT *
        FROM employees
        LEFT JOIN role on role.roleID = employees.roleID
        WHERE employeeID = %s""",(id))
    
    employee = cur.fetchone()

    result = cur.execute("""SELECT *
        FROM role""")
    roles = cur.fetchall()


    return render_template('edit_employee.html', employee = employee, roles = roles)

@app.route('/departures', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def departures():
    cur = connection.cursor()
    cur.execute("""SELECT employeeID,firstname,surname
    FROM employees
    left join role on employees.roleID = role.roleID
    WHERE role.name = "pilot" """)
    pilots = cur.fetchall()
    cur.execute("""SELECT employeeID,firstname,surname
    FROM employees
    left join role on employees.roleID = role.roleID
    WHERE role.name = "crew" """)
    crews = cur.fetchall()
    cur.execute(""" SELECT * FROM flights""")
    flights = cur.fetchall()
    result = cur.execute("SELECT * FROM departures")
    departures = cur.fetchall()
    

    first_time = True

    if request.method == 'POST' :
        first_time = False

        departure_date = request.form['departure_date']
        free_seats = request.form['free_seats']
        sold_seats = request.form['sold_seats']
        
        try:
            flight = request.form['flight']
            pilot1 = request.form['pilot1']
            pilot2 = request.form['pilot2']
            crew1 = request.form['crew1']
            crew2 = request.form['crew2']
        except:
            flash('Missing fields', 'danger')

            return render_template('departures.html',
                pilots=pilots,
                crews=crews,
                flights=flights,
                departures=departures,
                first_time=first_time)

        if(departure_date =='' or free_seats=='' or sold_seats==''):
            flash('Missing fields', 'danger')

            return render_template('departures.html',
                pilots=pilots,
                crews=crews,
                flights=flights,
                departures=departures,
                first_time=first_time)

        cur = connection.cursor()

        try:
            cur.execute("""INSERT INTO departures(departure_date, free_seats, sold_seats, flightID, pilot1ID, pilot2ID, crew_member1ID, crew_member2ID)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s)""",
                (departure_date, free_seats, sold_seats, flight, pilot1, pilot2, crew1,crew2))
        except :
            
            flash('Check the fields format', 'danger')

            return render_template('departures.html',
                pilots=pilots,
                crews=crews,
                flights=flights,
                departures=departures,
                first_time=first_time)

        connection.commit()

        cur.close()

        flash('Departure added succefuly', 'success')

        return redirect(url_for('departures'))


    
    if result > 0:
        return render_template('departures.html',
            pilots=pilots,
            crews=crews,
            flights=flights,
            departures=departures,
            first_time=first_time)
        
    else:
        msg = "No departure found"
        return render_template('departures.html',
            pilots=pilots,
            crews=crews,
            flights=flights,
            first_time=first_time)
    cur.close()



@app.route('/edit/departure/<id>', methods=['GET', 'POST'])
@is_logged_in
@is_admin
def edit_departure(id):
    cur = connection.cursor()
    cur.execute("SELECT * FROM departures where departureID=%s",(id))
    departure = cur.fetchone()
    
    cur = connection.cursor()
    cur.execute("""SELECT employeeID,firstname,surname
    FROM employees
    LEFT JOIN role on employees.roleID = role.roleID
    WHERE role.name = "pilot" """)
    pilots = cur.fetchall()
    cur.execute("""SELECT employeeID,firstname,surname
    FROM employees
    LEFT JOIN role on employees.roleID = role.roleID
    WHERE role.name = "crew" """)
    crews = cur.fetchall()
    cur.execute("""SELECT flightID FROM flights""")
    flights = cur.fetchall()

    if request.method == 'POST':
        # Get Form Fields
        departure_date = request.form['departure_date']
        free_seats = request.form['free_seats']
        sold_seats = request.form['sold_seats']
        
        try:
            flight = request.form['sold_seats'][1]
            pilot1 = request.form['pilot1'][1]
            pilot2 = request.form['pilot2'][1]
            crew1 = request.form['crew1'][1]
            crew2 = request.form['crew2'][1]
        except:
            flash('Missing fields', 'danger')

            return redirect(url_for('edit_departure',id=id))


        if(departure_date =='' or free_seats=='' or sold_seats==''):
            flash('Missing Fields', 'danger')
            return redirect(url_for('edit_departure',id=id))

        try :
            cur.execute("UPDATE departures SET departure_date=%s, free_seats=%s,sold_seats=%s,flightID=%s,pilot1ID=%s,pilot2ID=%s, crew_member1ID=%s,crew_member2ID=%s WHERE departureID=%s", 
                    (departure_date, free_seats, sold_seats, flight, pilot1, pilot2,crew1,crew2,id))
        except :
            flash('Error in fields', 'danger')
            return redirect(url_for('edit_departures',id=id))
            


        cur.close()

        flash('Departure edited succefuly', 'success')

        return redirect(url_for('departures'))
    
    return render_template('edit_departure.html', departure = departure, flights=flights, pilots=pilots)



@app.route('/search-flight', methods=['GET', 'POST'])
@is_logged_in
def search_flight():
    cur = connection.cursor()
    cur.execute("SELECT DISTINCT city FROM airports")
    cities = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        # Get Form Fields
        departure_city = request.form['departure_city']
        arrival_city = request.form['arrival_city']
        print(departure_city)
        print(arrival_city)
        cur = connection.cursor()
        result = cur.execute("""
            SELECT f.departure_time, f.arrival_time,
                d.departure_date,
                da.*, aa.*,
                d.departureID
            FROM departures d
            LEFT JOIN flights f ON f.flightID = d.flightID
            LEFT JOIN links l ON l.linkID = f.linkID
            LEFT JOIN airports da ON da.airportID = l.departure_airportID
            LEFT JOIN airports aa ON aa.airportID = l.arrival_airportID
            WHERE da.city=%s AND aa.city=%s""",(departure_city, arrival_city))


        departures = cur.fetchall()

        formated_departures = []
        for d in departures:
            departure = {
                'departureID': d[11],
                'price': 555,
                'departure_time': strfdelta(d[0], "{hours:0>2d}:{minutes:0>2d} {AMPM}"),
                'arrival_time': strfdelta(d[1], "{hours:0>2d}:{minutes:0>2d} {AMPM}"),
                'departure_date': d[2],
                'departure_airport':{
                    'name': d[4],
                    'code': d[5],
                    'city': d[6],
                },
                'arrival_airport':{
                    'name': d[8],
                    'code': d[9],
                    'city': d[10],
                }
            }
            formated_departures.append(departure)
        
        cur.close()
        
        if result > 0:
            return render_template('search-flight.html',
                cities = sorted(cities),
                departures=formated_departures,
                departure=departure_city,
                arrival=arrival_city)
        else:
            msg = "No flights were found"
            return render_template('search-flight.html',
                cities = sorted(cities),
                msg=msg,
                departure=departure_city,
                arrival=arrival_city)

    return render_template('search-flight.html', cities = sorted(cities))

@app.route('/book/<departureID>', methods=['GET'])
@is_logged_in
def book(departureID):
    cur = connection.cursor()
    
    cur.execute("""SELECT clientID FROM clients c
        WHERE c.username=%s""",(session['username']))
    clientID = cur.fetchone()

    cur.execute("""INSERT INTO tickets(date_of_issue, price, departureID, clientID)
        VALUES(%s, %s, %s, %s)""",
        (datetime.datetime.now(), 555, departureID, clientID))
        
    connection.commit()
    cur.close()

    flash('Ticket was booked succefuly', 'success')

    return redirect(url_for('my_tickets'))