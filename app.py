from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import face_recognition
import numpy as np
import os
import base64
from io import BytesIO
from PIL import Image
import uuid

app = Flask(__name__)
app.config.from_object('config.Config')

mysql = MySQL(app)
bcrypt = Bcrypt(app)

# Load known faces
known_face_encodings = []
known_face_names = []

def load_known_faces(directory):
    global known_face_encodings, known_face_names
    known_face_encodings = []
    known_face_names = []
    for user_dir in os.listdir(directory):
        user_path = os.path.join(directory, user_dir)
        if os.path.isdir(user_path):
            for filename in os.listdir(user_path):
                if filename.endswith(".jpg") or filename.endswith(".png"):
                    image_path = os.path.join(user_path, filename)
                    image = face_recognition.load_image_file(image_path)
                    face_encodings = face_recognition.face_encodings(image)
                    if face_encodings:
                        known_face_encodings.append(face_encodings[0])
                        known_face_names.append(user_dir)

load_known_faces('known_faces')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    data_url = data['image']
    password = data['password']
    
    header, encoded = data_url.split(",", 1)
    image_data = base64.b64decode(encoded)
    image = Image.open(BytesIO(image_data)).convert('RGB')
    img_array = np.array(image)

    face_encodings = face_recognition.face_encodings(img_array)
    if face_encodings:
        face_encoding = face_encodings[0]
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            # Verify password with database
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT password FROM users WHERE username=%s", (known_face_names[best_match_index],))
            user_password = cursor.fetchone()
            cursor.close()

            if user_password and bcrypt.check_password_hash(user_password[0], password):
                return jsonify({"status": "success", "user": known_face_names[best_match_index]})
    return jsonify({"status": "fail", "user": "Unknown"})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        image_data = request.form['image']

        # Save image to known_faces directory with unique name
        user_dir = os.path.join('known_faces', username)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        
        unique_filename = f'{uuid.uuid4()}.jpg'
        image_path = os.path.join(user_dir, unique_filename)
        with open(image_path, 'wb') as f:
            f.write(base64.b64decode(image_data.split(",")[1]))

        # Hash password and save to database
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cursor.close()

        # Reload known faces to include the new user
        load_known_faces('known_faces')

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/add-photo', methods=['GET', 'POST'])
def add_photo():
    if request.method == 'POST':
        username = request.form['username']
        photo = request.files['photo']

        # Save photo to user's directory
        user_dir = os.path.join('known_faces', username)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        
        photo.save(os.path.join(user_dir, f'{uuid.uuid4()}.jpg'))

        flash('Photo added to dataset!', 'success')
        return redirect(url_for('add_photo'))

    usernames = [user_dir for user_dir in os.listdir('known_faces') if os.path.isdir(os.path.join('known_faces', user_dir))]
    return render_template('add-photo.html', usernames=usernames)

if __name__ == '__main__':
    app.run(debug=True)
