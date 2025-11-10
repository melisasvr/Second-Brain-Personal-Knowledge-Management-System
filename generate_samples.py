"""
Generate 100 sample documents for testing
Run: python generate_samples.py
"""

from database import SecondBrainDB
from ai_tagger import get_tagger
import random
from datetime import datetime, timedelta

# Sample content templates
SAMPLE_NOTES = [
    # Work/Business
    ("Team Meeting Notes Q4", "Discussed quarterly goals, budget allocation, and new project timelines. Action items: finalize requirements by next week, schedule follow-up with engineering team.", "meeting"),
    ("Project Status Update", "The new feature development is on track. Completed user authentication, working on payment integration. Expected completion in 2 weeks.", "work"),
    ("Business Idea: Food Delivery", "Local organic food delivery service focusing on zero-waste packaging. Target market: environmentally conscious millennials. Potential partnerships with local farms.", "idea"),
    ("Client Feedback Summary", "Client requested additional features: dark mode, export functionality, and better mobile responsiveness. Priority: high. Deadline: end of month.", "work"),
    
    # Personal
    ("Morning Thoughts", "Realized I need to focus more on deep work sessions. Planning to block 2-hour chunks in the morning for important tasks without distractions.", "personal"),
    ("Weekend Plans", "Visit the farmers market, try that new coffee shop downtown, work on personal coding project, read for at least an hour.", "personal"),
    ("Gratitude Journal", "Grateful for supportive friends, good health, interesting work challenges, and the beautiful weather today.", "personal"),
    
    # Learning/Research
    ("Python Best Practices", "Key takeaways: use list comprehensions for readability, follow PEP 8, write docstrings, use virtual environments, implement proper error handling.", "code"),
    ("Machine Learning Notes", "Supervised learning requires labeled data. Common algorithms: linear regression, decision trees, neural networks. Feature engineering is crucial for model performance.", "research"),
    ("Book Summary: Atomic Habits", "Small changes compound over time. Focus on systems rather than goals. Make good habits obvious, attractive, easy, and satisfying.", "research"),
    
    # Tasks/Todo
    ("Week Priorities", "1. Complete project proposal, 2. Review code from team, 3. Prepare presentation, 4. Schedule dentist appointment, 5. Update portfolio website.", "task"),
    ("Shopping List", "Groceries: milk, eggs, bread, vegetables, fruits. Hardware store: light bulbs, batteries. Pharmacy: vitamins, sunscreen.", "task"),
    
    # Creative
    ("Story Idea", "A programmer discovers their code is creating a parallel universe. Every function they write creates new physical laws in this world.", "idea"),
    ("App Concept: Habit Tracker", "Visual habit tracking with streak counters, reminders, analytics. Gamification elements: achievements, levels. Social features: share progress with friends.", "idea"),
    
    # Health/Fitness
    ("Workout Routine", "Monday: Upper body, Wednesday: Lower body, Friday: Full body. Include warm-up, compound exercises, cool-down stretches. Progressive overload each week.", "personal"),
    ("Meal Prep Ideas", "Sunday prep: grilled chicken, roasted vegetables, quinoa, salad ingredients. Portion into containers. Snacks: nuts, fruits, yogurt.", "recipe"),
    
    # Finance
    ("Monthly Budget Review", "Income: salary + freelance. Expenses: rent, utilities, groceries, transport, subscriptions. Savings goal: 20% of income. Investment: index funds.", "finance"),
    ("Investment Research", "Diversification is key. Mix of stocks, bonds, real estate. Long-term strategy. Dollar-cost averaging. Review quarterly.", "finance"),
    
    # Technology
    ("Database Design Principles", "Normalization reduces redundancy. Use indexes for query performance. Consider read vs write optimization. Document schema decisions.", "code"),
    ("API Design Notes", "RESTful principles: use proper HTTP methods, clear resource naming, version your API, implement proper error handling, document endpoints.", "code"),
]

def generate_variations(template_title, template_content, category, count=5):
    """Generate variations of a template"""
    variations = []
    suffixes = ["v1", "v2", "Part 2", "Updated", "Revised", "Notes", "Draft", "Final", "Summary", "Review"]
    
    for i in range(count):
        title = f"{template_title} {random.choice(suffixes)}" if i > 0 else template_title
        # Add some variation to content
        content = template_content
        if i > 0:
            additions = [
                " Additional notes from follow-up discussion.",
                " Updated with new information.",
                " Revised based on feedback.",
                " Extra details added.",
                " Further thoughts on this topic."
            ]
            content += random.choice(additions)
        
        variations.append((title, content, category))
    
    return variations

def generate_sample_documents():
    """Generate 100 sample documents"""
    db = SecondBrainDB()
    tagger = get_tagger(use_transformer=False)
    
    all_samples = []
    
    # Generate variations of each template
    for title, content, category in SAMPLE_NOTES:
        variations = generate_variations(title, content, category, count=random.randint(3, 7))
        all_samples.extend(variations)
    
    # Limit to 100
    all_samples = all_samples[:100]
    
    print(f"Generating {len(all_samples)} sample documents...")
    
    for i, (title, content, category) in enumerate(all_samples, 1):
        # Generate tags and summary
        tags, summary = tagger.generate_tags(title, content)
        
        # Add category to tags if not already present
        if category not in tags:
            tags.insert(0, category)
        
        # Add to database
        doc_id = db.add_document(
            title=title,
            content=content,
            file_type='text',
            tags=tags,
            summary=summary
        )
        
        if i % 10 == 0:
            print(f"Generated {i} documents...")
    
    print(f"\n✅ Successfully generated {len(all_samples)} documents!")
    print(f"Database: {db.db_path}")
    
    # Show some stats
    docs = db.get_all_documents(limit=1000)
    tag_counts = {}
    for doc in docs:
        if doc['tags']:
            for tag in doc['tags'].split(','):
                tag = tag.strip()
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    print("\nTop 10 tags:")
    for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {tag}: {count}")

if __name__ == '__main__':
    generate_sample_documents()