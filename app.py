from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import send_from_directory
from werkzeug.utils import secure_filename
import os
import logging
import time

app = Flask(__name__)
CORS(app)

# config storing files
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
test_text = 'TS241464'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Set up logging
logging.basicConfig(level=logging.DEBUG)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

        # TO D0: load ML model weights and process media input

        # TO D0: extract text from detected media

        # for testing
        text = test_text

        # Return the file details
        return jsonify({"file_path": file_path, "filename": filename, "unique_filename": unique_filename,
                        "extracted_text": text}), 200

    elif file and (allowed_file(file.filename) is False):
        logging.error(f"File type of {file.filename} not allowed")
        return jsonify({"error": "File type not allowed"}), 400

    else:
        return jsonify({"error": "Unexpected error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
