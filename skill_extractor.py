import re
import json
import os
import spacy
from config import Config

# Global variable to hold spaCy model
nlp = None
try:
    # Try to load the English model
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    print(f"spaCy model 'en_core_web_sm' not found. Falling back to keyword-based matching: {e}")

def load_all_known_skills():
    """Loads all skills present in skills_database.json to use as a baseline."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    skills_json_path = os.path.join(base_dir, 'skills_database.json')
    
    skills_set = set()
    if os.path.exists(skills_json_path):
        try:
            with open(skills_json_path, 'r') as f:
                data = json.load(f)
                for role, skills in data.items():
                    for skill in skills:
                        skills_set.add(skill.strip())
        except Exception as e:
            print(f"Error reading skills database json: {e}")
            
    # Add common general technical terms just in case
    general_tech = {
        "Python", "Java", "C++", "C#", "SQL", "Git", "Docker", "Kubernetes", "Linux", "Windows",
        "HTML", "CSS", "JavaScript", "React", "Node.js", "Express", "Flask", "Django", "FastAPI",
        "MongoDB", "MySQL", "PostgreSQL", "SQLite", "AWS", "Azure", "GCP", "Figma", "Adobe XD",
        "Machine Learning", "Deep Learning", "NLP", "PyTorch", "TensorFlow", "Pandas", "NumPy",
        "Bootstrap", "Tailwind", "REST API", "Microservices", "CI/CD", "Jenkins", "GitHub Actions",
        "Cyber Security", "Penetration Testing", "Cryptography", "SOQL", "Apex", "Figma"
    }
    skills_set.update(general_tech)
    return list(skills_set)

def extract_skills(text):
    """
    Extracts technical and professional skills from the text.
    Uses spaCy for tokenization/noun chunks, combined with regex matcher.
    """
    if not text:
        return []
        
    extracted_skills = set()
    known_skills = load_all_known_skills()
    text_lower = text.lower()
    
    # Method 1: Regex boundary-matching (very robust for list of exact technical keywords)
    for skill in known_skills:
        # Avoid simple short letters matching everywhere unless bounded
        # e.g., 'C' matching inside every word.
        # Handle special characters like C++, C#, .NET
        escaped_skill = re.escape(skill)
        
        # Word boundaries matching for text and special characters
        pattern = r'\b' + escaped_skill + r'\b'
        if '+' in skill or '#' in skill or '.' in skill:
            # Special regex pattern for C++, C#, .NET because boundaries \b fail on non-alphanumeric trailing chars
            pattern = r'(?:^|[\s,;:\(\)])' + escaped_skill + r'(?:$|[\s,;:\(\)])'
            
        if re.search(pattern, text_lower, re.IGNORECASE):
            extracted_skills.add(skill)

    # Method 2: spaCy Noun Chunks (captures extra skill noun groups like "deep reinforcement learning")
    global nlp
    if nlp:
        try:
            doc = nlp(text)
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.strip().lower()
                # If a noun chunk matches one of our known skills (e.g. "software development"), add the standard name
                for skill in known_skills:
                    if skill.lower() == chunk_text or (len(chunk_text) > 3 and chunk_text in skill.lower()):
                        # Check word overlap
                        if skill.lower() in chunk_text:
                            extracted_skills.add(skill)
        except Exception as e:
            print(f"spaCy extraction encountered error: {e}")

    # Deduplicate and sort
    return sorted(list(extracted_skills))

if __name__ == "__main__":
    # Small test harness
    test_text = "I am a Python developer with experience in Django, REST APIs, HTML5, CSS3, C++, and PostgreSQL."
    print("Test text:", test_text)
    print("Extracted skills:", extract_skills(test_text))
