from flask import Flask, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL
import yaml
import re

app = Flask(__name__)
db = yaml.load(open('db.yaml'), Loader=yaml.Loader)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

app.secret_key = "super secret key"

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        username = request.form['username']
        PASSWORD = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s",(username,PASSWORD))
        record = cur.fetchone()
        if record:
            session['loggedin'] = True
            session['username'] = record[1]
            flash("Login Successful")
            return redirect('/home')
        else:
            flash("Incorrect Password or Username")
            return redirect('/')

@app.route('/venlogin', methods=['GET', 'POST'])
def venlogin():
    if request.method=='POST':
        venname = request.form['venlogname']
        PASSWORD = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM vendor WHERE ven_name=%s AND password=%s",(venname,PASSWORD))
        record = cur.fetchone()
        if record:
            session['logedin'] = True
            session['ven_id'] = record[0]
            session['venlogname'] = record[1]
            flash("Login Successful")
            return redirect('/detail')
        else:
            flash("Incorrect Password or Username")
            return redirect('/')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register',methods=['GET','POST'])
def registerpage():
    if request.method == 'POST':
        #Fetch form data
        f = 0
        userDetails = request.form
        username = userDetails['username']
        mobileno = userDetails['mobileno']
        email = userDetails['email']
        password = userDetails['password']
        fname = userDetails['fname']
        lname = userDetails['lname']
        cur = mysql.connection.cursor()
        resultval = cur.execute("SELECT password FROM USERS")
        record = cur.fetchall()
        for row in record:
            if password == ''.join(row) or password == '':
                flash("Password Same")
                return render_template('register.html')
        if f==0:
            cur.execute("INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s, %s)",((resultval+1),username, email, password,fname,lname,mobileno))
            mysql.connection.commit()
            cur.close()
            session['username'] = username
            flash("Register Successful")
            return redirect('/home')
            
    return render_template('register.html')

@app.route('/venregister', methods=['GET','POST'])
def vendorregister():
    if request.method == 'POST':
        #Fetch form data
        f = 0
        userDetails = request.form
        venlogname = userDetails['venlogname']
        mobileno = userDetails['mobileno']
        email = userDetails['email']
        password = userDetails['password']
        name = userDetails['vendorname']
        cur = mysql.connection.cursor()
        resultval = cur.execute("SELECT password FROM vendor")
        record = cur.fetchall()
        for row in record:
            if password == ''.join(row) or password == '':
                f = 1
                flash("Password Same")
                return render_template('vendorregister.html')
        
        if f==0:
            cur.execute("INSERT INTO vendor VALUES (%s, %s, %s, %s, %s, %s)",((resultval+1), venlogname, mobileno, email, password, name))
            mysql.connection.commit()
            cur.close()
            session['ven_id'] = resultval+1
            session['venlogname'] = venlogname
            flash("Register Successful")
            return redirect('/detail')
            
    return render_template('vendorregister.html')

@app.route('/reservation', methods=['GET','POST'])
def reserve():
    if request.method == 'POST':
        #Fetch form data
        regex = ("^(([A-Z]{2}[0-9]{2})" +
             "( )|([A-Z]{2}-[0-9]" +
             "{2}))((19|20)[0-9]" +
             "[0-9])[0-9]{7}$")
        p = re.compile(regex)
        userDetails = request.form
        username = session['username']
        name = userDetails['name']
        email = userDetails['email']
        mobileno = userDetails['phone']
        location = userDetails['location']
        model_name = userDetails['model_name']
        lic_no = userDetails['lic_num']
        date = userDetails['date']
        if re.search(p, lic_no):
            cur = mysql.connection.cursor()
            resultval = cur.execute("SELECT * FROM RESERVATION")
            cur.execute("INSERT INTO RESERVATION VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", ((resultval+1), username, name, email, mobileno, location, model_name, date, lic_no))
            mysql.connection.commit()
            cur.close()
            session['req'] = date
            flash("Reservation Successful")
            return redirect('/table')
        else:
            flash('Invalid Licence Number')
            return redirect('/home')

    return render_template('reservation.html')

@app.route('/feedback', methods=['GET','POST'])
def feedback():
    if request.method == 'POST':
        #Fetch form data
        userDetails = request.form
        username = session['username']
        name = userDetails['name']
        email = userDetails['email']
        city = userDetails['city']
        description = userDetails['description']
        cur = mysql.connection.cursor()
        resultval = cur.execute("SELECT * FROM FEEDBACK")
        cur.execute("INSERT INTO FEEDBACK VALUES (%s, %s, %s, %s, %s, %s)", ((resultval+1), username, name, email, city, description))
        mysql.connection.commit()
        cur.close()
        return redirect('/home')

    return render_template('reservation.html')

@app.route('/home')
def home():
    return render_template('home.html',username=session['username'])

@app.route('/table', methods=['GET', 'POST'])
def table():
    date = session['req']
    cur = mysql.connection.cursor()
    resultVal = cur.execute("SELECT * FROM RESERVATION where req_date=%s",(str(date)))
    if resultVal > 0:
        userDetails = cur.fetchall()
        return render_template('reservetable.html', userDetail=userDetails)

@app.route('/detail', methods=['POST', 'GET'])
def detail():
    cursor = mysql.connection.cursor()
    id = session['ven_id']
    cursor.execute("SELECT * FROM BIKE_DES WHERE vendor_id = %s",(str(id)))
    data1 = cursor.fetchall()
    return render_template('venbikedetails.html', venlogname = session['venlogname'], data=data1)

@app.route('/bikelend', methods=['GET','POST'])
def lendbike():
    if request.method == 'POST':
        #Fetch form data
        id = session['ven_id']
        userDetails = request.form
        bikename = userDetails['bikename']
        biketype = userDetails['biketype']
        price = userDetails['price']
        image = userDetails['image']
        cur = mysql.connection.cursor()
        resultval = cur.execute("SELECT * FROM BIKE_DES")
        cur.execute("INSERT INTO BIKE_DES VALUES (%s, %s, %s, %s, %s, %s)", (id,(resultval+101), bikename, biketype, price, image))
        mysql.connection.commit()
        cur.close()
        flash("Display Successful")
        return redirect('/detail')

    return render_template('bikebook.html')

@app.route('/details')
def details():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM BIKE_DES')
    data1 = cursor.fetchall()
    return render_template('details.html', data=data1)

@app.route('/logout')
def logout():
    session.pop('logedin',None)
    session.pop('username',None)
    return redirect("/")

if __name__ == '__main__':
 
    # run() method of Flask class runs the application
    # on the local development server.
    app.run()