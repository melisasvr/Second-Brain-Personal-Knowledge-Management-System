"""
AI Tagger using local models
Install: pip install transformers torch sentence-transformers
"""

import re
from typing import List, Tuple

class SimpleTagger:
    """
    A lightweight tagger that uses keyword extraction and simple NLP
    This doesn't require downloading large models
    """
    
    def __init__(self):
        # Common stop words to filter out
        self.stop_words = {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but',
            'in', 'with', 'to', 'for', 'of', 'as', 'by', 'that', 'this',
            'it', 'from', 'be', 'are', 'was', 'were', 'been', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
        
        # Category patterns for common document types
        self.category_patterns = {
            'code': r'\b(function|class|def|import|return|if|else|for|while)\b',
            'meeting': r'\b(meeting|agenda|discussion|attendees|action items)\b',
            'idea': r'\b(idea|concept|brainstorm|think|maybe|could)\b',
            'task': r'\b(todo|task|deadline|complete|finish|done)\b',
            'research': r'\b(study|research|paper|article|analysis|findings)\b',
            'recipe': r'\b(recipe|ingredients|cook|bake|mix|serve)\b',
            'finance': r'\b(budget|money|cost|price|expense|payment|invoice)\b',
            'personal': r'\b(journal|diary|feeling|thought|reflect)\b',
        }
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract important keywords from text"""
        # Convert to lowercase and split into words
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # Filter out stop words
        words = [w for w in words if w not in self.stop_words]
        
        # Count frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:max_keywords]]
        
        return keywords
    
    def detect_categories(self, text: str) -> List[str]:
        """Detect document categories based on content patterns"""
        categories = []
        text_lower = text.lower()
        
        for category, pattern in self.category_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                categories.append(category)
        
        return categories
    
    def generate_tags(self, title: str, content: str, max_tags: int = 8) -> Tuple[List[str], str]:
        """
        Generate tags and a summary for a document
        Returns: (tags, summary)
        """
        # Combine title and content for analysis
        full_text = f"{title} {content}"
        
        # Extract keywords
        keywords = self.extract_keywords(full_text, max_keywords=5)
        
        # Detect categories
        categories = self.detect_categories(full_text)
        
        # Combine and limit tags
        all_tags = categories + keywords
        tags = list(dict.fromkeys(all_tags))[:max_tags]  # Remove duplicates, limit
        
        # Generate simple summary (first 150 chars of content)
        summary = content[:150].strip()
        if len(content) > 150:
            summary += "..."
        
        return tags, summary


class TransformerTagger:
    """
    Advanced tagger using HuggingFace transformers
    Only use this if you want more sophisticated tagging
    Requires: pip install transformers torch sentence-transformers
    """
    
    def __init__(self):
        try:
            from transformers import pipeline
            self.classifier = pipeline("zero-shot-classification", 
                                      model="facebook/bart-large-mnli")
            self.available = True
        except ImportError:
            print("Transformers not available. Install with: pip install transformers torch")
            self.available = False
    
    def generate_tags(self, title: str, content: str, max_tags: int = 8) -> Tuple[List[str], str]:
        """Generate tags using transformer model"""
        if not self.available:
            # Fall back to simple tagger
            simple = SimpleTagger()
            return simple.generate_tags(title, content, max_tags)
        
        # Predefined candidate labels
        candidate_labels = [
            "technology", "business", "personal", "work", "idea",
            "task", "meeting", "research", "finance", "health",
            "education", "travel", "food", "entertainment", "project"
        ]
        
        full_text = f"{title}. {content[:500]}"  # Limit for speed
        
        # Classify
        result = self.classifier(full_text, candidate_labels, multi_label=True)
        
        # Get top scoring labels
        tags = [label for label, score in zip(result['labels'], result['scores']) 
                if score > 0.3][:max_tags]
        
        # Generate summary
        summary = content[:150].strip()
        if len(content) > 150:
            summary += "..."
        
        return tags, summary


# Factory function to get the right tagger
def get_tagger(use_transformer=False):
    """Get appropriate tagger based on availability"""
    if use_transformer:
        tagger = TransformerTagger()
        if tagger.available:
            return tagger
    return SimpleTagger()


if __name__ == '__main__':
    # Test the tagger
    tagger = SimpleTagger()
    
    test_text = """
    Team meeting notes for Q4 planning. We discussed the new product features,
    timeline for development, and budget allocation. Action items: finalize
    requirements by next week, schedule follow-up with engineering team.
    """
    
    tags, summary = tagger.generate_tags("Q4 Planning Meeting", test_text)
    print("Tags:", tags)
    print("Summary:", summary)