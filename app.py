from flask import Flask, render_template, request, redirect, session, flash
import logging
from flask_mysqldb import MySQL
import os
import qrcode
from io import BytesIO

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'shibanMySQL1234@DB'
app.config['MYSQL_DB'] = 'mini'

mysql = MySQL(app)


# Define 


#INDEX_ROUTE
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'a1234':
            session['username'] = username
            return redirect('/admin-dashboard')
        else:
            error = 'Invalid username or password'
            flash(error)
            logging.warning(error)
            return render_template('admin-login.html')
    else:
        return render_template('admin-login.html')



@app.route('/register')
def registers():
    return render_template('register.html')


@app.route("/register-success", methods=["POST"])
def register():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        register_number = request.form.get("register_number")
        phone = request.form.get("phone")
        address = request.form.get("address")
        dob = request.form.get("dob")
        gender = request.form.get("gender")
        branch = request.form.get("branch")
        semester = request.form.get("semester")
        
        # Check if all required fields are filled
        if not name or not email or not register_number or not phone or not address or not dob or not gender or not branch or not semester:
            error = 'All fields are required'
            flash(error)
            logging.warning(error)
            return render_template('register.html')

        # Insert data into the database
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM student WHERE email = %s OR register_number = %s', (email, register_number))
        result = cur.fetchone()
        if result:
            error = 'Email or register number already exists'
            flash(error)
            logging.warning(error)
            return render_template('register.html')

        # Generate the QR code
        data = f"Name: {name}, Email: {email}, Register Number: {register_number}"
        qr = qrcode.make(data)
        img = BytesIO()
        qr.save(img, "PNG")
        img.seek(0)

        # Insert data and QR code image into the database
        cur.execute('INSERT INTO student (name, email, register_number, phone, address, dob, gender, branch, semester, qr_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (name, email, register_number, phone, address, dob, gender, branch, semester, img.read()))
        mysql.connection.commit()
        

        # Save QR code as PNG image in specified folder
        qr_img_path = f"static/qr_codes/{register_number}.png"
        with open(qr_img_path, 'wb') as f:
            f.write(img.getbuffer())

        cur.close()
        flash('Registration successful. Please log in.')
        return redirect('/register-success')
    else:
        return render_template('register.html')


@app.route("/register-success")
def success():
    return "Registration successful!"



@app.route('/librarian-login', methods=['GET', 'POST'])
def librarian_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'library' and password == 'l1234':
            session['username'] = username
            return redirect('/librarian-dashboard')
        else:
            error = 'Invalid username or password'
            flash(error)
            logging.warning(error)
            return render_template('librarian-login.html')
    else:
        return render_template('librarian-login.html')



@app.route('/college-office-login', methods=['GET', 'POST'])
def college_office_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'office' and password == 'o1234':
            session['username'] = username
            return redirect('/college-office-dashboard')
        else:
            error = 'Invalid username or password'
            flash(error)
            logging.warning(error)
            return render_template('college-office-login.html')
    else:
        return render_template('college-office-login.html')



@app.route('/admin-dashboard')
def admin_dashboard():
    if session.get('username') == 'admin':
        return render_template('admin-dashboard.html')
    else:
        error = 'You need to log in as admin first.'
        flash(error)
        logging.warning(error)
        return redirect('/admin-login')



@app.route('/librarian-dashboard')
def librarian_dashboard():
    if session.get('username') == 'library':
        return render_template('librarian-dashboard.html')
    else:
        error = 'You need to log in as librarian first.'
        flash(error)
        logging.warning(error)
        return redirect('/librarian-login')



@app.route('/college-office-dashboard')
def college_office_dashboard():
    if session.get('username') == 'office':
        return render_template('college-office-dashboard.html')
    else:
        error = 'You need to log in as college office first.'
        flash(error)
        logging.warning(error)
        return redirect('/college-office-login')
    


@app.route('/view-students')
def view_students():
    if session.get('username') == 'admin':
        cur = mysql.connection.cursor()
        cur.execute('SELECT name, email, register_number,semester FROM student')
        students = cur.fetchall()
        cur.close()
        return render_template('view-students.html', students=students)
    else:
        error = 'You need to log in as admin first.'
        flash(error)
        logging.warning(error)
        return redirect('/admin-login')
    


@app.route('/delete-student/<register_number>', methods=['GET'])
def delete_student(register_number):
    if session.get('username') == 'admin':
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM student WHERE register_number = %s', (register_number,))
        cur.execute('DELETE FROM library WHERE register_number = %s', (register_number,))
        mysql.connection.commit()
        cur.close()
        flash('Student record deleted successfully')
        return redirect('/view-students')
    else:
        error = 'You need to log in as admin first.'
        flash(error)
        logging.warning(error)
        return redirect('/admin-login')


@app.route('/edit-student/<register_number>', methods=['GET', 'POST'])
def edit_student(register_number):
    if session.get('username') == 'admin':
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM student WHERE register_number = %s', (register_number,))
        cur.execute('SELECT * FROM library WHERE register_number = %s', (register_number,))
        student = cur.fetchone()
        cur.close()
        if request.method == 'POST':
            semester = request.form['semester']
            cur = mysql.connection.cursor()
            cur.execute('UPDATE student SET semester = %s WHERE register_number = %s', (semester, register_number,))
            cur.execute('UPDATE library SET semester = %s WHERE register_number = %s', (semester, register_number,))
            mysql.connection.commit()
            cur.close()
            flash('Student record updated successfully')
            return redirect('/view-students')
        return render_template('edit-student.html', student=student)
    else:
        error = 'You need to log in as admin first.'
        flash(error)
        logging.warning(error)
        return redirect('/admin-login') 

@app.route('/view-std-lib')
def view_std_lib():
    if session.get('username') == 'library':
        cur = mysql.connection.cursor()
        cur.execute('SELECT name, email, register_number, semester FROM student WHERE added_to_library = FALSE')
        students = cur.fetchall()
        cur.close()
        return render_template('view-std-lib.html', students=students)
    else:
        error = 'You need to log in as libraruan first.'
        flash(error)
        logging.warning(error)
        return redirect('/librarian-login')



@app.route('/add_lib/<register_number>', methods=['GET'])
def add_to_lib(register_number):
    if session.get('username') == 'library':
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO library SELECT * FROM student WHERE register_number = %s', (register_number,))
        cur.execute('UPDATE student SET added_to_library = TRUE WHERE register_number = %s', (register_number,))
        mysql.connection.commit()
        cur.close()
        flash('Student record added to library successfully')
        return redirect('/view-std-lib')
    else:
        error = 'You need to log in as librarian first.'
        flash(error)
        logging.warning(error)
        return redirect('/librarian-login')


@app.route('/reg_lib')
def reg_lib():
    if session.get('username') == 'library':
        cur = mysql.connection.cursor()
        cur.execute('SELECT name, email, register_number,semester FROM library')
        students = cur.fetchall()
        cur.close()
        return render_template('reg_lib.html', students=students)
    else:
        error = 'You need to log in as librarian first.'
        flash(error)
        logging.warning(error)
        return redirect('/librarian-login')

@app.route('/lib_profile/<string:register_number>')
def lib_profile(register_number):
    # Get student's record from the database
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM library WHERE register_number = %s', (register_number,))
    student = cur.fetchone()
    cur.close()

    # Check if student exists
    if not student:
        flash('Student not found.')
        logging.warning('Student not found.')
        return redirect('/')

    # Render the template with the student's information
    return render_template('lib_profile.html', student=student)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')



if __name__ == '__main__':
    app.run(debug=True)
