# Stockton University CSCI-4485 - Software Engineering (Spring 2021)
# Chores & Tasks Project
# GitHub: https://github.com/gguerini129/chores-tasks/

from flask import Flask, render_template, url_for, redirect, session, request
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

# INITIALIZATION

app = Flask(__name__)
mysql = MySQL(app)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "mysql"
app.config["MYSQL_DB"] = "chores_tasks"
app.secret_key = "secretKey"

# INDEX VIEW FUNCTION
@app.route("/")
def index():
    """
    :return: render_template of the next page
    """
    return redirect(url_for("login"))

# REGISTER VIEW FUNCTION
@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Renders the registration page for get and post requests
    Displays a message when the registration is invalid
    :return: render_template for the next page
    """
    
    msg = "Nothing to report."
    
    if request.method == "POST" and "first-name" in request.form and "last-name" in request.form and "username" in request.form and "password" in request.form and "email" in request.form:
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        
        # if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            # msg = "Invalid email address!"
        # elif not re.match(r"[A-Za-z0-9]+", username):
            # msg = "Username must contain only characters and numbers!"
        # elif not username or not password or not email:
            # msg = "Please fill out the form!"
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        account = cursor.fetchone()
        
        if account is None:
            cursor.execute("INSERT INTO user (username, password, email, first_name, last_name) VALUES (%s, %s, %s, %s, %s)", (username, password, email, first_name, last_name,))
            mysql.connection.commit()
            
            session["first_name"] = first_name
            session["last_name"] = last_name
            session["username"] = username
            session["password"] = password
            session["email"] = email
            
            return redirect(url_for("home"))
        else:
            msg = "Username already taken."
    
    return render_template("register.html", msg=msg)

# LOGIN VIEW FUNCTION
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Renders the login page for get and post requests
    Displays a message when the login is invalid
    :return: render_template for the next page
    """
    
    msg = "Nothing to report."
    
    if request.method == "POST" and "username" in request.form and "password" in request.form:
        username = request.form["username"]
        password = request.form["password"]
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s", (username, password,))
        account = cursor.fetchone()
        
        if account is not None:
            # All home page will need for now.
            # May need to close cursor in this block later to gather more info
            # about the user, but that is a feature that will be implemented
            # later when the homepage is complete.
            #
            session["first_name"] = account["first_name"]
            session["last_name"] = account["last_name"]
            session["username"] = username
            session["password"] = password
            session["email"] = account["email"]
            
            return redirect(url_for("home"))
        else:
            msg = "Incorrect login details."
    
    return render_template("login.html", msg=msg)

# LOGOUT VIEW FUNCTION
@app.route("/logout", methods = ["GET"])
def logout():
    """
    Logs a user out.
    :return: renders the log in screen with a message indicating that the user logged out.
    """
    
    session.pop("first_name", None)
    session.pop("last_name", None)
    session.pop("username", None)
    session.pop("password", None)
    session.pop("email", None)
    
    return redirect(url_for("login"))

# HOME VIEW FUNCTION
@app.route("/home", methods = ["GET", "POST"])
def home():
    lists = {
        "Brian's Task List": 0,
        "Courtney's Task List": 1,
        "The Mega Awesome List": 2
    }
    
    return render_template("home.html", lists=lists)

# EXECUTION
if __name__ == "__main__":
    app.run()
