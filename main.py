from flask import Flask, render_template, redirect, url_for, request, flash, session

app = Flask(__name__)
app.secret_key = 'your_very_secret_key'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    # Here you will handle the login logic
    username = request.form['username']
    password = request.form['password']
    if username == "test" and password == "pass":
        # For now, let's redirect to a dummy video list page
        return redirect(url_for('video_list'))
    else:
        flash('Invalid username or password. Please try again.')
        return redirect(url_for('index'))

@app.route('/video_list')
def video_list():
    return render_template('video_list.html')


if __name__ == '__main__':
    app.run(debug=True)
