from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)


# =========================
# CONNECT TO MYSQL
# =========================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="NAGA@2007",
    database="to_dolist"
)

cursor = db.cursor()


# =========================
# LOGIN
# =========================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        query = """
        SELECT * FROM users
        WHERE username = %s AND password = %s
        """

        cursor.execute(query, (username, password))

        result = cursor.fetchone()

        if result:
            return render_todo(username)

        else:
            return "Invalid username or password."

    return render_template("login.html")


# =========================
# SHOW TODO DASHBOARD
# =========================
def render_todo(username):

    query = """
    SELECT id, task, status
    FROM tasks
    WHERE username = %s
    ORDER BY id DESC
    """

    cursor.execute(query, (username,))

    tasks = cursor.fetchall()

    total_tasks = len(tasks)

    pending_tasks = sum(
        1 for task in tasks
        if task[2] == "Pending"
    )

    completed_tasks = sum(
        1 for task in tasks
        if task[2] == "Completed"
    )

    # Calculate productivity percentage
    if total_tasks > 0:
        progress = round((completed_tasks / total_tasks) * 100)
    else:
        progress = 0

    return render_template(
        "todo.html",
        username=username,
        tasks=tasks,
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        progress=progress
    )

# =========================
# ADD TASK
# =========================

@app.route("/add_task", methods=["POST"])
def add_task():

    task = request.form["task"]
    username = request.form["username"]

    query = """
    INSERT INTO tasks (username, task, status)
    VALUES (%s, %s, %s)
    """

    cursor.execute(
        query,
        (username, task, "Pending")
    )

    db.commit()

    return render_todo(username)


# =========================
# COMPLETE TASK
# =========================

@app.route("/complete_task/<int:task_id>/<username>")
def complete_task(task_id, username):

    query = """
    UPDATE tasks
    SET status = 'Completed'
    WHERE id = %s AND username = %s
    """

    cursor.execute(
        query,
        (task_id, username)
    )

    db.commit()

    return render_todo(username)


# =========================
# DELETE TASK
# =========================

@app.route("/delete_task/<int:task_id>/<username>")
def delete_task(task_id, username):

    query = """
    DELETE FROM tasks
    WHERE id = %s AND username = %s
    """

    cursor.execute(
        query,
        (task_id, username)
    )

    db.commit()

    return render_todo(username)


# =========================
# COMPLETED TASKS PAGE
# =========================

@app.route("/completed/<username>")
def completed(username):

    query = """
    SELECT id, task, status
    FROM tasks
    WHERE username = %s
    AND status = 'Completed'
    ORDER BY id DESC
    """

    cursor.execute(
        query,
        (username,)
    )

    tasks = cursor.fetchall()

    return render_template(
        "completed.html",
        username=username,
        tasks=tasks
    )


# =========================
# PROFILE PAGE
# =========================

@app.route("/profile/<username>")
def profile(username):

    query = """
    SELECT id, task, status
    FROM tasks
    WHERE username = %s
    """

    cursor.execute(
        query,
        (username,)
    )

    tasks = cursor.fetchall()

    total_tasks = len(tasks)

    pending_tasks = sum(
        1 for task in tasks
        if task[2] == "Pending"
    )

    completed_tasks = sum(
        1 for task in tasks
        if task[2] == "Completed"
    )

    return render_template(
        "profile.html",
        username=username,
        total_tasks=total_tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks
    )


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    return render_template("login.html")


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    app.run(debug=True)