from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "task2_secret_key"

DATABASE = "database.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
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

    return render_template(
        "dashboard.html",
        user=session["user"]
    )


@app.route("/logout")
def logout():
    session.pop("user", None)

    flash("Logged out successfully!", "success")

    return redirect(url_for("login"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)