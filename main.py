import bcrypt
from flask import Flask, render_template, redirect, url_for, request, session, Response
import sqlite3
from bson import ObjectId
from gridfs import GridFS, NoFile
from mongo_connection import get_database, get_gridfs
from pymongo import MongoClient
from flask_cors import CORS






app = Flask(__name__)
CORS(app)
app.secret_key = 'secretkey!'

def get_database():
    client = MongoClient("mongodb+srv://Mvacc:pwd@iotproject.lkfss1w.mongodb.net/?retryWrites=true&w=majority")
    db = client.your_database_name  # Replace with your actual database name
    return db

# Initialize GridFS
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
        
        if user and bcrypt.checkpw(password, user[0]):
            session['username'] = username
            return redirect(url_for('video_list'))
        else:
            return "Login Failed"
    return render_template('login.html')

@app.route('/video_list')
def video_list():
    if 'username' in session:
        videos = db.fs.files.find()
        return render_template('video_list.html', videos=videos)
    else:
        return redirect(url_for('login'))

@app.route('/stream_video/<video_id>')
def stream_video(video_id):
    try:
        # Attempt to get the video file by its ID
        video = fs.get(ObjectId(video_id))

        # Define a generator function that streams the video in chunks
        def generate():
            for chunk in video:
                yield chunk

        # Return a streaming response with the appropriate MIME type
        return Response(generate(), mimetype='video/mp4')
    except NoFile:
        # If the video file doesn't exist or can't be opened, return a 404 error
        return "Video not found", 404


from flask import send_file

@app.route('/test_video')
def test_video():
    return send_file('/home/mvacc/Documents/VideosForIOT/my_videofileTest3.mp4', mimetype='video/mp4')




@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, threaded=True)

