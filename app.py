from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os

app = Flask(__name__)
app.secret_key = "change_this_secret"  

COMPANY_NAME = "AN Tech Solutions"

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        message TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        year INTEGER
    )""")

    # Seed projects if empty
    count = c.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    if count == 0:
        projects = [
            ("Inventory Management System", "A scalable web app for real-time stock tracking.", 2023),
            ("E-commerce Platform", "Full-stack marketplace with payments & analytics.", 2024),
            ("HR Portal", "Employee onboarding, leave & performance workflows.", 2022),
        ]
        c.executemany("INSERT INTO projects (title, description, year) VALUES (?, ?, ?)", projects)

    conn.commit()
    conn.close()

@app.context_processor
def inject_globals():
    return {"COMPANY_NAME": COMPANY_NAME}

# Public pages 
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/services")
def services():
    conn = get_db_connection()
    projects = conn.execute("SELECT * FROM projects ORDER BY year DESC").fetchall()
    conn.close()
    services = [
        {"name": "Custom Software Projects", "desc": "End-to-end delivery: discovery, design, development, QA, deployment."},
        {"name": "Scalable Websites", "desc": "Responsive, SEO-friendly websites with good performance."},
        {"name": "Cloud & DevOps", "desc": "Pipelines, containerization, monitoring and cost optimization."},
    ]
    return render_template("services.html", services=services, projects=projects)

@app.route("/contact", methods=["GET","POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip()
        phone = request.form.get("phone","").strip()
        message = request.form.get("message","").strip()
        if not (name and email and message):
            flash("Please fill name, email and message.", "danger")
            return redirect(url_for("contact"))
        conn = get_db_connection()
        conn.execute("INSERT INTO contacts (name,email,phone,message) VALUES (?, ?, ?, ?)",
                     (name,email,phone,message))
        conn.commit()
        conn.close()
        flash("Thanks — your message has been received.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")

# Customer Authorization and Dashboard
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        if not (username and password):
            flash("Username and password required.", "danger")
            return redirect(url_for("register"))
        hashed = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username,password) VALUES (?, ?)", (username, hashed))
            conn.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists.", "warning")
            return redirect(url_for("register"))
        finally:
            conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session["user"] = user["username"]
            flash("Login successful.", "success")
            return redirect(url_for("customer_dashboard"))
        else:
            flash("Invalid credentials.", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out.", "info")
    return redirect(url_for("index"))

@app.route("/customer/dashboard")
def customer_dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    services = [
        {"name": "Custom Software Projects", "desc": "End-to-end product engineering."},
        {"name": "Scalable Websites", "desc": "Fast, responsive and scalable sites."},
        {"name": "Cloud & DevOps", "desc": "Infrastructure & CI/CD."}
    ]
    conn = get_db_connection()
    projects = conn.execute("SELECT * FROM projects ORDER BY year DESC").fetchall()
    conn.close()
    return render_template("customer_dashboard.html", user=session["user"], services=services, projects=projects)

# Admin Section
@app.route("/admin")                # Admin main entry
def admin_page():
    return render_template("admin_page.html")

@app.route("/admin/register", methods=["GET","POST"])
def admin_register():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        if not (username and password):
            flash("Username and password required.", "danger")
            return redirect(url_for("admin_register"))
        hashed = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO admins (username,password) VALUES (?, ?)", (username, hashed))
            conn.commit()
            flash("Admin registered. Please login.", "success")
            return redirect(url_for("admin_login"))
        except sqlite3.IntegrityError:
            flash("Admin username already exists.", "warning")
            return redirect(url_for("admin_register"))
        finally:
            conn.close()
    return render_template("admin_register.html")

@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        conn = get_db_connection()
        admin = conn.execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
        conn.close()
        if admin and check_password_hash(admin["password"], password):
            session["admin"] = admin["username"]
            flash("Admin login successful.", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin credentials.", "danger")
            return redirect(url_for("admin_login"))
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    flash("Admin logged out.", "info")
    return redirect(url_for("admin_page"))

# Admin Dashboard & CRUD operations
@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))
    conn = get_db_connection()
    customers = conn.execute("SELECT * FROM customers ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("admin_dashboard.html", customers=customers)

@app.route("/admin/add_customer", methods=["GET","POST"])
def admin_add_customer():
    if "admin" not in session:
        return redirect(url_for("admin_login"))
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip()
        phone = request.form.get("phone","").strip()
        if not (name and email):
            flash("Name and Email required.", "danger")
            return redirect(url_for("admin_add_customer"))
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO customers (name,email,phone) VALUES (?, ?, ?)", (name,email,phone))
            conn.commit()
            flash("Customer added.", "success")
        except sqlite3.IntegrityError:
            flash("Email already exists.", "warning")
        finally:
            conn.close()
        return redirect(url_for("admin_dashboard"))
    return render_template("add_customer.html")

@app.route("/admin/edit_customer/<int:cid>", methods=["GET","POST"])
def admin_edit_customer(cid):
    if "admin" not in session:
        return redirect(url_for("admin_login"))
    conn = get_db_connection()
    customer = conn.execute("SELECT * FROM customers WHERE id = ?", (cid,)).fetchone()
    if not customer:
        conn.close()
        flash("Customer not found.", "warning")
        return redirect(url_for("admin_dashboard"))
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip()
        phone = request.form.get("phone","").strip()
        if not (name and email):
            flash("Name and Email required.", "danger")
            return redirect(url_for("admin_edit_customer", cid=cid))
        try:
            conn.execute("UPDATE customers SET name=?, email=?, phone=? WHERE id=?",
                         (name,email,phone,cid))
            conn.commit()
            flash("Customer updated.", "success")
        except sqlite3.IntegrityError:
            flash("Email already used.", "warning")
        finally:
            conn.close()
        return redirect(url_for("admin_dashboard"))
    conn.close()
    return render_template("edit_customer.html", customer=customer)

@app.route("/admin/delete_customer/<int:cid>")
def admin_delete_customer(cid):
    if "admin" not in session:
        return redirect(url_for("admin_login"))
    conn = get_db_connection()
    conn.execute("DELETE FROM customers WHERE id = ?", (cid,))
    conn.commit()
    conn.close()
    flash("Customer deleted.", "info")
    return redirect(url_for("admin_dashboard"))

# Main Function Run
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
