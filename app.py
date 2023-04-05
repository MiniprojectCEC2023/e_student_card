from flask import Flask, render_template, request, redirect, session, flash,jsonify
import logging
from flask_mysqldb import MySQL
import os
import qrcode
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode
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

################################################################
#----------------------------INDEX-----------------------------#
################################################################


#INDEX_ROUTE
@app.route('/')
def home():
    return render_template('index.html')




################################################################
#----------------------------ADMIN-----------------------------#
################################################################


#Route to get admin login page and login to admin dashboard
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
            return render_template('admin/admin-login.html')
    else:
        return render_template('admin/admin-login.html')

#Route to get admin dashboard
@app.route('/admin-dashboard')
def admin_dashboard():
    if session.get('username') == 'admin':
        return render_template('admin/admin-dashboard.html')
    else:
        error = 'You need to log in as admin first.'
        flash(error)
        logging.warning(error)
        return redirect('/admin-login')


#Route to get register form page
@app.route('/register')
def registers():
    return render_template('admin/register.html')

#Route to submit registration form
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
            return render_template('admin/register.html')

        # Insert data into the database
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM student WHERE email = %s OR register_number = %s', (email, register_number))
        result = cur.fetchone()
        if result:
            error = 'Email or register number already exists'
            flash(error)
            logging.warning(error)
            return render_template('admin/register.html')

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
        return render_template('admin/register.html')

#Route to return registration success message
@app.route("/register-success")
def success():
    return "Registration successful!"

#Route for students viewing for admin
@app.route('/view-students')
def view_students():
    if session.get('username') == 'admin':
        cur = mysql.connection.cursor()
        cur.execute('SELECT name, email, register_number,semester FROM student')
        students = cur.fetchall()
        cur.close()
        return render_template('admin/view-students.html', students=students)
    else:
        error = 'You need to log in as admin first.'
        flash(error)
        logging.warning(error)
        return redirect('/admin-login')

#Route to update semester of students by admin
@app.route('/edit-student/<register_number>', methods=['GET', 'POST'])
def edit_student(register_number):
    if session.get('username') == 'admin':
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM student WHERE register_number = %s', (register_number,))
        student = cur.fetchone()
        cur.close()
        if request.method == 'POST':
            semester = request.form['semester']
            cur = mysql.connection.cursor()
            cur.execute('UPDATE student SET semester = %s WHERE register_number = %s', (semester, register_number,))
            mysql.connection.commit()
            cur.close()
            flash('Student record updated successfully')
            return redirect('/view-students')
        return render_template('admin/edit-student.html', student=student)
    else:
        error = 'You need to log in as admin first.'
        flash(error)
        logging.warning(error)
        return redirect('/admin-login') 

     
#Route to delete  students by admin
@app.route('/delete-student/<register_number>', methods=['GET'])
def delete_student(register_number):
    if session.get('username') == 'admin':
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM student WHERE register_number = %s', (register_number,))
        mysql.connection.commit()
        cur.close()
        flash('Student record deleted successfully')
        return redirect('/view-students')
    else:
        error = 'You need to log in as admin first.'
        flash(error)
        logging.warning(error)
        return redirect('/admin-login')



################################################################
#----------------------------LIBRARY---------------------------#
################################################################

#Route to get librarian login page and login to librarian dashboard
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
            return render_template('librarian/librarian-login.html')
    else:
        return render_template('librarian/librarian-login.html')


#Route to get library dashboard
@app.route('/librarian-dashboard')
def librarian_dashboard():
    if session.get('username') == 'library':
        return render_template('librarian/librarian-dashboard.html')
    else:
        error = 'You need to log in as librarian first.'
        flash(error)
        logging.warning(error)
        return redirect('/librarian-login')


#Route for viewing student who does not register with library by librarian
@app.route('/view-std-lib')
def view_std_lib():
    if session.get('username') == 'library':
        cur = mysql.connection.cursor()
        cur.execute('SELECT name, email, register_number, semester FROM student WHERE added_to_library = FALSE')
        students = cur.fetchall()
        cur.close()
        return render_template('librarian/view-std-lib.html', students=students)
    else:
        error = 'You need to log in as libraruan first.'
        flash(error)
        logging.warning(error)
        return redirect('/librarian-login')


#Rouute for adding students to library
@app.route('/add_lib/<register_number>', methods=['GET'])
def add_to_lib(register_number):
    if session.get('username') == 'library':
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO library (id, name, email, semester, branch, register_number, qr_code, max_book) SELECT id, name, email, semester, branch, register_number, qr_code, 4 FROM student WHERE register_number = %s', (register_number,))
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


#Route to view registered students in library
@app.route('/reg_lib')
def reg_lib():
    if session.get('username') == 'library':
        cur = mysql.connection.cursor()
        cur.execute('SELECT name, email, register_number,semester FROM library')
        students = cur.fetchall()
        cur.close()
        return render_template('librarian/reg_lib.html', students=students)
    else:
        error = 'You need to log in as librarian first.'
        flash(error)
        logging.warning(error)
        return redirect('/librarian-login')


#Route to view each library profile of students
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
 
    # Render the template with the student's information and book details
    return render_template('librarian/lib_profile.html', student=student)


#Route to delete library profile
@app.route('/delete-std-lib/<register_number>', methods=['GET'])
def delete_std_lib(register_number):
    if session.get('username') == 'library':
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM library WHERE register_number = %s', (register_number,))
        cur.execute('UPDATE student SET added_to_library = FALSE WHERE register_number = %s', (register_number,))
        mysql.connection.commit()
        cur.close()
        flash('Student record deleted successfully')
        return redirect('/reg_lib')
    else:
        error = 'You need to log in as librarian first.'
        flash(error)
        logging.warning(error)
        return redirect('/librarian-login')

################################################################
################################################################

################################################################
################################################################
@app.route('/scan_qrcode/<string:qrcode_data>')
def scan_qrcode(qrcode_data):
    # Get student's record from the database
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM library WHERE qrcode_data = %s', (qrcode_data,))
    student = cur.fetchone()
    cur.close()
    # Check if student exists
    if not student:
        flash('Student not found.')
        logging.warning('Student not found.')
        return redirect('/')
 
    # Render the template with the student's information and book details
    return render_template('librarian/lib_profile.html', student=student)

@app.route('/camera')
def camera():
    return render_template('librarian/camera.html')

# Route to handle the QR code scan
@app.route("/scan_result", methods=["POST"])
def scan_qr_code():
    # Get the QR code image from the request
    qr_code_img = request.files["qr_code"]

    # Decode the QR code image
    qr_code_data = decode(Image.open(qr_code_img))[0].data.decode()

    # Retrieve the student information from the database
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM student WHERE register_number = %s', (qr_code_data,))
    student = cur.fetchone()
    cur.close()

    # Render the student information page
    return render_template("librarian/scan_result.html", student=student)

################################################################
################################################################

################################################################
################################################################



################################################################
#----------------------------OFFICE----------------------------#
################################################################


#Route to get office login page and login to office dashboard
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
            return render_template('office/college-office-login.html')
    else:
        return render_template('office/college-office-login.html')


#Route to get office dashboard
@app.route('/college-office-dashboard')
def college_office_dashboard():
    if session.get('username') == 'office':
        return render_template('office/college-office-dashboard.html')
    else:
        error = 'You need to log in as college office first.'
        flash(error)
        logging.warning(error)
        return redirect('/college-office-login')


#Route for viewing student who does not register for college bus by office
@app.route('/view-std-bus')
def view_std_bus():
    if session.get('username') == 'office':
        cur = mysql.connection.cursor()
        cur.execute('SELECT name, email, register_number, semester FROM student WHERE added_to_bus = FALSE')
        students = cur.fetchall()
        cur.close()
        return render_template('office/view-std-bus.html', students=students)
    else:
        error = 'You need to log in as  office first.'
        flash(error)
        logging.warning(error)
        return redirect('/college-office-login')


#Rouute for adding students for college bus
@app.route('/add_bus/<register_number>', methods=['GET'])
def add_to_bus(register_number):
    if session.get('username') == 'office':
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO bus (id, name, email, semester, branch, register_number, qr_code, fee_paid) SELECT id, name, email, semester, branch, register_number, qr_code, 0 FROM student WHERE register_number = %s', (register_number,))
        cur.execute('UPDATE student SET added_to_bus = TRUE WHERE register_number = %s', (register_number,))
        mysql.connection.commit()
        cur.close()
        flash('Student record added to office successfully')
        return redirect('/view-std-bus')
    else:
        error = 'You need to log in as office first.'
        flash(error)
        logging.warning(error)
        return redirect('/college-office-login')


#Route to view registered students for college bus
@app.route('/reg_bus')
def reg_bus():
    if session.get('username') == 'office':
        cur = mysql.connection.cursor()
        cur.execute('SELECT name, email, register_number,semester FROM bus')
        students = cur.fetchall()
        cur.close()
        return render_template('office/reg_bus.html', students=students)
    else:
        error = 'You need to log in as office first.'
        flash(error)
        logging.warning(error)
        return redirect('/college-office-login')


#Route to view each college bus profile of students
@app.route('/bus_profile/<string:register_number>')
def bus_profile(register_number):
    # Get student's record from the database
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM bus WHERE register_number = %s', (register_number,))
    student = cur.fetchone()
    cur.close()
    # Check if student exists
    if not student:
        flash('Student not found.')
        logging.warning('Student not found.')
        return redirect('/')
 
    # Render the template with the student's information and book details
    return render_template('office/bus_profile.html', student=student)


#Route to delete college bus profile
@app.route('/delete-std-bus/<register_number>', methods=['GET'])
def delete_std_bus(register_number):
    if session.get('username') == 'office':
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM bus WHERE register_number = %s', (register_number,))
        cur.execute('UPDATE student SET added_to_bus = FALSE WHERE register_number = %s', (register_number,))
        mysql.connection.commit()
        cur.close()
        flash('Student record deleted successfully')
        return redirect('/reg_bus')
    else:
        error = 'You need to log in as office first.'
        flash(error)
        logging.warning(error)
        return redirect('/college-office-login')

################################################################
#----------------------------LOGOUT----------------------------#
################################################################


#Route for logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
