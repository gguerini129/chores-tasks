# Stockton University CSCI-4485 - Software Engineering (Spring 2021)
# Chores & Tasks Project
# GitHub: https://github.com/gguerini129/chores-tasks/

# cursor.fetchone() -> returns a dict
# cursor.fetchall() -> returns a tuple of dicts

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

    if request.method == "POST" and "username" in request.form and "password" in request.form and "email" in request.form and "first-name" in request.form and "last-name" in request.form:
        username = request.form["username"]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        account = cursor.fetchone()

        if account is None:
            password = request.form["password"]
            email = request.form["email"]
            first_name = request.form["first-name"]
            last_name = request.form["last-name"]

            cursor.execute("INSERT INTO user (username, password, email, first_name, last_name) VALUES (%s, %s, %s, %s, %s)", (username, password, email, first_name, last_name,))
            mysql.connection.commit()

            cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
            account = cursor.fetchone()

            # Logs the user in
            session["user_id"] = account["user_id"]
            session["username"] = username
            session["password"] = password
            session["email"] = email
            session["first_name"] = first_name
            session["last_name"] = last_name

            return redirect(url_for("home"))
        else:
            msg = "Username already taken."

    # Logs the user out
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("password", None)
    session.pop("email", None)
    session.pop("first_name", None)
    session.pop("last_name", None)

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
            # Logs the user in
            session["user_id"] = account["user_id"]
            session["username"] = username
            session["password"] = password
            session["email"] = account["email"]
            session["first_name"] = account["first_name"]
            session["last_name"] = account["last_name"]

            return redirect(url_for("home"))
        else:
            msg = "Incorrect login details."

    # Logs the user out
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("password", None)
    session.pop("email", None)
    session.pop("first_name", None)
    session.pop("last_name", None)

    return render_template("login.html", msg=msg)


# HOME VIEW FUNCTION
@app.route("/home", methods=["GET", "POST"])
def home():
    """
    Renders the home page for get and post requests
    :return: render_template for the next page
    """

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST":
        if request.form["submit"] == "create":
            task_list_name = request.form["task-list-name"]
            cursor.execute("INSERT INTO task_list (name) VALUES (%s)", (task_list_name,))
            mysql.connection.commit()

            cursor.execute("SELECT * FROM task_list ORDER BY task_list_id DESC")
            task_list = cursor.fetchone()
            task_list_id = task_list["task_list_id"]

            user_id = session["user_id"]

            cursor.execute("INSERT INTO parent (user_id, task_list_id) VALUES (%s, %s)", (user_id, task_list_id,))
            mysql.connection.commit()
        elif request.form["submit"] == "view" and "task-list-id" in request.form:
            task_list_id = request.form["task-list-id"]

            return redirect(url_for("tasklist", task_list_id=task_list_id))

    task_list_ids = set()
    user_id = session["user_id"]

    cursor.execute("SELECT * FROM parent WHERE user_id = %s", (user_id,))

    for parent_association in cursor.fetchall():
        task_list_ids.add(tuple([parent_association["task_list_id"]]))

    pairs = {}

    if len(task_list_ids) >= 1:
        query = "SELECT * FROM task_list WHERE task_list_id = " + str(list(task_list_ids)[0][0])

        for i in range(1, len(task_list_ids)):
            query += " OR task_list_id = " + str(list(task_list_ids)[i][0])

        cursor.execute(query)
        task_lists = cursor.fetchall()

        for task_list in task_lists:
            pairs[task_list["name"]] = task_list["task_list_id"]

    return render_template("home.html", pairs=pairs)


# TASKLIST VIEW FUNCTION
@app.route("/tasklist/<int:task_list_id>", methods=["GET", "POST"])
def tasklist(task_list_id):
    """
    Renders the tasklist page for get and post requests
    :return: render_template for the next page
    """

    if request.method == "POST":
        if request.form["submit"] == "create":
            print("Creating Task for Task List with ID " + str(task_list_id))
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM task_list WHERE task_list_id = %s", (task_list_id,))
    task_list = cursor.fetchone()
    
    task_list_name = task_list["name"]

    return render_template("tasklist.html", task_list_id=task_list_id, task_list_name=task_list_name)

# EXECUTION
if __name__ == "__main__":
    app.run(debug=True)  # Setting debug to true tells flask to immediately apply changes in the code
