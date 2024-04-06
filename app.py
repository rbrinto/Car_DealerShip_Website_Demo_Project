from flask import Flask, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '61017751'
app.config['MYSQL_DB'] = 'caraccounts'
app.config['SECRET_KEY'] = 'my_secret_key'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    # Insert user data into database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
    mysql.connection.commit()
    cur.close()

    return redirect('/')

@app.route('/inventory')
def inventory():
    # Check if the user is signed in
    if 'user_id' not in session:
        # If not signed in, redirect to the login page
        return redirect('/sign_in')
    return render_template('inventory.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        username_or_email = request.form['username']
        password = request.form['password']

        # Check if username or email exists in the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username_or_email, username_or_email))
        user = cur.fetchone()
        cur.close()

        if user and user[3] == password:
            session['user_id'] = user[0]  # Create session for logged-in user
            return redirect('/')
        else:
            return 'Invalid username or password'
    return render_template('sign_in.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user_id from session
    return redirect('/')  # Redirect to homepage after logout

@app.route('/book_car')
def book_car():
    cur = mysql.connection.cursor()
    # Get the car name from the form submission
    car_name = request.args.get('car_name')

    # Perform the booking confirmation
        # Update the bookings column in the users table
        # You need to replace this with your database logic
    user_id = session.get('user_id')  # Assuming the user is logged in
    if user_id is not None:
        # Append the booked car name to the bookings field
        cur.execute("SELECT bookings FROM users WHERE id = %s", (user_id,))
        current_bookings = cur.fetchone()[0]

# Append the newly booked car to the existing bookings
    if current_bookings:
        updated_bookings = current_bookings + ', ' + car_name
    else:
        updated_bookings = car_name

    # Update the "bookings" column in the users table with the updated bookings
    cur.execute("UPDATE users SET bookings = %s WHERE id = %s", (updated_bookings, user_id))
    cur.connection.commit()
    cur.close()
    flash("Booking Confirmed")
    return redirect("/inventory")

@app.route('/mybookings')

def mybookings():
    cur = mysql.connection.cursor()
    

if __name__ == "__main__":
    app.run(debug=True)

