from flask import Flask, render_template, request, redirect, url_for, session, flash
from mysql.connector import connect, Error
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a strong secret key

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'vishnu@123',
    'database': 'auth',
    'auth_plugin': 'mysql_native_password'  # Ensure MySQL 8+ compatibility
}
def get_db_connection():
    """Establish a connection to the MySQL database."""
    try:
        return connect(**db_config)
    except Error as e:
        print(f"Database Connection Error: {e}")
        return None

@app.route('/')
def home():
    """Home route displaying logged-in user details."""
    if 'email' in session:
        return f'Logged sucssfully completed as {session["email"]}'
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        if not username or not email or not password:
            flash('All fields are required!', 'warning')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed!', 'danger')
            return redirect(url_for('register'))

        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                (username, email, hashed_password)
            )
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Error as e:
            if e.errno == 1062:  # Duplicate entry error (MySQL Error Code)
                flash('Email already exists!', 'danger')
            else:
                flash('Registration failed! Please try again.', 'danger')
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        if not email or not password:
            flash('Email and password are required!', 'warning')
            return redirect(url_for('login'))

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed!', 'danger')
            return redirect(url_for('login'))

        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session['email'] = user['email']
                session['username'] = user['username']
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid email or password!', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout route."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
