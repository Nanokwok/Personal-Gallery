from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from PIL import Image
import logging
import sys
import sqlite3
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize database
    init_db()

    return app


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize BLIP model with error handling
try:
    logger.info("Loading BLIP model and processor...")
    from transformers import BlipProcessor, BlipForConditionalGeneration

    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    logger.info("BLIP model and processor loaded successfully!")
    MODEL_LOADED = True
except Exception as e:
    logger.error(f"Error loading BLIP model: {str(e)}")
    MODEL_LOADED = False


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def init_db():
    try:
        logger.info("Initializing database...")
        conn = sqlite3.connect('gallery.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS images
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             filename TEXT NOT NULL,
             caption TEXT,
             album TEXT,
             upload_date DATETIME)
        ''')
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully!")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise e


def get_db():
    conn = sqlite3.connect('gallery.db')
    conn.row_factory = sqlite3.Row
    return conn


def generate_caption(image_path):
    if not MODEL_LOADED:
        return "Image captioning currently unavailable"
    try:
        raw_image = Image.open(image_path).convert('RGB')
        inputs = processor(raw_image, return_tensors="pt")
        out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)
        return caption
    except Exception as e:
        logger.error(f"Error generating caption: {str(e)}")
        return "Error generating caption"


app = create_app()


@app.route('/')
def index():
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT DISTINCT album FROM images WHERE album IS NOT NULL")
        albums = [row[0] for row in c.fetchall()]
        conn.close()
        return render_template('index.html', albums=albums)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        flash("Error loading albums", "error")
        return render_template('index.html', albums=[])


@app.route('/album/<album_name>')
def view_album(album_name):
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM images WHERE album = ?", (album_name,))
        images = c.fetchall()
        conn.close()
        return render_template('album.html', images=images, album_name=album_name)
    except Exception as e:
        logger.error(f"Error in view_album route: {str(e)}")
        flash("Error loading album", "error")
        return redirect(url_for('index'))


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files[]')
        album_name = request.form.get('album_name', 'Default Album')

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)

                try:
                    file.save(filepath)
                    caption = generate_caption(filepath)

                    conn = get_db()
                    c = conn.cursor()
                    c.execute("""
                        INSERT INTO images (filename, caption, album, upload_date)
                        VALUES (?, ?, ?, ?)
                    """, (new_filename, caption, album_name, datetime.now()))
                    conn.commit()
                    conn.close()

                    flash('File uploaded successfully!')
                except Exception as e:
                    logger.error(f"Error uploading file: {str(e)}")
                    flash('Error uploading file')
                    return redirect(request.url)

        return redirect(url_for('index'))

    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)