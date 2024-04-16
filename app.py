from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
# Importing Flask class from the flask module.
from flask import Flask

# Importing MySQL class from flask_mysqldb module to handle MySQL interactions.
from flask_mysqldb import MySQL

# Creating an instance of the Flask class. '__name__' is a built-in variable which evaluates to the name of the current module.
app = Flask(__name__)

# Configuring the MySQL database host to 'localhost'. This is where the MySQL server is running.
app.config['MYSQL_HOST'] = 'localhost'

# Configuring the MySQL database user as 'root'. This is the username used to authenticate with MySQL.
app.config['MYSQL_USER'] = 'root'

# Configuring the MySQL database password as 'root'. This is the password used to authenticate with MySQL.
app.config['MYSQL_PASSWORD'] = 'root'

# Setting the name of the database to use, here it's set as 'caraccounts'.
app.config['MYSQL_DB'] = 'caraccounts'

# Setting a secret key for the application. This is used for securely signing the session cookie.
app.config['SECRET_KEY'] = 'my_secret_key'

# Creating an instance of the MySQL class and passing the Flask app instance to handle MySQL operations.
mysql = MySQL(app)

# Define a route for the root URL '/' that handles GET requests.
@app.route('/')
# This function handles requests to the root URL.
def index():
    # Retrieve the 'message' parameter from the request's query string (URL parameters).
    message = request.args.get('message')
    # Render the 'index.html' template, passing in the 'message' variable.
    return render_template('index.html', message=message)

# Define a route for the URL '/register' that handles POST requests.
@app.route('/register', methods=['POST'])
# This function handles requests to the '/register' URL for POST requests.
def register():
    # Retrieve the 'username' parameter from the submitted form data.
    username = request.form['username']
    # Retrieve the 'email' parameter from the submitted form data.
    email = request.form['email']
    # Retrieve the 'password' parameter from the submitted form data.
    password = request.form['password']

    # Create a cursor object to interact with the MySQL database.
    cur = mysql.connection.cursor()
    # Execute an SQL statement to insert the user data (username, email, password) into the 'users' table.
    cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
    # Commit the transaction to save the changes to the database.
    mysql.connection.commit()
    # Close the cursor object.
    cur.close()

    # Redirect the user back to the root URL '/' after registration.
    return redirect('/')


# Define a route for the URL '/inventory' that handles GET requests.
@app.route('/inventory')
# This function handles requests to the '/inventory' URL.
def inventory():
    # Check if the user is signed in by looking for 'user_id' in the session object.
    if 'user_id' not in session:
        # If the user is not signed in, redirect them to the sign-in page at '/sign_in'.
        return redirect('/sign_in')
    # Retrieve the 'message' parameter from the request's query string (URL parameters).
    message = request.args.get('message')
    # Render the 'inventory.html' template, passing in the 'message' variable.
    return render_template('inventory.html', message=message)

# Define a route for the URL '/about' that handles GET requests.
@app.route('/about')
# This function handles requests to the '/about' URL.
def about():
    # Render the 'about.html' template.
    return render_template('about.html')

# Define a route for the URL '/sign_in' that handles both GET and POST requests.
@app.route('/sign_in', methods=['GET', 'POST'])
# This function handles requests to the '/sign_in' URL for both GET and POST methods.
def sign_in():
    # If the request method is POST, proceed with form submission logic.
    if request.method == 'POST':
        # Retrieve the 'username' or 'email' parameter from the submitted form data.
        username_or_email = request.form['username']
        # Retrieve the 'password' parameter from the submitted form data.
        password = request.form['password']

        # Create a cursor object to interact with the MySQL database.
        cur = mysql.connection.cursor()
        # Execute an SQL statement to select the user record from the 'users' table using username or email.
        cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username_or_email, username_or_email))
        # Fetch one record from the query result.
        user = cur.fetchone()
        # Close the cursor object.
        cur.close()

        # Check if the user record exists and if the password matches the stored password.
        if user and user[3] == password:
            # If the user is authenticated, create a session for the logged-in user by storing the user ID.
            session['user_id'] = user[0]
            # Define a success message to be displayed upon successful sign-in.
            message = "Signed In Successfully!"
            # Redirect the user to the root URL '/' with a success message.
            return redirect(url_for('index', message=message))
        else:
            # If the authentication fails, return an error message indicating invalid username or password.
            return 'Invalid username or password'
    # If the request method is GET, render the 'sign_in.html' template.
    return render_template('sign_in.html')

# Define a route for the URL '/logout' that handles GET requests.
@app.route('/logout')
# This function handles requests to the '/logout' URL.
def logout():
    # Remove the 'user_id' key from the session to log the user out.
    session.pop('user_id', None)
    # Define a message indicating successful logout.
    message = "Logged Out Successfully!"
    # Redirect the user to the root URL '/' (index) with the logout success message.
    return redirect(url_for('index', message=message))

# Define a route for the URL '/book_car' that handles GET requests.
@app.route('/book_car')
# This function handles requests to the '/book_car' URL.
def book_car():
    # Create a cursor object to interact with the MySQL database.
    cur = mysql.connection.cursor()
    # Retrieve the 'car_name' parameter from the request's query string (URL parameters).
    car_name = request.args.get('car_name')

    # Retrieve the user ID from the session object.
    user_id = session.get('user_id')  # Assuming the user is logged in
    # Check if the user ID exists in the session.
    if user_id is not None:
        # Execute an SQL statement to retrieve the current bookings for the user from the 'users' table.
        cur.execute("SELECT bookings FROM users WHERE id = %s", (user_id,))
        # Fetch the current bookings from the query result.
        current_bookings = cur.fetchone()[0]

        # Append the newly booked car to the existing bookings if there are any current bookings.
        if current_bookings:
            updated_bookings = current_bookings + ', ' + car_name
        else:
            updated_bookings = car_name

        # Execute an SQL statement to update the "bookings" column in the 'users' table with the updated bookings.
        cur.execute("UPDATE users SET bookings = %s WHERE id = %s", (updated_bookings, user_id))
        # Commit the transaction to save the changes to the database.
        cur.connection.commit()
    # Close the cursor object.
    cur.close()
    # Define a message indicating successful booking confirmation.
    message = "Booking Confirmed"
    # Redirect the user to the 'inventory' URL with the booking confirmation message.
    return redirect(url_for("inventory", message=message))

# Define a route for the URL '/mybookings' that handles GET requests.
@app.route('/mybookings')
# This function handles requests to the '/mybookings' URL.
def mybookings():
    # Create a cursor object to interact with the MySQL database.
    cur = mysql.connection.cursor()
    # Retrieve the user ID from the session object.
    user_id = session.get('user_id')
    # Execute an SQL statement to retrieve the bookings for the user from the 'users' table.
    cur.execute("SELECT bookings FROM users WHERE id = %s;", (user_id,))
    # Fetch the bookings from the query result.
    bookings = cur.fetchone()[0]
    # Close the cursor object.
    cur.close()
    # Split the bookings string into a list of car names if there are bookings, otherwise return an empty list.
    car_names = bookings.split(', ') if bookings else []
    # Render the 'mybookings.html' template, passing in the list of car names.
    return render_template('mybookings.html', car_names=car_names)

# Define a route for the URL '/remove_booking' that handles POST requests.
@app.route('/remove_booking', methods=['POST'])
# This function handles requests to the '/remove_booking' URL for POST requests.
def remove_booking():
    # Retrieve the user ID from the session object.
    user_id = session.get('user_id')
    # Retrieve the car name to be removed from the form submission.
    car_to_remove = request.form.get('car_name')
    # Create a cursor object to interact with the MySQL database.
    cursor = mysql.connection.cursor()
    # Execute an SQL statement to retrieve the current bookings for the user from the 'users' table.
    cursor.execute("SELECT bookings FROM users WHERE id = %s;", (user_id,))
    # Fetch the current bookings from the query result.
    current_bookings = cursor.fetchone()[0]
    # Create a new string of bookings that excludes the car to be removed.
    new_bookings = ', '.join([car for car in current_bookings.split(', ') if car != car_to_remove])
    # Execute an SQL statement to update the "bookings" column in the 'users' table with the new bookings.
    cursor.execute("UPDATE users SET bookings = %s WHERE id = %s;", (new_bookings, user_id))
    # Commit the transaction to save the changes to the database.
    cursor.connection.commit()
    # Close the cursor object.
    cursor.close()
    # Redirect the user to the 'mybookings' URL after the booking is removed.
    return redirect(url_for('mybookings', user_id=user_id))

# The entry point for running the Flask app.
if __name__ == "__main__":
    # Run the Flask app in debug mode, allowing for real-time updates and error messages.
    app.run(debug=True)
