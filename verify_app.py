# Test Runner and Diagnostics Script: Skill Gap Analysis Agent
import os
import sqlite3
import unittest
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_connection, init_db
from skill_matcher import match_skills
from roadmap_generator import generate_fallback_roadmap
from recommendation_engine import get_recommendations

class TestSkillGapAgent(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Trigger DB initialization
        init_db()
        
    def test_database_tables(self):
        """Verify that all core SQLite tables exist and can be queried."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        tables = ['users', 'resumes', 'skills', 'job_roles', 'analysis', 'recommendations', 'learning_roadmap']
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            self.assertIsNotNone(cursor.fetchone(), f"Table {table} does not exist.")
            
        # Check if job roles were seeded
        cursor.execute("SELECT COUNT(*) FROM job_roles")
        role_count = cursor.fetchone()[0]
        self.assertGreater(role_count, 0, "JobRoles table was not seeded.")
        
        conn.close()

    def test_auth_hashing(self):
        """Verify password hashing compatibility checks."""
        password = "securepassword123"
        hashed = generate_password_hash(password, method='pbkdf2:sha256')
        self.assertTrue(check_password_hash(hashed, password))
        self.assertFalse(check_password_hash(hashed, "wrongpassword"))

    def test_matching_algorithm(self):
        """Verify the mathematical logic for skill matching calculations."""
        user_skills = ["Python", "Flask", "SQL", "Git", "React", "Docker"]
        target_role = "Python Developer"
        
        # Core skills required for Python Developer: Python, OOP, Flask, FastAPI, Django, SQL, Git, REST API, Docker, Linux (10 skills total)
        # Match list: Python, Flask, SQL, Git, Docker (5 matches out of 10)
        match_results = match_skills(user_skills, target_role)
        
        self.assertEqual(match_results["match_percentage"], 50.0)
        self.assertIn("Python", match_results["matched_skills"])
        self.assertIn("Django", match_results["missing_skills"])
        self.assertIn("React", match_results["extra_skills"])

    def test_fallback_roadmap(self):
        """Verify fallback timeline roadmap distribution yields exactly 8 weeks."""
        missing = ["Docker", "Kubernetes", "CI/CD"]
        roadmap = generate_fallback_roadmap("DevOps Engineer", missing)
        self.assertEqual(len(roadmap), 8)
        
        # Check that we have all required milestone parameters
        for week in roadmap:
            self.assertIn("week_number", week)
            self.assertIn("title", week)
            self.assertIn("topics", week)
            self.assertIn("practice", week)
            self.assertIn("mini_project", week)
            self.assertIn("assignment", week)

    def test_recommendations_retrieval(self):
        """Verify fallback recommended resources load valid details."""
        missing = ["Figma", "UI UX"]
        recs = get_recommendations("UI UX Designer", missing, ["HTML5"])
        
        self.assertGreater(len(recs["courses"]), 0)
        self.assertGreater(len(recs["projects"]), 0)
        self.assertGreater(len(recs["certifications"]), 0)
        self.assertIn("Figma", recs["missing_skills_explanation"])

if __name__ == '__main__':
    print("Running automated verification suite...")
    unittest.main()
