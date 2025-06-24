from flask import Flask, request, redirect, render_template, session
import sqlite3
import string
import random

app = Flask(__name__)
app.secret_key = 'secure_key'

def init_db():
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    short TEXT UNIQUE,
                    original TEXT
                )''')
    conn.commit()
    conn.close()

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/', methods=['GET', 'POST'])
def index():
    short_url = None
    if 'history' not in session:
        session['history'] = []

    if request.method == 'POST':
        original_url = request.form['original']
        short_code = generate_short_code()
        
        # Ensure uniqueness
        conn = sqlite3.connect('urls.db')
        c = conn.cursor()
        c.execute("SELECT 1 FROM urls WHERE short = ?", (short_code,))
        while c.fetchone():
            short_code = generate_short_code()
        
        c.execute("INSERT INTO urls (short, original) VALUES (?, ?)", (short_code, original_url))
        conn.commit()
        conn.close()

        short_url = request.host_url + short_code
        session['history'].append((original_url, short_url))

    return render_template('index.html', short_url=short_url, history=session['history'])

@app.route('/<short>')
def redirect_short_url(short):
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute("SELECT original FROM urls WHERE short = ?", (short,))
    result = c.fetchone()
    conn.close()
    if result:
        return redirect(result[0])
    else:
        return "URL not found", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
