"""
Document Processor - Handles different file types
Install: pip install pypdf2 pillow pytesseract
For OCR on images, also install tesseract: https://github.com/tesseract-ocr/tesseract
"""

import os
from pathlib import Path
from typing import Tuple, Optional

class DocumentProcessor:
    """Process different types of documents and extract text"""
    
    def __init__(self):
        self.supported_types = {
            'text': ['.txt', '.md', '.markdown'],
            'pdf': ['.pdf'],
            'image': ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        }
    
    def get_file_type(self, file_path: str) -> str:
        """Determine the type of file"""
        ext = Path(file_path).suffix.lower()
        
        for file_type, extensions in self.supported_types.items():
            if ext in extensions:
                return file_type
        
        return 'unknown'
    
    def process_text_file(self, file_path: str) -> Tuple[str, str]:
        """Process plain text files"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        title = Path(file_path).stem
        return title, content
    
    def process_pdf_file(self, file_path: str) -> Tuple[str, str]:
        """Process PDF files"""
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                
                # Extract text from all pages
                text_content = []
                for page in pdf_reader.pages:
                    text_content.append(page.extract_text())
                
                content = '\n'.join(text_content)
                title = Path(file_path).stem
                
                return title, content
        except ImportError:
            return Path(file_path).stem, "[PDF content - PyPDF2 not installed]"
    
    def process_image_file(self, file_path: str) -> Tuple[str, str]:
        """Process image files using OCR"""
        try:
            from PIL import Image
            import pytesseract
            
            image = Image.open(file_path)
            content = pytesseract.image_to_string(image)
            title = Path(file_path).stem
            
            if not content.strip():
                content = f"[Image file - no text detected]"
            
            return title, content
        except ImportError:
            return Path(file_path).stem, "[Image content - OCR libraries not installed]"
        except Exception as e:
            return Path(file_path).stem, f"[Image content - error: {str(e)}]"
    
    def process_file(self, file_path: str) -> Optional[Tuple[str, str, str]]:
        """
        Process any supported file type
        Returns: (title, content, file_type) or None if unsupported
        """
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
        
        file_type = self.get_file_type(file_path)
        
        if file_type == 'text':
            title, content = self.process_text_file(file_path)
        elif file_type == 'pdf':
            title, content = self.process_pdf_file(file_path)
        elif file_type == 'image':
            title, content = self.process_image_file(file_path)
        else:
            print(f"Unsupported file type: {Path(file_path).suffix}")
            return None
        
        return title, content, file_type
    
    def process_directory(self, directory: str, recursive: bool = False):
        """
        Process all supported files in a directory
        Returns: list of (file_path, title, content, file_type)
        """
        results = []
        path = Path(directory)
        
        if not path.exists():
            print(f"Directory not found: {directory}")
            return results
        
        # Get all files
        if recursive:
            files = path.rglob('*')
        else:
            files = path.glob('*')
        
        for file_path in files:
            if file_path.is_file():
                result = self.process_file(str(file_path))
                if result:
                    title, content, file_type = result
                    results.append((str(file_path), title, content, file_type))
        
        return results


class ManualNoteCreator:
    """Helper for creating notes directly without files"""
    
    @staticmethod
    def create_note(title: str, content: str) -> Tuple[str, str, str]:
        """Create a note manually"""
        return title, content, 'text'
    
    @staticmethod
    def create_quick_note(content: str) -> Tuple[str, str, str]:
        """Create a quick note with auto-generated title"""
        # Use first line or first 50 chars as title
        lines = content.split('\n')
        title = lines[0][:50] if lines else content[:50]
        title = title.strip()
        
        if not title:
            title = "Quick Note"
        
        return title, content, 'text'


if __name__ == '__main__':
    # Test the processor
    processor = DocumentProcessor()
    
    # Test with manual note
    creator = ManualNoteCreator()
    title, content, ftype = creator.create_note(
        "Test Note",
        "This is a test note to verify the document processor works correctly."
    )
    print(f"Title: {title}")
    print(f"Type: {ftype}")
    print(f"Content: {content[:100]}...")