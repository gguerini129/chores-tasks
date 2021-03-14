import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

# Stockton University CSCI-4485 - Software Engineering (Spring 2021)
#
# Student Task Manager project
# (add link to Github repo)
#

# 3. Log out
#    a. log out redirects to log in page
#
#

# initialize Flask and mysql and log in
app = Flask(__name__)
mysql = MySQL(app)
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "root"
app.config['MYSQL_DB'] = "user"
app.secret_key = 'secretKey'

@app.route("/", methods=['GET', 'POST'])
def login():
    """
    Verifies if the credentials exist, and allows the user to log in if so.
    Otherwise, a message is displayed that the account does not exist.
    :return: render_template to the homepage of the application.
    """

    # Display a message to the user if log in is unsuccessful
    msg = ""

    if request.method == "POST" and 'username' in request.form and 'password' in request.form:

        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM user WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()

        if account:
            # All home page will need for now.
            # May need to close cursor in this block later to gather more info
            # about the user, but that is a feature that will be implemented
            # later when the homepage is complete.
            #
            username = account["username"]
            first_name = account["first_name"]
            email = account["email"]

            return render_template("home.html", username = username, first_name = first_name, email = email)
        else:
            msg = "Invalid credentials entered. Try again, or click the register link to create an account."

    return render_template("index.html", msg = msg)

@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Registers a new user if the username and email are unique.
    :return: Redirects to log in page for user to log in with new account.
    """

    # Output message if something goes wrong...
    msg = ''

    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:

        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE username = %s', (username,))
        account = cursor.fetchone()

        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'

        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'

        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'

        elif not username or not password or not email:
            msg = 'Please fill out the form!'

        else:

            #create unique ID for user (MAX of user_id + 1)
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO user (username, password, email, first_name, last_name) VALUES (%s, %s, %s, %s, %s)', (username, password, email, first_name, last_name,))
            # default id is -1, but it is updated to MAX + 1

            mysql.connection.commit()

            msg = 'You have successfully registered! Please log in using your newly-created account.'
            return render_template("index.html", msg = msg)

    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'

    return render_template('register.html', msg = msg)


@app.route('/logout', methods = ["GET", "POST"])
def logout():
    """
    Logs a user out.
    :return: renders the log in screen with a message indicating that the user logged out.
    """
    return render_template("index.html", msg = "You have logged out")

if __name__ == "__main__":
    app.run()
