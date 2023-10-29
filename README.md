# VehicleRegistrationPlateRecognitionBackend

# Flask Backend

This Flask backend provides API endpoints for uploading and processing files. It can handle various file types like `.jpg`, `.jpeg`, `.png`, `.mp4` and more.

## Prerequisites

- Python 3.x
- pip

## Installation

1. **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Create a virtual environment (optional but recommended)**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # For Windows: .\venv\Scripts\activate
    ```

3. **Install required packages**:
    ```bash
    pip install -r requirements.txt
    ```

## Running the server

1. **Set up environment variables**:
   - Make sure the `UPLOAD_FOLDER` directory exists or Flask will create it the first time you upload a file.
   
2. **Run the Flask application**:
    ```bash
    python app.py
    ```

   By default, the server will start on `http://localhost:5000`.

## API Endpoints

- **POST** `/process`: Endpoint to upload and process files.

## Contributing

If you want to contribute, please fork the repository and use a feature branch. Pull requests are welcome.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

