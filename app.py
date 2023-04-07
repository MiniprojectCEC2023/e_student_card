from flask import Flask, render_template, request, redirect, session, flash,jsonify
from flask_mysqldb import MySQL
import qrcode
from io import BytesIO
import PIL
from PIL import Image
from pyzbar.pyzbar import decode
import base64
import logging
import os
import math
from typing import List, Tuple
from mysql.connector import connect, Error
import binascii
from waitress import serve
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

@app.route('/update_info/<string:register_number>', methods=['POST'])
def update_info(register_number):
  books_available = request.form.get('books_available')
  # Update the student information in your database or data structure
  cur = mysql.connection.cursor()
  cur.execute('SELECT * FROM library WHERE register_number = %s', (register_number,))
  student = cur.fetchone()
  cur.execute('UPDATE library SET max_book = %s  WHERE register_number = %s', (books_available, register_number))
  mysql.connection.commit()
  cur.close()
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



@app.route('/lib_profile_qr', methods=['GET', 'POST'])
def lib_profile_qr():
    if request.method == 'POST':
        # Get the image data from the POST request
        image_data = request.form.get('image_data')
        if not image_data:
            flash('Invalid image data.')
            logging.warning('Invalid image data.')
            return redirect('/')
        try:
            # Add padding if necessary
            padding_length = 4 - len(image_data) % 4
            if padding_length == 4:
                padding_length = 0
            padding = b'=' * padding_length
            image_bytes = base64.b64decode(image_data.encode('utf-8') + padding)
        except binascii.Error as e:
            flash('Invalid base64-encoded image data.')
            logging.warning(f'Invalid base64-encoded image data: {e}')
            return redirect('/')

        # Open the image using PIL Image module
        try:
            image = Image.open(BytesIO(image_bytes))
            # Decode the QR code from the image
            qr_code = decode(image)
            # Get the register number from the QR code
            register_number = qr_code[0].data.decode('utf-8')

            # Get student's record from the database
            connection, cursor = connect_to_database()
            if not connection or not cursor:
                return "Error connecting to the database."
            cursor.execute('SELECT * FROM library WHERE register_number = %s', (register_number,))
            student = cursor.fetchone()
            connection.close()
            # Check if student exists
            if not student:
                flash('Student not found.')
                logging.warning('Student not found.')
                return redirect('/')

            # Render the template with the student's information and book details
            return render_template('librarian/lib_profile.html', student=student) 
        except PIL.UnidentifiedImageError as e:
            # return an error message to the user or log the error
            print(f"Error: {e}")
            return "Error: Invalid image file."

    # Render the template for scanning QR code
    return render_template('librarian/scan_qr_code.html')

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


@app.route('/update_infobus/<string:register_number>', methods=['POST'])
def update_infobus(register_number):
  fee_paid = request.form.get('fee_paid')
  # Update the student information in your database or data structure
  cur = mysql.connection.cursor()
  cur.execute('SELECT * FROM bus WHERE register_number = %s', (register_number,))
  student = cur.fetchone()
  cur.execute('UPDATE bus SET fee_paid = %s  WHERE register_number = %s', (fee_paid, register_number))
  mysql.connection.commit()
  cur.close()
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

    
mode='dev'
if __name__ == '__main__':
    if mode=='dev':
         app.run(host='127.0.0.1', port=5000,debug=True)
    else:
     serve(app, host='127.0.0.1', port=5000, threads=2, url_prefix="/cec")
