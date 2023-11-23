import bcrypt
from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3
app = Flask(__name__)
app.secret_key = 'secretkey!'
@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['psw'].encode('utf-8')

        # Hashing the password
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

        conn = sqlite3.connect("securityDatabase.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')  # Password from form, encode to bytes

        conn = sqlite3.connect("securityDatabase.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password, user[0]):  # user[0] is already in bytes
            session['username'] = username
            return redirect(url_for('video_list'))
        else:
            return "Login Failed"

    return render_template('login.html')



@app.route('/video_list')
def video_list():
    return render_template('video_list.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))




if __name__ == '__main__':
    app.run(debug=True)
