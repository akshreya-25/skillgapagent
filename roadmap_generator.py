import json
from gemini_api import get_roadmap_with_gemini

def generate_roadmap(target_role, missing_skills):
    """
    Generates an 8-week learning roadmap.
    Checks Gemini API first; falls back to rule-based roadmap if API is unavailable or fails.
    """
    # 1. Try Gemini API
    if missing_skills:
        api_result = get_roadmap_with_gemini(target_role, missing_skills)
        if api_result and "weeks" in api_result:
            return api_result["weeks"]
            
    # 2. Local Fallback Generator
    return generate_fallback_roadmap(target_role, missing_skills)

def generate_fallback_roadmap(target_role, missing_skills):
    """
    Builds a robust, structured 8-week learning path locally based on missing skills.
    """
    roadmap = []
    
    # If no missing skills, build an advanced mastery path
    if not missing_skills:
        return [
            {
                "week_number": 1,
                "title": f"Deep Dive into Advanced {target_role} Architecture",
                "topics": ["Design Patterns", "Clean Code Principles", "System Architecture Blueprinting"],
                "practice": "Refactor a past project to use SOLID principles and design patterns.",
                "mini_project": "Design Pattern Showcase App",
                "assignment": "Write a structural review of an open-source codebase."
            },
            {
                "week_number": 2,
                "title": "Performance Optimization & Benchmarking",
                "topics": ["Memory Management", "Caching Strategies", "Concurrency & Threading"],
                "practice": "Write code containing concurrency bottlenecks and measure performance before and after optimization.",
                "mini_project": "High-Throughput Task Processor",
                "assignment": "Implement Redis or in-memory cache to speed up a slow API."
            },
            {
                "week_number": 3,
                "title": "Advanced Database Management",
                "topics": ["Query Optimization", "Indexing Strategies", "Database Sharding & Replication"],
                "practice": "Run EXPLAIN ANALYZE on complex SQL queries, create indexes, and measure improvements.",
                "mini_project": "Normalized Database Schema Migrator",
                "assignment": "Configure a database read/write replica model."
            },
            {
                "week_number": 4,
                "title": "Cloud Services Integration",
                "topics": ["Serverless Computing", "Object Storage API Integration", "Cloud IAM Configurations"],
                "practice": "Deploy a script to run as a serverless function (AWS Lambda / Cloud Functions).",
                "mini_project": "Cloud File-Storage API",
                "assignment": "Configure safe access keys and CORS rules on cloud storage."
            },
            {
                "week_number": 5,
                "title": "Containerization & Orchestration",
                "topics": ["Dockerizing Complex Apps", "Multi-stage Dockerfiles", "Kubernetes Pod Deployments"],
                "practice": "Write Dockerfile and docker-compose.yml files for a multi-service web app.",
                "mini_project": "Containerized Development Environment",
                "assignment": "Deploy containers to a local Kubernetes (Minikube) cluster."
            },
            {
                "week_number": 6,
                "title": "CI/CD & Deployment Automations",
                "topics": ["Automated Testing Pipelines", "GitHub Actions workflows", "Zero-downtime deployment"],
                "practice": "Set up a git pre-commit hook to run linters and unit tests.",
                "mini_project": "Automated Deployment Pipeline",
                "assignment": "Write a GitHub Actions script that builds a container and deploys it on success."
            },
            {
                "week_number": 7,
                "title": "System Security & Hardening",
                "topics": ["OAuth2 / JWT Protocols", "SQL Injection hardens", "CORS & XSS protections"],
                "practice": "Perform a security audit on a local application to verify header settings.",
                "mini_project": "Secure Auth Microservice",
                "assignment": "Implement rate limiting and token validation on all API endpoints."
            },
            {
                "week_number": 8,
                "title": "Expert Capstone & Defense Preparation",
                "topics": ["System Design interviews", "Resume Review for Leadership roles", "Portfolio Presentation"],
                "practice": "Draw system architecture diagrams for high-traffic platforms (e.g. Netflix, Uber).",
                "mini_project": "Production-grade Portfolio Showcase",
                "assignment": "Prepare pitch decks explaining technical decisions in your core capstone projects."
            }
        ]

    # If there are missing skills, distribute them over the first 6 weeks.
    # Weeks 7 and 8 are reserved for integration, testing, deployment, and mock interviews.
    num_missing = len(missing_skills)
    
    # We will distribute the missing skills.
    skills_per_week = max(1, -(-num_missing // 6)) # Ceiling division
    
    for w in range(1, 7):
        start_idx = (w - 1) * skills_per_week
        end_idx = min(start_idx + skills_per_week, num_missing)
        
        # If we have run out of missing skills to assign, fill with deep-dive topics on what was assigned earlier
        if start_idx < num_missing:
            week_skills = missing_skills[start_idx:end_idx]
            title = f"Mastering {', '.join(week_skills)}"
            topics = [f"Fundamentals of {s}" for s in week_skills] + \
                     [f"Intermediate implementations of {s}" for s in week_skills] + \
                     [f"Best practices & configuration for {s}" for s in week_skills]
            practice = f"Complete coding exercises and practice problems focusing heavily on {', '.join(week_skills)}."
            mini_project = f"Small utility using {week_skills[0]} to solve a real-world task."
            assignment = f"Implement a clean, documented coding script utilizing {', '.join(week_skills)} and upload it to Git."
        else:
            # Buffer week if user only has 1 or 2 missing skills
            title = f"Refining {target_role} Core Knowledge"
            topics = ["Advanced concepts", "Code review patterns", "Performance optimization principles"]
            practice = "Perform refactoring on code created in earlier weeks."
            mini_project = "Refactored Utility Suite"
            assignment = "Write test coverage reaching at least 80% for your code from weeks 1-4."
            
        roadmap.append({
            "week_number": w,
            "title": title,
            "topics": topics,
            "practice": practice,
            "mini_project": mini_project,
            "assignment": assignment
        })
        
    # Week 7: Integration & Testing
    roadmap.append({
        "week_number": 7,
        "title": "Comprehensive System Integration & Testing",
        "topics": [
            "Integrating individual modules",
            "Writing Unit & Integration Tests",
            "API Authentication & Middleware Setup"
        ],
        "practice": "Integrate projects built in weeks 1-6 into a single unified application.",
        "mini_project": f"Integrated {target_role} Prototype App",
        "assignment": "Write a testing suite verify endpoints, functions, and database integrity."
    })
    
    # Week 8: Production Deployment & Career Prep
    roadmap.append({
        "week_number": 8,
        "title": "Production Deployment & Job Readiness",
        "topics": [
            "Cloud Deployment (Render/AWS/Vercel)",
            "System Monitoring & Environment Variables",
            f"Interview Questions for {target_role} roles",
            "Resume & Portfolio Polishing"
        ],
        "practice": "Deploy the integrated application online. Create a clear README file with screenshot placeholders.",
        "mini_project": "Public Portfolio & Live App Launch",
        "assignment": "Answer 10 behavioral and 10 technical questions simulating the hiring interview."
    })
    
    return roadmap
