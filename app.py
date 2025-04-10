from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secure_secret_key_here'  # Use a strong, unique key

# Database connection function (better than global connection)
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="hrishi123",
            database="airline_db",
            port=3306
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Middleware to check login status
def login_required(role=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'username' not in session:
                flash("Please log in first.", "error")
                return redirect('/')
            if role and session.get('role') != role:
                flash("Unauthorized access.", "error")
                return redirect('/')
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__  # Preserve function name for Flask
        return wrapper
    return decorator

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        flash("Username and password are required.", "error")
        return redirect('/')

    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect('/')

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT Role FROM Users WHERE Username=%s AND Password=%s", (username, password))
        role = cursor.fetchone()
        if role:
            session['username'] = username
            session['role'] = role[0]
            flash(f"Welcome, {username}!", "success")
            return redirect('/admin' if role[0] == 'Admin' else '/book_ticket')  # Users go to booking
        else:
            flash("Invalid credentials.", "error")
    except Error as e:
        flash(f"Login error: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash("Logged out successfully.", "success")
    return redirect('/')

@app.route('/admin')
@login_required('Admin')
def admin_dashboard():
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect('/')

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Flight")
        flights = cursor.fetchall()
        return render_template('admin.html', flights=flights)
    except Error as e:
        flash(f"Error fetching flights: {e}", "error")
        return redirect('/admin')
    finally:
        cursor.close()
        conn.close()

@app.route('/user')
@login_required('User')
def user_dashboard():
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect('/')

    try:
        cursor = conn.cursor()
        # Show tickets for the logged-in user (assuming email links to username)
        cursor.execute("""
            SELECT t.* FROM Ticket t
            JOIN Passenger p ON t.PNR = p.PNR
            WHERE p.Email = %s
        """, (f"{session['username']}@example.com",))  # Adjust email logic
        tickets = cursor.fetchall()
        return render_template('user.html', tickets=tickets, username=session['username'])
    except Error as e:
        flash(f"Error fetching tickets: {e}", "error")
        return redirect('/user')
    finally:
        cursor.close()
        conn.close()

@app.route('/book_ticket', methods=['GET', 'POST'])
@login_required('User')
def book_ticket():
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect('/user')

    try:
        cursor = conn.cursor()
        if request.method == 'POST':
            pnr = f"P{int(datetime.now().timestamp()):03d}"[:10]  # Unique PNR (simplified)
            name = request.form.get('name')
            flight_id = request.form.get('flight_id')
            ticket_id = f"T{int(datetime.now().timestamp()):03d}"[:10]  # Unique Ticket_id

            if not all([name, flight_id]):
                flash("All fields are required.", "error")
                return redirect('/book_ticket')

            cursor.execute("SELECT COUNT(*) FROM Flight WHERE Flight_id = %s", (flight_id,))
            if cursor.fetchone()[0] == 0:
                flash("Invalid Flight ID.", "error")
                return redirect('/book_ticket')

            cursor.execute("""
                CALL AddPassengerAndTicket(%s, %s, 25, 'M', %s, '9876543210', 'Test Address', 
                                           %s, %s, 'A1', 'Economy', 5000)
            """, (pnr, name, f"{session['username']}@example.com", ticket_id, flight_id))
            conn.commit()
            flash("Ticket booked successfully!", "success")
            return redirect('/user')

        # GET: Show available flights
        cursor.execute("SELECT Flight_id, Source, Destination, Scheduled_date FROM Flight")
        flights = cursor.fetchall()
        return render_template('book_ticket.html', flights=flights)
    except Error as e:
        conn.rollback()
        flash(f"Booking error: {e}", "error")
        return redirect('/book_ticket')
    finally:
        cursor.close()
        conn.close()

@app.route('/add_flight', methods=['POST'])
@login_required('Admin')
def add_flight():
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect('/admin')

    try:
        cursor = conn.cursor()
        flight_id = request.form.get('flight_id')
        scheduled_date = request.form.get('scheduled_date')
        source = request.form.get('source')
        destination = request.form.get('destination')

        if not all([flight_id, scheduled_date, source, destination]):
            flash("All fields are required.", "error")
            return redirect('/admin')

        cursor.execute("""
            INSERT INTO Flight (Flight_id, Scheduled_date, Source, Destination, Departure_time, 
                                Arrival_time, Capacity, Plane_type, Crew_count, Airline_name)
            VALUES (%s, %s, %s, %s, '08:00:00', '11:00:00', 100, 'Boeing 737', 5, 'AirX')
        """, (flight_id, scheduled_date, source, destination))
        conn.commit()
        flash("Flight added successfully!", "success")
    except Error as e:
        conn.rollback()
        flash(f"Error adding flight: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect('/admin')

@app.route('/delete_flight/<flight_id>')
@login_required('Admin')
def delete_flight(flight_id):
    conn = get_db_connection()
    if conn is None:
        flash("Database connection failed.", "error")
        return redirect('/admin')

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Flight WHERE Flight_id=%s", (flight_id,))
        conn.commit()
        flash("Flight deleted successfully!", "success")
    except Error as e:
        conn.rollback()
        flash(f"Error deleting flight: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)