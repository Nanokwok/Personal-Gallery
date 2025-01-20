# Image Gallery with ML-Powered Captioning

A Flask-based web application that allows users to create photo albums and automatically generates captions for uploaded images using the BLIP (Salesforce/blip-image-captioning-base) machine learning model.

## Features

- Create and manage multiple photo albums
- Upload multiple images at once
- Automatic image captioning using BLIP ML model
- Responsive web interface
- SQLite database for storage

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Nanokwok/Personal-Gallery.git
cd image-caption
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Configuration

The application uses the following configuration:
- `UPLOAD_FOLDER`: Directory for storing uploaded images (default: `static/uploads/`)
- `MAX_CONTENT_LENGTH`: Maximum file size limit (default: 16MB)
- Supported image formats: PNG, JPG, JPEG, GIF

## Running the Application

1. Initialize the database (automatic on first run)

2. Start the Flask development server:
```bash
flask run
```

3. Access the application at `http://localhost:5000`

## Project Structure

```
image-caption/
├── app.py              # Main application file
├── gallery.db          # SQLite database
├── static/
│   └── uploads/        # Directory for uploaded images
├── templates/          # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── album.html
│   └── upload.html
├── .gitignore
└── README.md
```

## Database Management

To reset the database:
```bash
# Windows PowerShell
Remove-Item gallery.db

# Linux/Mac
rm gallery.db
```
The database will be automatically recreated when you restart the application.
