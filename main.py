from flask import Flask, render_template, redirect, url_for, request
import sqlite3
app = Flask(__name__)

@app.route('/register', methods=['GET'])
def register_page():
    return render_template('register.html')
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['psw']

        conn = sqlite3.connect("securityDatabase.db")
        cursor = conn.cursor()

        # Insert user data into the 'users' table
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

        conn.commit()
        conn.close()

        return redirect(url_for('login'))


@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    # Here you will handle the login logic
    username = request.form['username']
    password = request.form['password']

    # For now, let's redirect to a dummy video list page
    return redirect(url_for('video_list'))


@app.route('/video_list')
def video_list():
    return render_template('video_list.html')






if __name__ == '__main__':
    app.run(debug=True)
