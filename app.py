from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask import send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, UserMixin, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
import os
import logging
import time
import math

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configurations
app.config['SECRET_KEY'] = 'SOC#12'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Configure mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
test_text = 'TS241464'

# Extensions initialization
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = "strong"

# Logging setup
logging.basicConfig(level=logging.DEBUG)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


@app.route('/')
def index():
    return "Welcome to the Flask API!"


@app.route('/hello')
def api_hello():
    return jsonify(message="Hello from Flask!")


@app.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/process', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        logging.error("File not uploaded")
        return jsonify({"error": "File not uploaded"}), 400

    file = request.files['file']
    file_size = len(file.read())

    # Check for the file size
    if file_size > MAX_FILE_SIZE:
        logging.error(f" File {file.filename} exceeds the allowed limit.")
        return jsonify({"error": "File size exceeds the allowed limit"}), 400

    logging.info(
        f" Received file with name: {file.filename}, type: {file.content_type}, size: {convert_size(file_size)} ")

    if file.filename == '':
        logging.warning("No selected file in the request")
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # Ensure UPLOAD_FOLDER exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        # Save the file with a unique name
        timestamp = int(time.time())
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

        file.seek(0)  # Reset file pointer to the start
        file.save(file_path)
        logging.info(f" File saved at: {file_path}")

        # TO D0: load ML model weights and process media input

        # TO D0: extract text from detected media

        # for testing
        text = test_text

        # Return the file details
        return jsonify({"file_path": file_path, "filename": filename, "unique_filename": unique_filename,
                        "extracted_text": text}), 200

    elif file and (allowed_file(file.filename) is False):
        logging.error(f" File type of {file.filename} not allowed")
        return jsonify({"error": "File type not allowed"}), 400

    else:
        return jsonify({"error": "Unexpected error"}), 500


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    # Check if email or username already exists
    existing_user = User.query.filter((User.email == data['email']) | (User.username == data['username'])).first()
    if existing_user:
        return jsonify({"error": "Email or Username already exists!"}), 409

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha1')
    new_user = User(username=data['username'], email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully!"}), 201


@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()

        if user and check_password_hash(user.password, data['password']):
            login_user(user, remember=True)
            return jsonify(
                {
                    "message": "Login successful",
                    "user": {
                        "username": user.username,
                        "email": user.email
                    }
                }), 200
    else:
        return jsonify({"error": "Invalid content type"}), 415

    return jsonify({"error": "Invalid email or password"}), 401


@app.route('/logout', methods=['POST'])
def logout():
    if not current_user.is_authenticated:
        return jsonify({"error": "Not logged in"}), 401  # or another appropriate status code

    try:
        logout_user()
        session.clear()  # Clear the session as well to remove all stored values
        return jsonify({"message": "Logged out successfully!"}), 200
    except Exception as e:
        # Log the error for debugging purposes
        app.logger.error(f"Logout error: {str(e)}")
        # Return a generic error message to the client
        return jsonify({"error": "Logout failed due to an internal error."}), 500


@app.route('/send-email', methods=['POST'])
def send_email():
    if request.is_json:
        data = request.get_json()
        email = data.get('email')
        if email:
            msg = Message('Sample Email', sender='your-email@example.com', recipients=[email])
            msg.body = 'This is a sample email sent from the Flask backend.'
            mail.send(msg)
            return jsonify({"message": "Email sent successfully"}), 200
        else:
            return jsonify({"error": "Email not provided"}), 400
    else:
        return jsonify({"error": "Invalid content type"}), 415


if __name__ == '__main__':
    app.run(debug=True)
