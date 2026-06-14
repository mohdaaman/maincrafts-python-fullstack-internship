from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)

app.secret_key = "maincrafts_internship_secret_key"

DATABASE = "database.db"


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            department TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY id DESC")

    users = cursor.fetchall()

    conn.close()

    return render_template("index.html", users=users)


@app.route("/add_user", methods=["POST"])
def add_user():

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    department = request.form["department"]

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users
        (name, email, phone, department, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        email,
        phone,
        department,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()
    
    flash("User added successfully!", "success")

    return redirect(url_for("index"))

@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM users WHERE id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()

    flash("User deleted successfully!", "danger")

    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)