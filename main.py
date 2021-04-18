# Stockton University CSCI-4485 - Software Engineering (Spring 2021)
# Chores & Tasks Project
# GitHub: https://github.com/gguerini129/chores-tasks/

from flask import Flask
app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "mysql"
app.config["MYSQL_DB"] = "chores_tasks"
app.secret_key = "8970ab5e8cf15b3dd90919d215914ffcddbd06b9947f0dd2"

from flask_mysqldb import MySQL
mysql = MySQL(app)

from flask import render_template, url_for, redirect, session, request
import MySQLdb.cursors

@app.route("/")
def index():
    return redirect(url_for("login"))

# VIEW FUNCTIONS FOR LOGIN & REGISTER
@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    
    if request.method == "POST":
        form = request.form
        
        if valid_credentials(form["username"], form["password"]):
            log_in(getUser(form["username"]))
            return redirect(url_for("home"))
        else:
            error = "Invalid Login Credentials"
    
    log_out()
    return render_template("auth/login.html", error=error)

@app.route("/register", methods=["GET", "POST"])
def registration():
    error = ""
    
    if request.method == "POST":
        form = request.form
        
        if user_exists(form["username"]):
            error = "Username Taken"
        else:
            addUser(form["username"], form["password"], form["email"], form["first-name"], form["last-name"])
            log_in(getUser(form["username"]))
            return redirect(url_for("home"))
    
    log_out()
    return render_template("auth/register.html", error=error)

# HELPER FUNCTIONS FOR LOGIN & REGISTER
def user_exists(username):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
    exists = cursor.fetchone() != None
    cursor.close()
    return exists

def valid_credentials(username, password):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s", (username, password,))
    validity = cursor.fetchone() != None
    cursor.close()
    return validity

def getUser(username):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
    account = cursor.fetchone()
    cursor.close()
    return account

def addUser(username, password, email, first_name, last_name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO user (username, password, email, first_name, last_name) VALUES (%s, %s, %s, %s, %s)", (username, password, email, first_name, last_name,))
    mysql.connection.commit()
    cursor.close()

def log_in(account):
    session["user_id"] = account["user_id"]
    session["username"] = account["username"]
    session["password"] = account["password"]
    session["email"] = account["email"]
    session["first_name"] = account["first_name"]
    session["last_name"] = account["last_name"]

def log_out():
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("password", None)
    session.pop("email", None)
    session.pop("first_name", None)
    session.pop("last_name", None)

# VIEW FUNCTION FOR HOME
@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        form = request.form
        
        if form["submit"] == "create":
            task_list_id = get_next_task_list_id()
            add_task_list(form["name"])
            add_parent(session["user_id"], task_list_id)
        elif form["submit"] == "view":
            return redirect(url_for("task_list_basic", task_list_id=form["id"]))
    
    task_lists = get_task_lists(session["user_id"])
    return render_template("home.html", task_lists=task_lists)

# HELPER FUNCTIONS FOR HOME
def get_task_lists(user_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute((
        "SELECT task_list_id FROM parent WHERE user_id = {user_id}"
        " UNION ALL SELECT task_list_id FROM child WHERE user_id = {user_id}"
        " UNION ALL SELECT task_list_id FROM guardian WHERE user_id = {user_id}"
        "".format(user_id=user_id)
    ))
    
    task_list_ids = set()
    
    for row in cursor.fetchall():
        for _, task_list_id in row.items():
            task_list_ids.add(task_list_id)
    
    if len(task_list_ids) >= 1:
        query = "SELECT * FROM task_list"
        
        for i in range(len(task_list_ids)):
            conjunction = " WHERE" if i == 0 else " OR"
            query += conjunction + " task_list_id = " + str(list(task_list_ids)[i])
    
        cursor.execute(query)
        task_lists = cursor.fetchall()
    else:
        task_lists = ()
    
    cursor.close()
    return task_lists

def get_next_task_list_id():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT MAX(task_list_id) FROM task_list")
    next_id = cursor.fetchone()["MAX(task_list_id)"]
    cursor.close()
    next_id = 1 if next_id == None else next_id + 1
    return next_id

def add_task_list(name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO task_list (name) VALUES (%s)", (name,))
    mysql.connection.commit()
    cursor.close()

def add_parent(user_id, task_list_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO parent (user_id, task_list_id) VALUES (%s, %s)", (user_id, task_list_id,))
    mysql.connection.commit()
    cursor.close()

# VIEW FUNCTION FOR BASIC TASK LIST
@app.route("/tasklist/<int:task_list_id>/basic", methods=["GET", "POST"])
def task_list_basic(task_list_id):
    if request.method == "POST":
        form = request.form
        
        if form["submit"] == "create":
            if "description" in request.form:
                add_task(form["name"], form["description"], session["user_id"], task_list_id)
            else:
                add_task(form["name"], session["user_id"], task_list_id)
        elif form["submit"] == "delete":
            award_points(form["id"])
            delete_task(form["id"])
        elif form["submit"] == "modify":
            add_points_to_task(form["points"], form["id"])
        elif form["submit"] == "mark":
            if "marked" not in form:
                unmark(form["id"])
            elif form["marked"] == "marked":
                mark(form["id"])
            else:
                raise Exception()
        else:
            raise Exception()
    
    task_list = get_task_list(task_list_id)
    tasks = get_tasks(task_list_id)
    
    if parent_of(session["user_id"], task_list_id):
        user_type = "parent"
    elif child_of(session["user_id"], task_list_id):
        user_type = "child"
    elif guardian_of(session["user_id"], task_list_id):
        user_type = "guardian"
    else:
        raise Exception()
    
    if user_type == "parent":
        deletable_tasks = tasks
    elif user_type == "child" or user_type == "guardian":
        deletable_tasks = get_own_tasks(session["user_id"], task_list_id)
    
    return render_template("tasklist/basic.html", task_list=task_list, tasks=tasks, deletable_tasks=deletable_tasks, user_type=user_type)

# HELPER FUNCTIONS FOR BASIC TASK LIST
def get_tasks(task_list_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM task WHERE task_list_id = %s", (task_list_id,))
    tasks = cursor.fetchall()
    cursor.close()
    return tasks

def get_own_tasks(user_id, task_list_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM task WHERE user_id = %s AND task_list_id = %s AND points = 0", (user_id, task_list_id,))
    tasks = cursor.fetchall()
    cursor.close()
    return tasks

def child_of(user_id, task_list_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM child WHERE user_id = %s AND task_list_id = %s", (user_id, task_list_id,))
    child_of = True if cursor.fetchone() else False
    cursor.close()
    return child_of
    
def parent_of(user_id, task_list_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM parent WHERE user_id = %s AND task_list_id = %s", (user_id, task_list_id,))
    parent_of = True if cursor.fetchone() else False
    cursor.close()
    return parent_of
    
def guardian_of(user_id, task_list_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM guardian WHERE user_id = %s AND task_list_id = %s", (user_id, task_list_id,))
    guardian_of = True if cursor.fetchone() else False
    cursor.close()
    return guardian_of

def add_task(name, user_id, task_list_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO task (name, user_id, task_list_id) VALUES (%s, %s, %s)", (name, user_id, task_list_id,))
    mysql.connection.commit()
    cursor.close()

def add_task(name, description, user_id, task_list_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO task (name, description, user_id, task_list_id) VALUES (%s, %s, %s, %s)", (name, description, user_id, task_list_id,))
    mysql.connection.commit()
    cursor.close()
    
def delete_task(task_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM task WHERE task_id = %s", (task_id,))
    mysql.connection.commit()
    cursor.close()

def award_points(task_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM task WHERE task_id = %s AND marked = 1", (task_id,))
    task = cursor.fetchone()
    
    if task is None:
        cursor.close()
        return
    
    points = task["points"]
    
    cursor.execute("UPDATE child SET points = points + %s WHERE task_list_id = %s", (points, task["task_list_id"]))
    mysql.connection.commit()
    cursor.close()

def add_points_to_task(points, task_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE task SET points = %s WHERE task_id = %s", (points, task_id,))
    mysql.connection.commit()
    cursor.close()

def mark(task_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE task SET marked = 1 WHERE task_id = %s", (task_id,))
    mysql.connection.commit()
    cursor.close()

def unmark(task_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE task SET marked = 0 WHERE task_id = %s", (task_id,))
    mysql.connection.commit()
    cursor.close()

def get_task_list(task_list_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM task_list WHERE task_list_id = %s", (task_list_id,))
    task_list = cursor.fetchone()
    cursor.close()
    return task_list

# VIEW FUNCTION FOR ADMIN TASK LIST
@app.route("/tasklist/<int:task_list_id>/admin", methods=["GET", "POST"])
def task_list_admin(task_list_id):
    error = ""
    
    if request.method == "POST":
        form = request.form
        
        if form["submit"] == "share":
            account = getUser(form["username"])
            
            if account:
                if assigned_to(account["user_id"], task_list_id):
                    error = "User Already Assigned"
                else:
                    if form["user-type"] == "parent":
                        add_parent(account["user_id"], task_list_id)
                    elif form["user-type"] == "child":
                        add_child(account["user_id"], task_list_id)
                    elif form["user-type"] == "guardian":
                        add_guardian(account["user_id"], task_list_id)
            else:
                error = "User Not Found"
        elif form["submit"] == "delete":
            delete_task_list(task_list_id)
            return redirect(url_for("home"))
        else:
            raise Exception()
    
    task_list = get_task_list(task_list_id)
    
    if parent_of(session["user_id"], task_list_id):
        user_type = "parent"
    elif child_of(session["user_id"], task_list_id):
        user_type = "child"
    elif guardian_of(session["user_id"], task_list_id):
        user_type = "guardian"
    else:
        raise Exception()
    
    return render_template("tasklist/admin.html", task_list=task_list, user_type=user_type, error=error)

# HELPER FUNCTIONS FOR ADMIN TASK LIST
def assigned_to(user_id, task_list_id):
    return parent_of(user_id, task_list_id) or child_of(user_id, task_list_id) or guardian_of(user_id, task_list_id)

def add_child(user_id, task_list_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO child (user_id, task_list_id) VALUES (%s, %s)", (user_id, task_list_id,))
    mysql.connection.commit()
    cursor.close()

def add_guardian(user_id, task_list_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO guardian (user_id, task_list_id) VALUES (%s, %s)", (user_id, task_list_id,))
    mysql.connection.commit()
    cursor.close()

def delete_task_list(task_list_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM task_list WHERE task_list_id = %s", (task_list_id,))
    mysql.connection.commit()
    cursor.close()

# VIEW FUNCTION FOR TASK LIST WISH LIST
@app.route("/tasklist/<int:task_list_id>/wishlist", methods=["GET", "POST"])
def task_list_wish_list(task_list_id):
    error = ""
    
    if request.method == "POST":
        form = request.form
        
        if form["submit"] == "create":
            if "description" in request.form:
                add_wish(form["name"], form["description"], session["user_id"], task_list_id)
            else:
                add_wish(form["name"], session["user_id"], task_list_id)
        elif form["submit"] == "delete":
            delete_wish(form["id"])
        elif form["submit"] == "modify":
            add_points_to_wish(form["points"], form["id"])
        else:
            raise Exception()
    
    task_list = get_task_list(task_list_id)
    wishes = get_wishes(task_list_id)
    
    points = 0
    
    if parent_of(session["user_id"], task_list_id):
        user_type = "parent"
    elif child_of(session["user_id"], task_list_id):
        user_type = "child"
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM child WHERE user_id = %s AND task_list_id = %s", (session["user_id"], task_list_id,))
        points = cursor.fetchone()["points"]
        cursor.close()
    elif guardian_of(session["user_id"], task_list_id):
        user_type = "guardian"
    else:
        raise Exception()
    
    return render_template("tasklist/wishlist.html", task_list=task_list, wishes=wishes, user_type=user_type, points=points)

# HELPER FUNCTIONS FOR TASK LIST WISH LIST
def get_wishes(task_list_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM wish WHERE task_list_id = %s", (task_list_id,))
    wishes = cursor.fetchall()
    cursor.close()
    return wishes

def add_wish(name, user_id, task_list_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO wish (name, user_id, task_list_id) VALUES (%s, %s, %s)", (name, user_id, task_list_id,))
    mysql.connection.commit()
    cursor.close()

def add_wish(name, description, user_id, task_list_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO wish (name, description, user_id, task_list_id) VALUES (%s, %s, %s, %s)", (name, description, user_id, task_list_id,))
    mysql.connection.commit()
    cursor.close()

def delete_wish(wish_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM wish WHERE wish_id = %s", (wish_id,))
    mysql.connection.commit()
    cursor.close()

def add_points_to_wish(points, wish_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE wish SET points = %s WHERE wish_id = %s", (points, wish_id,))
    mysql.connection.commit()
    cursor.close()

# EXECUTION
if __name__ == "__main__":
    app.run(debug=True)  # Setting debug to true tells flask to immediately apply changes in the code
