from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "task3_secret_key"

DATABASE = "database.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Students table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL,
            semester INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(
            request.form["password"]
        )

        db = get_db()

        try:
            db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )

            db.commit()
            flash("Registration successful! Please login.", "success")

            return redirect(url_for("login"))

        except:
            flash("Username already exists!", "danger")

        db.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()

        user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        db.close()

        if user and check_password_hash(
            user["password"],
            password
        ):
            session["user"] = user["username"]

            flash("Login successful!", "success")

            return redirect(url_for("dashboard"))

        else:
            flash("Invalid username or password!", "danger")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        flash("Please login first!", "danger")
        return redirect(url_for("login"))

    db = get_db()

    total_students = db.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    total_courses = db.execute(
        "SELECT COUNT(DISTINCT course) FROM students"
    ).fetchone()[0]

    latest_student = db.execute("""
        SELECT name
        FROM students
        ORDER BY created_at DESC
        LIMIT 1
    """).fetchone()

    db.close()

    return render_template(
        "dashboard.html",
        user=session["user"],
        total_students=total_students,
        total_courses=total_courses,
        latest_student=latest_student
    )

@app.route("/students")
def students():

    if "user" not in session:
        flash("Please login first!", "danger")
        return redirect(url_for("login"))

    search = request.args.get("search", "")

    db = get_db()

    if search:

        students = db.execute("""
            SELECT *
            FROM students
            WHERE
                name LIKE ?
                OR email LIKE ?
                OR course LIKE ?
            ORDER BY created_at DESC
        """,
        (
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        )).fetchall()

    else:

        students = db.execute("""
            SELECT *
            FROM students
            ORDER BY created_at DESC
        """).fetchall()

    db.close()

    return render_template(
        "students.html",
        students=students,
        user=session["user"],
        search=search
    )

@app.route("/add-student", methods=["GET", "POST"])
def add_student():

    if "user" not in session:
        flash("Please login first!", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        course = request.form["course"]
        semester = request.form["semester"]

        db = get_db()

        db.execute("""
            INSERT INTO students
            (name, email, course, semester)
            VALUES (?, ?, ?, ?)
        """, (name, email, course, semester))

        db.commit()
        db.close()

        flash("Student added successfully!", "success")

        return redirect(url_for("students"))

    return render_template("add_student.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    if "user" not in session:
        flash("Please login first!", "danger")
        return redirect(url_for("login"))

    db = get_db()

    student = db.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    ).fetchone()

    if request.method == "POST":

        db.execute("""
            UPDATE students
            SET
                name=?,
                email=?,
                course=?,
                semester=?
            WHERE id=?
        """,
        (
            request.form["name"],
            request.form["email"],
            request.form["course"],
            request.form["semester"],
            id
        ))

        db.commit()
        db.close()

        flash("Student updated successfully!", "success")

        return redirect(url_for("students"))

    db.close()

    return render_template(
        "edit_student.html",
        student=student
    )


@app.route("/delete/<int:id>")
def delete_student(id):

    if "user" not in session:
        flash("Please login first!", "danger")
        return redirect(url_for("login"))

    db = get_db()

    db.execute(
        "DELETE FROM students WHERE id=?",
        (id,)
    )

    db.commit()
    db.close()

    flash("Student deleted successfully!", "success")

    return redirect(url_for("students"))

@app.route("/logout")
def logout():
    session.pop("user", None)

    flash("Logged out successfully!", "success")

    return redirect(url_for("login"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)