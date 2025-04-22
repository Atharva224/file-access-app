from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # change this!

UPLOAD_FOLDER = 'uploads'
DATABASE = 'database.db'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- DATABASE SETUP ----------
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS requests (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            email TEXT,
                            reason TEXT,
                            approved INTEGER DEFAULT 0
                        )''')

init_db()

# ---------- ROUTES ----------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    reason = request.form['reason']
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("INSERT INTO requests (name, email, reason) VALUES (?, ?, ?)", (name, email, reason))
    flash('Request submitted! You will receive access if approved.')
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM requests")
                rows = cursor.fetchall()
            return render_template('admin.html', requests=rows)
        else:
            flash("Incorrect login.")
            return redirect(url_for('admin'))
    return render_template('admin_login.html')

@app.route('/approve/<int:request_id>')
def approve(request_id):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("UPDATE requests SET approved = 1 WHERE id = ?", (request_id,))
    return redirect(url_for('admin'))

@app.route('/downloads')
def downloads():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM requests WHERE approved = 1")
        approved_users = cursor.fetchall()
    return render_template('downloads.html', files=os.listdir(UPLOAD_FOLDER), users=approved_users)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
