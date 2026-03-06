from flask import Flask, render_template, request, redirect, session, jsonify, flash
import mysql.connector
import bcrypt
import random
import os

ADMIN_MASTER_PASSWORD = os.environ.get("ADMIN_MASTER_PASSWORD")   # change this to something strong

app = Flask(__name__)
app.secret_key = "supersecretkey123"


# ===============================
# Prevent Back Button After Logout
# ===============================
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# ===============================
# Database Connection
# ===============================
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME")
    )


# ===============================
# LOGIN
# ===============================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        if "account_no" in session:
            return redirect("/")
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE username=%s",
        (username,)
    )

    user = cursor.fetchone()

    if user and bcrypt.checkpw(
        password.encode(),
        user["password_hash"].encode()
    ):

        session["user"] = username
        session["account_no"] = user["account_no"]

        cursor.close()
        db.close()

        return redirect("/")

    cursor.close()
    db.close()

    return "Invalid username or password"


# ===============================
# LOGOUT
# ===============================
@app.route("/logout")
def logout():
    session.clear()
    response = redirect("/login")
    response.headers["Cache-Control"] = "no-store"
    return response


# ===============================
# SIGNUP
# ===============================
@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "GET":
        return render_template("signup.html")

    name = request.form["name"]
    username = request.form["username"]
    password = request.form["password"]
    pin = request.form["pin"]

    account_no = "ACC" + str(random.randint(1000, 9999))

    password_hash = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

    pin_hash = bcrypt.hashpw(
        pin.encode(),
        bcrypt.gensalt()
    ).decode()

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO customers (name, account_no, balance)
        VALUES (%s, %s, %s)
    """, (name, account_no, 0))

    cursor.execute("""
        INSERT INTO users (username, password_hash, pin_hash, account_no)
        VALUES (%s, %s, %s, %s)
    """, (username, password_hash, pin_hash, account_no))

    db.commit()
    cursor.close()
    db.close()

    return redirect("/login")


# ===============================
# DASHBOARD
# ===============================
@app.route("/")
def index():

    if "account_no" not in session:
        return redirect("/login")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    account_no = session["account_no"]

    # Balance
    cursor.execute(
        "SELECT name, balance FROM customers WHERE account_no=%s",
        (account_no,)
    )
    customer = cursor.fetchone()

    full_name = customer["name"] if customer else "User"
    balance = customer["balance"] if customer else 0

    # Average Debit Spending
    cursor.execute("""
        SELECT AVG(amount) AS avg_spending
        FROM transactions
        WHERE account_no=%s AND type='debit'
    """, (account_no,))
    avg_result = cursor.fetchone()
    avg_spending = avg_result["avg_spending"] or 0

    # Largest Transaction
    cursor.execute("""
        SELECT amount, description
        FROM transactions
        WHERE account_no=%s
        ORDER BY amount DESC
        LIMIT 1
    """, (account_no,))
    largest_transaction = cursor.fetchone()

    # All Transactions (latest first)
    cursor.execute("""
        SELECT date, type, amount, description
        FROM transactions
        WHERE account_no=%s
        ORDER BY transaction_id DESC
    """, (account_no,))
    transactions = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "index.html",
        username=session["user"],
        full_name=full_name,
        balance=balance,
        account_no=account_no,
        avg_spending=avg_spending,
        largest_transaction=largest_transaction,
        transactions=transactions
    )


# ===============================
# DEPOSIT
# ===============================
@app.route("/deposit", methods=["POST"])
def deposit():

    if "account_no" not in session:
        return redirect("/login")

    amount = request.form.get("amount")
    description = request.form.get("description") or "Deposit"

    if not amount or float(amount) <= 0:
        return redirect("/")

    amount = float(amount)

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE customers
        SET balance = balance + %s
        WHERE account_no = %s
    """, (amount, session["account_no"]))

    cursor.execute("""
        INSERT INTO transactions
        (account_no, amount, type, date, description)
        VALUES (%s, %s, 'credit', NOW(), %s)
    """, (session["account_no"], amount, description))

    db.commit()
    cursor.close()
    db.close()

    return redirect("/")


# ===============================
# WITHDRAW
# ===============================
@app.route("/withdraw", methods=["POST"])
def withdraw():

    if "account_no" not in session:
        return redirect("/login")

    amount = request.form.get("amount")
    description = request.form.get("description") or "Withdrawal"
    pin = request.form.get("pin")

    if not amount or not pin:
        return redirect("/")

    amount = float(amount)

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Check Balance
    cursor.execute(
        "SELECT balance FROM customers WHERE account_no=%s",
        (session["account_no"],)
    )
    customer = cursor.fetchone()

    if customer["balance"] < amount:
        cursor.close()
        db.close()
        flash("Insufficient balance", "error")
        return redirect("/")

    # Verify PIN
    cursor.execute(
        "SELECT pin_hash FROM users WHERE account_no=%s",
        (session["account_no"],)
    )
    user = cursor.fetchone()

    if not bcrypt.checkpw(
        pin.encode(),
        user["pin_hash"].encode()
    ):
        cursor.close()
        db.close()
        flash("Incorrect PIN", "error")
        return redirect("/")

    # Deduct balance
    cursor.execute("""
        UPDATE customers
        SET balance = balance - %s
        WHERE account_no = %s
    """, (amount, session["account_no"]))

    cursor.execute("""
        INSERT INTO transactions
        (account_no, amount, type, date, description)
        VALUES (%s, %s, 'debit', NOW(), %s)
    """, (session["account_no"], amount, description))

    db.commit()
    cursor.close()
    db.close()

    return redirect("/")


# ===============================
# CHANGE PIN
# ===============================
@app.route("/change_pin", methods=["POST"])
def change_pin():

    if "account_no" not in session:
        return jsonify({"status": "error", "message": "Not logged in"})

    data = request.json
    password = data["password"]
    new_pin = data["new_pin"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT password_hash FROM users WHERE account_no=%s",
        (session["account_no"],)
    )
    user = cursor.fetchone()

    if not bcrypt.checkpw(
        password.encode(),
        user["password_hash"].encode()
    ):
        cursor.close()
        db.close()
        return jsonify({"status": "error", "message": "Incorrect password"})

    new_pin_hash = bcrypt.hashpw(
        new_pin.encode(),
        bcrypt.gensalt()
    ).decode()

    cursor.execute(
        "UPDATE users SET pin_hash=%s WHERE account_no=%s",
        (new_pin_hash, session["account_no"])
    )

    db.commit()
    cursor.close()
    db.close()

    return jsonify({"status": "success", "message": "PIN changed successfully"})


# ===============================
# CHANGE PASSWORD
# ===============================
@app.route("/change_password", methods=["POST"])
def change_password():

    if "account_no" not in session:
        return jsonify({"status": "error", "message": "Not logged in"})

    data = request.json
    current_password = data["current_password"]
    new_password = data["new_password"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT password_hash FROM users WHERE account_no=%s",
        (session["account_no"],)
    )
    user = cursor.fetchone()

    if not bcrypt.checkpw(
        current_password.encode(),
        user["password_hash"].encode()
    ):
        return jsonify({
            "status": "error",
            "message": "Current password incorrect"
        })

    new_hash = bcrypt.hashpw(
        new_password.encode(),
        bcrypt.gensalt()
    ).decode()

    cursor.execute(
        "UPDATE users SET password_hash=%s WHERE account_no=%s",
        (new_hash, session["account_no"])
    )

    db.commit()
    cursor.close()
    db.close()

    return jsonify({
        "status": "success",
        "message": "Password changed successfully"
    })

@app.route("/secure-backoffice-29x7-admin", methods=["GET", "POST"])
def admin_login():

    if "account_no" not in session:
        return redirect("/login")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Check role
    cursor.execute(
        "SELECT role FROM users WHERE account_no=%s",
        (session["account_no"],)
    )
    user = cursor.fetchone()

    if not user or user["role"] != "admin":
        cursor.close()
        db.close()
        return "Access Denied", 403

    cursor.close()
    db.close()

    if request.method == "GET":
        return render_template("admin_login.html")

    # POST → verify master password
    master_password = request.form.get("master_password")

    if master_password != ADMIN_MASTER_PASSWORD:
        return render_template(
            "admin_login.html",
            error="Incorrect Admin Master Password"
        )

    session["admin_verified"] = True
    return redirect("/secure-backoffice-29x7-dashboard")

@app.route("/secure-backoffice-29x7-dashboard")
def secure_admin_dashboard():

    if "account_no" not in session:
        return redirect("/login")

    if not session.get("admin_verified"):
        return redirect("/secure-backoffice-29x7-admin")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # System-wide data
    cursor.execute("SELECT COUNT(*) AS total_users FROM customers")
    total_users = cursor.fetchone()["total_users"]

    cursor.execute("SELECT SUM(balance) AS total_money FROM customers")
    total_money = cursor.fetchone()["total_money"] or 0

    cursor.execute("""
        SELECT name, account_no, balance
        FROM customers
        ORDER BY balance DESC
        LIMIT 5
    """)
    top_accounts = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_money=total_money,
        top_accounts=top_accounts
    )

# ===============================
# RUN APP
# ===============================
if __name__ == "__main__":
    app.run(debug=False)