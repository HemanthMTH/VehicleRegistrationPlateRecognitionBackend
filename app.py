from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import logging
import time

app = Flask(__name__)
CORS(app)

# config storing files
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'mp4'])
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set up logging
logging.basicConfig(level=logging.DEBUG)


@app.route('/')
def index():
    return "Welcome to the Flask API!"

@app.route('/hello')
def api_hello():
    return jsonify(message="Hello from Flask!")
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/process', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        logging.error("File not uploaded")
        return jsonify({"error": "File not uploaded"}), 400

    file = request.files['file']
    file_size = len(file.read())

    # Check for the file size
    if file_size > MAX_FILE_SIZE:
        logging.error(f"File {file.filename} exceeds the allowed limit.")
        return jsonify({"error": "File size exceeds the allowed limit"}), 400

    logging.info(f"Received file with name: {file.filename}, type: {file.content_type}, size: {file_size} bytes")

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
        logging.info(f"File saved at: {file_path}")

        # Here you can add the ML processing code.
        # e.g. result = process_ml_model(file_path)

        return jsonify({"file_path": file_path}), 200
    else:
        logging.error(f"File type of {file.filename} not allowed")
        return jsonify({"error": "File type not allowed"}), 400

    return jsonify({"error": "Unexpected error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
