# Second Brain-Personal Knowledge Management System
- An intelligent knowledge management system that automatically tags and organizes your notes, documents, and files using AI.

## Features
- 📝 Add notes directly through the web interface
- 📤 Upload files (TXT, PDF, images with OCR)
- 🏷️ Automatic AI-powered tagging
- 🔍 Full-text search with multiple search modes
- 💾 SQLite database for persistence
- 🎨 Clean, modern web interface (no React needed!)
- 🤖 Local AI processing (no cloud API costs)

## Project Structure

```
second-brain/
├── database.py              # SQLite database management
├── ai_tagger.py            # AI tagging system
├── document_processor.py   # File processing (PDF, images, text)
├── app.py                  # Flask web server
├── generate_samples.py     # Generate 100 sample documents
├── templates/
│   └── index.html         # Web interface
├── uploads/               # Uploaded files storage
└── second_brain.db        # SQLite database (created automatically)
```

## Installation

### Step 1: Install Python Dependencies

```bash
# Basic dependencies (required)
pip install flask sqlite3

# Optional: For PDF support
pip install PyPDF2

# Optional: For image OCR support
pip install pillow pytesseract

# Optional: For advanced AI tagging
pip install transformers torch sentence-transformers
```

**Note:** The system works with just Flask and SQLite. Other dependencies add extra features.

### Step 2: Install Tesseract (Optional - for OCR on images)

- **Windows:** Download from https://github.com/UB-Mannheim/tesseract/wiki
- **Mac:** `brew install tesseract`
- **Linux:** `sudo apt-get install tesseract-ocr`

### Step 3: Set Up Project Structure

Create a folder structure:

```bash
mkdir second-brain
cd second-brain

# Create templates folder
mkdir templates

# Create uploads folder (will be auto-created by app)
mkdir uploads
```

### Step 4: Add Files
1. Save `database.py` in the project folder
2. Save `ai_tagger.py` in the project folder
3. Save `document_processor.py` in the project folder
4. Save `app.py` in the project folder
5. Save `generate_samples.py` in the project folder
6. Save `index.html` in the `templates/` folder

## Quick Start

### Option 1: Start with Sample Data (Recommended)

```bash
# Generate 100 sample documents
python generate_samples.py

# Start the web server
python app.py
```

### Option 2: Start from Scratch

```bash
# Just start the server (database will be created automatically)
python app.py
```

Then open your browser and go to: **http://localhost:5000**

## Usage

### Adding Notes

1. Use the sidebar on the left
2. Enter a title (optional) and content
3. Click "Add Note"
4. AI will automatically generate tags and a summary

### Uploading Files

1. Click "Choose File" in the sidebar
2. Select a supported file (.txt, .md, .pdf, .png, .jpg)
3. Click "Upload & Process"
4. The system extracts text and generates tags

### Searching

1. Type your search query in the search bar
2. Choose search type:
   - **Full Text:** Search in all content (fastest, most accurate)
   - **Tags:** Search specifically in tags
   - **Simple:** Basic keyword search
3. Click "Search" or press Enter

### Viewing Documents

- Click any document card to view full content
- See all tags, creation date, and file type
- Click X to close the modal

## AI Tagging System

The system includes two tagging options:

### Simple Tagger (Default - No ML required)
- Keyword extraction based on frequency
- Pattern matching for common categories
- Fast and lightweight
- No additional dependencies

### Transformer Tagger (Optional - Better accuracy)
- Uses HuggingFace transformers
- More sophisticated categorization
- Requires: `pip install transformers torch`
- Enable in `app.py`: Change `get_tagger(use_transformer=False)` to `True`

## Database Schema

```sql
documents (
  id INTEGER PRIMARY KEY,
  title TEXT,
  content TEXT,
  file_type TEXT,
  file_path TEXT,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  tags TEXT,          -- Comma-separated tags
  summary TEXT        -- Auto-generated summary
)
```

## API Endpoints

- `GET /` - Main web interface
- `GET /api/documents` - Get all documents
- `GET /api/document/<id>` - Get specific document
- `POST /api/search` - Search documents
- `POST /api/add-note` - Add new note
- `POST /api/upload` - Upload file
- `DELETE /api/delete/<id>` - Delete document
- `GET /api/stats` - Get statistics

## Customization

### Change Port

Edit `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Change port here
```

### Modify AI Tagger

Edit `ai_tagger.py` to:
- Add more category patterns
- Adjust tag count limits
- Change keyword extraction logic
- Add custom filtering

### Customize UI

Edit `templates/index.html`:
- Change colors in the `<style>` section
- Modify layout
- Add new features

## Troubleshooting

### Database locked error
- Only one process can write to SQLite at a time
- Close other connections before running

### PDF not processing
- Install PyPDF2: `pip install PyPDF2`
- Some PDFs (scanned images) need OCR

### Images not processing
- Install: `pip install pillow pytesseract`
- Install the Tesseract system binary
- For poor OCR quality, improve image resolution

### Port already in use
- Change port in `app.py`
- Or kill the process using port 5000


## License
- MIT License-Feel free to modify and use for your projects!

## Contributing
- This is a personal project template. Feel free to fork and customize for your needs!

---

**Enjoy your Second Brain! 🧠**
