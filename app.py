from flask import Flask, render_template, request, redirect, session
from myapp import create_app

app = create_app()
app.secret_key = 'your_secret_key_here'
@app.route('/')
def home():

    return render_template('index.html')

# Define routes for the login pages for each user type
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'a1234':
            session['username'] = username
            return redirect('/admin-dashboard')
        else:
            return render_template('admin-login.html', error='Invalid username or password')
    else:
        return render_template('admin-login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/librarian-login', methods=['GET', 'POST'])
def librarian_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'library' and password == 'l1234':
            session['username'] = username
            return redirect('/librarian-dashboard')
        else:
            return render_template('librarian-login.html', error='Invalid username or password')
    else:
        return render_template('librarian-login.html')

@app.route('/college-office-login', methods=['GET', 'POST'])
def college_office_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'office' and password == 'o1234':
            session['username'] = username
            return redirect('/college-office-dashboard')
        else:
            return render_template('college-office-login.html', error='Invalid username or password')
    else:
        return render_template('college-office-login.html')

# Define the dashboard routes for each user type
@app.route('/admin-dashboard')
def admin_dashboard():
    if 'username' in session and session['username'] == 'admin':
        return render_template('admin-dashboard.html')
    else:
        return redirect('/admin-login')

@app.route('/librarian-dashboard')
def librarian_dashboard():
    if 'username' in session and session['username'] == 'library':
        return render_template('librarian-dashboard.html')
    else:
        return redirect('/librarian-login')

@app.route('/college-office-dashboard')
def college_office_dashboard():
    if 'username' in session and session['username'] == 'office':
        return render_template('college-office-dashboard.html')
    else:
        return redirect('/college-office-login')

# Define a logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
