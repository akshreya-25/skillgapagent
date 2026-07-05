import json
import os
from database import get_db_connection

def load_role_skills_from_db_or_json(role_name):
    """
    Attempts to load the required skills for a role from the database.
    Falls back to reading skills_database.json if not in database.
    """
    # 1. Try DB
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT required_skills FROM job_roles WHERE role_name = ?", (role_name,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return [s.strip() for s in row['required_skills'].split(',') if s.strip()]
    except Exception as e:
        print(f"Error reading role from database: {e}")
        
    # 2. Try JSON
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'skills_database.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                if role_name in data:
                    return [s.strip() for s in data[role_name]]
        except Exception as e:
            print(f"Error reading skills JSON: {e}")
            
    return []

def match_skills(user_skills, target_role):
    """
    Matches user's skills against required skills for target_role.
    Returns a dict with matched_skills, missing_skills, extra_skills, and match_percentage.
    """
    required_skills = load_role_skills_from_db_or_json(target_role)
    
    if not required_skills:
        return {
            "matched_skills": [],
            "missing_skills": [],
            "extra_skills": list(user_skills),
            "match_percentage": 0.0,
            "required_skills": []
        }
        
    # Normalize comparison by lowercasing, but retain original casing for output
    user_skills_lower = {s.lower(): s for s in user_skills}
    required_skills_lower = {s.lower(): s for s in required_skills}
    
    matched_set = set(user_skills_lower.keys()) & set(required_skills_lower.keys())
    missing_set = set(required_skills_lower.keys()) - set(user_skills_lower.keys())
    extra_set = set(user_skills_lower.keys()) - set(required_skills_lower.keys())
    
    matched_skills = [required_skills_lower[k] for k in matched_set]
    missing_skills = [required_skills_lower[k] for k in missing_set]
    extra_skills = [user_skills_lower[k] for k in extra_set]
    
    # Calculate percentage
    total_required = len(required_skills)
    match_count = len(matched_skills)
    match_percentage = round((match_count / total_required) * 100, 1) if total_required > 0 else 0.0
    
    return {
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "extra_skills": sorted(extra_skills),
        "match_percentage": match_percentage,
        "required_skills": required_skills
    }

if __name__ == "__main__":
    # Test matcher
    user = ["Python", "Flask", "CSS3", "SQL"]
    role = "Python Developer"
    print(f"User Skills: {user}")
    print(f"Matching for '{role}':")
    print(match_skills(user, role))
