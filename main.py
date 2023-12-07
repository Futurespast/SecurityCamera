import os
import sqlite3
from datetime import datetime
import bcrypt
from bson import ObjectId
from flask import Flask, render_template, redirect, url_for, request, session, Response, flash
from gridfs import GridFS, NoFile
from pymongo import MongoClient
from retrieve import retrieve_video_from_gridfs
from collections import Counter

app = Flask(__name__)
app.secret_key = 'secretkey!'

def get_database():
    client = MongoClient("mongodb+srv://Mvacc:pwd@iotproject.lkfss1w.mongodb.net/?retryWrites=true&w=majority")
    db = client.your_database_name
    return db

db = get_database()
fs = GridFS(db)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['psw'].encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

        conn = sqlite3.connect("securityDatabase.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        conn.close()

        print(f"User registered: {username}")
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')

        conn = sqlite3.connect("securityDatabase.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            if bcrypt.checkpw(password, user[0]):
                session['username'] = username
                print(f"Login successful for user: {username}")
                return redirect(url_for('video_list'))
            else:
                print(f"Password mismatch for user: {username}")
                return "Login Failed - Password Mismatch"
        else:
            print(f"No user found for username: {username}")
            return "Login Failed - User Not Found"
    return render_template('login.html')

# Link to open the plotting page for all the videos
@app.route('/video_counts_chart')
def video_counts_chart():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        videos = list(db.fs.files.find({}))

        dates = [video['uploadDate'].date() for video in videos]
        date_counts = Counter(dates)

        sorted_dates = sorted(date_counts)
        counts = [date_counts[date] for date in sorted_dates]

        # X axis labels for the date the video(s) were recorded on
        labels = [date.strftime("%Y-%m-%d") for date in sorted_dates]

        return render_template('plot_template.html', labels=labels, data=counts)
    except Exception as e:
        flash(str(e))
        return redirect(url_for('index'))


# Our function to display all the videos on the website
@app.route('/video_list', methods=['GET'])
def video_list():
    if 'username' not in session:
        return redirect(url_for('login'))

    selected_date = request.args.get('date')
    videos = db.fs.files.find()

    if selected_date:
        selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d')
        videos = filter(lambda v: datetime.strptime(v['metadata']['start_time'], '%d-%m-%Y-%H-%M-%S').date() == selected_date_obj.date(), videos)

    video_data = [
        {
            'video_id': str(video['_id']),
            'filename': video['filename'],
            'date': video['metadata'].get('start_time')
        }
        for video in videos
    ]
    return render_template('video_list.html', video_data=video_data)

# Testing Route for Videos | Not to be presented in final project
@app.route('/stream_video/<video_id>')
def stream_video(video_id):
    try:
        video = fs.get(ObjectId(video_id))
        def generate():
            for chunk in video:
                yield chunk

        return Response(generate(), mimetype='video/mp4')
    except NoFile:
        return "Video not found", 404

from flask import after_this_request

@app.route('/download_video/<video_id>')
def download_video(video_id):
    output_path = 'temp_video.mp4'
    try:
        # Call my function in retrieve.py to download the video
        if retrieve_video_from_gridfs(ObjectId(video_id), output_path):
            @after_this_request
            def remove_file(response):
                try:
                    os.remove(output_path)
                except Exception as error:
                    app.logger.error("Error removing or closing downloaded file handle", error)
                return response
            return send_file(output_path, as_attachment=True)
        else:
            return "Failed to retrieve the video.", 404
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return "An error occurred", 500


from flask import send_file

@app.route('/test_video')
def test_video():
    return send_file('/home/mvacc/Documents/VideosForIOT/my_videofileTest3.mp4', mimetype='video/mp4')




@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # app.run(debug=True, threaded=True)
    app.run(host='0.0.0.0', port=8080, debug=True)

