from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort
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

@app.route('/downloads/', defaults={'req_path': ''})
@app.route('/downloads/<path:req_path>')
def downloads(req_path):
    abs_path = os.path.join(UPLOAD_FOLDER, req_path)

    # If path doesn't exist, return 404
    if not os.path.exists(abs_path):
        return abort(404)

    # If it's a file, download it
    if os.path.isfile(abs_path):
        return send_file(abs_path, as_attachment=True)

    # It's a folder, list contents
    files = os.listdir(abs_path)
    files = sorted(files)
    return render_template('downloads.html', files=files, current_path=req_path)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
