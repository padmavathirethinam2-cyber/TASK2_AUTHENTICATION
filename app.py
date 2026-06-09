from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "padhu_secret_key"

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(
            request.form["password"]
        )

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(name,email,password) VALUES(?,?,?)",
                (name, email, password)
            )

            conn.commit()

        except:
            return "Email already exists"

        finally:
            conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):

            session["user"] = user[1]
            session["email"] = user[2]

            return redirect("/dashboard")

        return "Invalid Email or Password"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        user=session["user"],
        email=session["email"]
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        user=session["user"],
        email=session["email"],
        total_users=total_users
    )