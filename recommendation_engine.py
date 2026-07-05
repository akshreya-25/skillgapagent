import json
import os
from gemini_api import get_recommendations_with_gemini, get_skill_gap_report_with_gemini

def load_local_courses(target_role):
    """Loads courses from courses.json for the target role."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'courses.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                if target_role in data:
                    return data[target_role]
        except Exception as e:
            print(f"Error loading local courses: {e}")
            
    # Generic fallback if role not found
    return [
        {"title": f"Mastering {target_role} Fundamentals", "provider": "Coursera", "url": "https://www.coursera.org", "level": "Beginner"},
        {"title": f"Advanced {target_role} Course", "provider": "Udemy", "url": "https://www.udemy.com", "level": "Intermediate"}
    ]

def load_local_projects(target_role):
    """Loads projects from projects.json for the target role."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'projects.json')
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                if target_role in data:
                    return data[target_role]
        except Exception as e:
            print(f"Error loading local projects: {e}")
            
    # Generic fallback
    return [
        {"title": "Open Source Contributions", "description": "Contribute to open-source libraries matching this career track.", "difficulty": "Intermediate", "tech_stack": "Git, GitHub"},
        {"title": "Personal Portfolio Capstone", "description": "Develop and document a project demonstrating your core engineering abilities.", "difficulty": "Advanced", "tech_stack": "Modern Tools"}
    ]

def generate_local_certifications(target_role, missing_skills):
    """Generates standard certifications based on the target role."""
    certs = []
    
    role_certs = {
        "Software Developer": [
            {"name": "Oracle Certified Associate: Java SE Programmer", "issuer": "Oracle", "description": "Demonstrates core Java programming capability and software developer fundamentals."},
            {"name": "AWS Certified Developer - Associate", "issuer": "Amazon Web Services", "description": "Validates technical expertise in developing and maintaining AWS-based applications."}
        ],
        "Python Developer": [
            {"name": "PCEP (Certified Entry-Level Python Programmer)", "issuer": "Python Institute", "description": "Validates entry-level python fundamentals, variables, and logic controls."},
            {"name": "PCAP (Certified Associate in Python Programming)", "issuer": "Python Institute", "description": "Validates object-oriented programming concepts and library imports."}
        ],
        "Java Developer": [
            {"name": "Oracle Certified Professional: Java SE Developer", "issuer": "Oracle", "description": "Validates high-level Java knowledge, microservices, and databases."},
            {"name": "Spring Certified Professional", "issuer": "VMware/Spring", "description": "Demonstrates spring framework, beans, transactions, and security knowledge."}
        ],
        "Frontend Developer": [
            {"name": "W3C Front-End Web Developer Certificate", "issuer": "W3C", "description": "Covers high-quality HTML5 coding, CSS styling, and responsive Javascript."},
            {"name": "Meta Front-End Developer Professional Certificate", "issuer": "Meta / Coursera", "description": "Covers React foundations, UI/UX, testing, and portfolio creation."}
        ],
        "Backend Developer": [
            {"name": "Meta Back-End Developer Professional Certificate", "issuer": "Meta / Coursera", "description": "Covers Django, Node.js, databases, cloud, and APIs."},
            {"name": "MongoDB Certified Developer Associate", "issuer": "MongoDB", "description": "Validates schema design, index performance, and CRUD queries."}
        ],
        "Full Stack Developer": [
            {"name": "IBM Full Stack Software Developer Certificate", "issuer": "IBM / Coursera", "description": "Covers node, react, cloud deployments, databases, and continuous delivery."},
            {"name": "AWS Certified Developer - Associate", "issuer": "Amazon Web Services", "description": "Great for full stack developers to prove backend cloud deployment expertise."}
        ],
        "Salesforce Administrator": [
            {"name": "Salesforce Certified Administrator", "issuer": "Salesforce", "description": "The baseline credential validating core CRM configurations, custom objects, and user profiles."},
            {"name": "Salesforce Certified Platform App Builder", "issuer": "Salesforce", "description": "Validates custom logic development using point-and-click declarations."}
        ],
        "Data Analyst": [
            {"name": "Google Data Analytics Professional Certificate", "issuer": "Google / Coursera", "description": "Demonstrates mastery in data cleaning, SQL analysis, Tableau, and R scripting."},
            {"name": "Microsoft Certified: Power BI Data Analyst Associate", "issuer": "Microsoft", "description": "Validates modeling, DAX queries, and report publishing skills."}
        ],
        "AI Engineer": [
            {"name": "TensorFlow Developer Certificate", "issuer": "TensorFlow", "description": "Validates neural network design, computer vision, and NLP model architectures."},
            {"name": "Google Cloud Professional Machine Learning Engineer", "issuer": "Google Cloud", "description": "Proves ability to train, monitor, and deploy large-scale ML models on GCP."}
        ],
        "Machine Learning Engineer": [
            {"name": "AWS Certified Machine Learning - Specialty", "issuer": "Amazon Web Services", "description": "Validates data engineering, modeling, analysis, and ML deployment operations."},
            {"name": "DeepLearning.AI TensorFlow Developer", "issuer": "DeepLearning.AI", "description": "Demonstrates regression, classification, CNNs, and sequence processing models."}
        ],
        "Cloud Engineer": [
            {"name": "AWS Certified Solutions Architect - Associate", "issuer": "Amazon Web Services", "description": "The gold standard for validating VPC design, EC2 hosting, and cloud storage structures."},
            {"name": "Google Certified Associate Cloud Engineer", "issuer": "Google Cloud", "description": "Demonstrates node deployment, billing configs, and console navigations."}
        ],
        "DevOps Engineer": [
            {"name": "Certified Kubernetes Administrator (CKA)", "issuer": "Cloud Native Computing Foundation", "description": "Validates installation, node config, and cluster maintenance."},
            {"name": "AWS Certified DevOps Engineer - Professional", "issuer": "Amazon Web Services", "description": "Validates continuous integration pipelines, logging, and security."}
        ],
        "Cyber Security Analyst": [
            {"name": "CompTIA Security+", "issuer": "CompTIA", "description": "The fundamental security credential validating network security, threat detection, and mitigation."},
            {"name": "Certified Information Systems Security Professional (CISSP)", "issuer": "ISC2", "description": "The advanced gold standard for cybersecurity leadership and management."}
        ],
        "UI UX Designer": [
            {"name": "Google UX Design Professional Certificate", "issuer": "Google / Coursera", "description": "Validates Figma skills, user empathy maps, low/high-fidelity wireframes, and design testing."},
            {"name": "NN/g UX Certification", "issuer": "Nielsen Norman Group", "description": "High-credibility professional UX design and research credential."}
        ]
    }
    
    # Return matched role certs, or generic cloud/git certifications
    certs = role_certs.get(target_role, [
        {"name": "Git & GitHub Professional Certificate", "issuer": "GitHub", "description": "Essential certification to prove code versioning and collaborative coding workflows."},
        {"name": "AWS Certified Cloud Practitioner", "issuer": "Amazon Web Services", "description": "Validates general cloud infrastructure knowledge relevant to all tech disciplines."}
    ])
    
    return certs

def generate_local_missing_explanation(missing_skills):
    """Provides local descriptions explaining why each missing skill is necessary."""
    explanations = {}
    for skill in missing_skills:
        explanations[skill] = f"Understanding {skill} is critical for this job role. Employers seek proficiency in this area to ensure efficient project collaboration, robust code quality, and compliance with modern industry standards. Learning this skill will make you highly competitive in technical rounds."
    return explanations

def generate_local_interview_tips(missing_skills):
    """Provides local general interview preparation tips based on missing skills."""
    tips = [
        "Be prepared to explain structural theoretical concepts for any skill listed on your resume.",
        "When asked about a skill you are currently learning, frame it as a proactive study plan: explain that you are taking courses and coding mini-projects to gain hands-on familiarity.",
        "Practice solving algorithmic coding challenges or layout designs on a whiteboard or screen share.",
        "Always use the STAR methodology (Situation, Task, Action, Result) to explain past projects and technical bottlenecks you solved."
    ]
    
    if missing_skills:
        tips.insert(0, f"Expect technical questions testing your core concepts in: {', '.join(missing_skills[:3])}.")
        
    return tips

def get_recommendations(target_role, missing_skills, user_skills):
    """
    Consolidates recommendations (courses, projects, certifications, explanations, tips).
    Integrates Gemini API and falls back to local databases gracefully.
    """
    recommendations_data = {
        "courses": [],
        "projects": [],
        "certifications": [],
        "missing_skills_explanation": {},
        "interview_prep_tips": []
    }
    
    # 1. Try Gemini API for report analysis and recommendations
    gemini_recommendations = None
    gemini_report = None
    
    if missing_skills:
        # Run recommendations fetch
        gemini_recommendations = get_recommendations_with_gemini(target_role, missing_skills)
        gemini_report = get_skill_gap_report_with_gemini(user_skills, target_role, missing_skills)
        
    # 2. Integrate Gemini data if successful
    if gemini_recommendations and "courses" in gemini_recommendations:
        recommendations_data["courses"] = gemini_recommendations["courses"]
        recommendations_data["projects"] = gemini_recommendations["projects"]
    else:
        # Fallback to local JSON files
        recommendations_data["courses"] = load_local_courses(target_role)
        recommendations_data["projects"] = load_local_projects(target_role)
        
    if gemini_report and "recommended_certifications" in gemini_report:
        recommendations_data["certifications"] = gemini_report["recommended_certifications"]
        recommendations_data["missing_skills_explanation"] = gemini_report.get("missing_skills_explanation", {})
        recommendations_data["interview_prep_tips"] = gemini_report.get("interview_prep_tips", [])
    else:
        # Fallback to local logic
        recommendations_data["certifications"] = generate_local_certifications(target_role, missing_skills)
        recommendations_data["missing_skills_explanation"] = generate_local_missing_explanation(missing_skills)
        recommendations_data["interview_prep_tips"] = generate_local_interview_tips(missing_skills)
        
    return recommendations_data
