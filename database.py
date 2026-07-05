import sqlite3
import os
import json
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Resumes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            extracted_text TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create Skills table (Manual / Extracted User Skills)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            skills_list TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create JobRoles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT UNIQUE NOT NULL,
            required_skills TEXT NOT NULL
        )
    ''')
    
    # Create Analysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_role TEXT NOT NULL,
            match_percentage REAL NOT NULL,
            matched_skills TEXT NOT NULL,
            missing_skills TEXT NOT NULL,
            extra_skills TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create Recommendations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER UNIQUE NOT NULL,
            certifications TEXT NOT NULL, -- JSON string
            courses TEXT NOT NULL, -- JSON string
            projects TEXT NOT NULL, -- JSON string
            interview_tips TEXT NOT NULL, -- JSON string
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analysis_id) REFERENCES analysis(id) ON DELETE CASCADE
        )
    ''')
    
    # Create LearningRoadmap table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS learning_roadmap (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id INTEGER UNIQUE NOT NULL,
            roadmap_data TEXT NOT NULL, -- JSON string
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (analysis_id) REFERENCES analysis(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    
    # Seed JobRoles table if empty
    cursor.execute("SELECT COUNT(*) FROM job_roles")
    if cursor.fetchone()[0] == 0:
        seed_job_roles(cursor)
        conn.commit()
        
    conn.close()

def seed_job_roles(cursor):
    # Standard roles and skills dictionary
    default_roles = {
        "Software Developer": "Python, Java, C++, SQL, Git, OOP, Data Structures, Algorithms, REST API, Testing",
        "Python Developer": "Python, OOP, Flask, FastAPI, Django, SQL, Git, REST API, Docker, Linux",
        "Java Developer": "Java, Spring Boot, JPA, Hibernate, SQL, Git, Maven, JUnit, REST API, Microservices",
        "Frontend Developer": "HTML5, CSS3, JavaScript, Bootstrap, Tailwind, React, Vue, Git, Webpack, Responsive Design",
        "Backend Developer": "Node.js, Express, Python, Django, SQL, NoSQL, REST API, Docker, AWS, Git",
        "Full Stack Developer": "HTML5, CSS3, JavaScript, React, Node.js, Express, Python, SQL, REST API, Git",
        "Salesforce Administrator": "Salesforce CRM, SOQL, Apex, Flow Builder, Validation Rules, Reports, Dashboards, Profiles, Roles, Sharing Rules",
        "Data Analyst": "Python, SQL, Excel, Power BI, Statistics, Pandas, NumPy, Visualization, Tableau, Git",
        "AI Engineer": "Python, Machine Learning, Deep Learning, NLP, Gemini API, PyTorch, TensorFlow, Pandas, SQL, Git",
        "Machine Learning Engineer": "Python, Machine Learning, Scikit-Learn, PyTorch, TensorFlow, MLOps, SQL, Git, Pandas, Docker",
        "Cloud Engineer": "AWS, Azure, GCP, Docker, Kubernetes, Terraform, Linux, Networking, IAM, Cloud Security",
        "DevOps Engineer": "Docker, Kubernetes, CI/CD, Jenkins, GitHub Actions, Linux, AWS, Terraform, Bash, Monitoring",
        "Cyber Security Analyst": "Cyber Security, Penetration Testing, Networking, Cryptography, Firewall, SIEM, Linux, OWASP, Risk Assessment",
        "UI UX Designer": "UI UX, Figma, Adobe XD, Wireframing, Prototyping, User Research, Typography, Color Theory, Interaction Design"
    }
    
    for role, skills in default_roles.items():
        cursor.execute("INSERT OR IGNORE INTO job_roles (role_name, required_skills) VALUES (?, ?)", (role, skills))

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
