import sqlite3
import os
from datetime import datetime

class SecondBrainDB:
    def __init__(self, db_path='second_brain.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                file_type TEXT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT,
                summary TEXT
            )
        ''')
        
        # Create full-text search virtual table
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                title, content, tags, summary,
                content='documents',
                content_rowid='id'
            )
        ''')
        
        # Triggers to keep FTS table in sync
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
                INSERT INTO documents_fts(rowid, title, content, tags, summary)
                VALUES (new.id, new.title, new.content, new.tags, new.summary);
            END
        ''')
        
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
                DELETE FROM documents_fts WHERE rowid = old.id;
            END
        ''')
        
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
                UPDATE documents_fts SET 
                    title = new.title,
                    content = new.content,
                    tags = new.tags,
                    summary = new.summary
                WHERE rowid = new.id;
            END
        ''')
        
        conn.commit()
        conn.close()
        print(f"Database initialized at {self.db_path}")
    
    def add_document(self, title, content, file_type='text', file_path=None, tags=None, summary=None):
        """Add a new document to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tags_str = ','.join(tags) if tags else ''
        
        cursor.execute('''
            INSERT INTO documents (title, content, file_type, file_path, tags, summary)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, content, file_type, file_path, tags_str, summary))
        
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return doc_id
    
    def search_documents(self, query, search_type='fulltext'):
        """Search documents using different methods"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if search_type == 'fulltext':
            # Full-text search
            cursor.execute('''
                SELECT d.* FROM documents d
                JOIN documents_fts ON d.id = documents_fts.rowid
                WHERE documents_fts MATCH ?
                ORDER BY rank
            ''', (query,))
        elif search_type == 'tags':
            # Tag search
            cursor.execute('''
                SELECT * FROM documents
                WHERE tags LIKE ?
                ORDER BY created_at DESC
            ''', (f'%{query}%',))
        else:
            # Simple LIKE search
            cursor.execute('''
                SELECT * FROM documents
                WHERE title LIKE ? OR content LIKE ?
                ORDER BY created_at DESC
            ''', (f'%{query}%', f'%{query}%'))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_all_documents(self, limit=100):
        """Get all documents with optional limit"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM documents
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_document(self, doc_id):
        """Get a specific document by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None
    
    def update_document_tags(self, doc_id, tags, summary=None):
        """Update tags and summary for a document"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tags_str = ','.join(tags) if tags else ''
        
        if summary:
            cursor.execute('''
                UPDATE documents
                SET tags = ?, summary = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (tags_str, summary, doc_id))
        else:
            cursor.execute('''
                UPDATE documents
                SET tags = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (tags_str, doc_id))
        
        conn.commit()
        conn.close()
    
    def delete_document(self, doc_id):
        """Delete a document"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
        conn.commit()
        conn.close()

if __name__ == '__main__':
    # Test the database
    db = SecondBrainDB()
    print("Database setup complete!")