"""
Flask Web Server for Second Brain
Install: pip install flask
Run: python app.py
"""

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import json

# Import our modules
from database import SecondBrainDB
from ai_tagger import get_tagger
from document_processor import DocumentProcessor, ManualNoteCreator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize components
db = SecondBrainDB()
tagger = get_tagger(use_transformer=False)  # Use simple tagger by default
processor = DocumentProcessor()

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get all documents"""
    try:
        docs = db.get_all_documents(limit=100)
        return jsonify({'success': True, 'documents': docs})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/document/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    """Get a specific document"""
    try:
        doc = db.get_document(doc_id)
        if doc:
            return jsonify({'success': True, 'document': doc})
        else:
            return jsonify({'success': False, 'error': 'Document not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def search_documents():
    """Search documents"""
    try:
        data = request.json
        query = data.get('query', '')
        search_type = data.get('search_type', 'fulltext')
        
        if not query:
            return jsonify({'success': False, 'error': 'Query is required'}), 400
        
        results = db.search_documents(query, search_type)
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/add-note', methods=['POST'])
def add_note():
    """Add a new note manually"""
    try:
        data = request.json
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        # Generate title if not provided
        if not title:
            title = content.split('\n')[0][:50] or "Untitled Note"
        
        # Generate tags and summary
        tags, summary = tagger.generate_tags(title, content)
        
        # Add to database
        doc_id = db.add_document(
            title=title,
            content=content,
            file_type='text',
            tags=tags,
            summary=summary
        )
        
        return jsonify({
            'success': True,
            'document_id': doc_id,
            'tags': tags,
            'summary': summary
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and process a file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Process file
        result = processor.process_file(file_path)
        
        if not result:
            return jsonify({'success': False, 'error': 'Unsupported file type'}), 400
        
        title, content, file_type = result
        
        # Generate tags and summary
        tags, summary = tagger.generate_tags(title, content)
        
        # Add to database
        doc_id = db.add_document(
            title=title,
            content=content,
            file_type=file_type,
            file_path=file_path,
            tags=tags,
            summary=summary
        )
        
        return jsonify({
            'success': True,
            'document_id': doc_id,
            'title': title,
            'tags': tags,
            'summary': summary
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete/<int:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Delete a document"""
    try:
        db.delete_document(doc_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        docs = db.get_all_documents(limit=10000)
        
        # Collect tag frequencies
        tag_freq = {}
        for doc in docs:
            if doc['tags']:
                for tag in doc['tags'].split(','):
                    tag = tag.strip()
                    tag_freq[tag] = tag_freq.get(tag, 0) + 1
        
        # Top tags
        top_tags = sorted(tag_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        stats = {
            'total_documents': len(docs),
            'top_tags': [{'tag': tag, 'count': count} for tag, count in top_tags]
        }
        
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Second Brain server...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)