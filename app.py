from flask import Flask, request, redirect, render_template, url_for
import sqlite3
import string
import random
from datetime import datetime

app = Flask(__name__)

# ---------- DB Setup ----------
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            click_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------- Helper: Generate Short Code ----------
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

# ---------- Routes ----------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['url']
        short_code = generate_short_code()

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Avoid duplicate short_code
        while c.execute("SELECT * FROM urls WHERE short_code = ?", (short_code,)).fetchone():
            short_code = generate_short_code()

        c.execute("INSERT INTO urls (original_url, short_code) VALUES (?, ?)", (original_url, short_code))
        conn.commit()
        conn.close()

        short_url = request.host_url + short_code
        return render_template('index.html', short_url=short_url)

    return render_template('index.html')

@app.route('/<short_code>')
def redirect_short_url(short_code):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    result = c.execute("SELECT original_url, click_count FROM urls WHERE short_code = ?", (short_code,)).fetchone()

    if result:
        original_url, click_count = result
        c.execute("UPDATE urls SET click_count = ? WHERE short_code = ?", (click_count + 1, short_code))
        conn.commit()
        conn.close()
        return redirect(original_url)
    else:
        conn.close()
        return f"URL not found: {short_code}", 404

if __name__ == '__main__':
    app.run(debug=True)
