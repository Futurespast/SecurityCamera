from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


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
