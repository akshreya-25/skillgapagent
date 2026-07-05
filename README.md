# Skill Gap Analysis Agent — AI Career Advisor

The **Skill Gap Analysis Agent** is a full-stack, AI-powered web application that helps students and job seekers align their capabilities with modern industry expectations. By parsing uploaded PDF resumes, the system extracts core competencies, matches them against target job requirements, calculates job-readiness match scores, suggests course materials/certifications/projects, and structures an 8-week visual timeline learning roadmap.

---

## Project Structure

```
SkillGapAnalysisAgent/
│   app.py                      # Flask Application Entrypoint
│   config.py                   # Global configurations
│   requirements.txt            # Python Dependencies
│   README.md                   # Installation & Setup guide
│   database.py                 # SQLite tables setup & seeding
│   models.py                   # Flask-Login User model class
│   routes.py                   # Flask Blueprint controllers & endpoints
│   resume_parser.py            # PDF text extractor
│   skill_extractor.py          # NLP & regex skill parser
│   skill_matcher.py            # Percentage matching algorithm
│   roadmap_generator.py        # 8-week roadmap generator
│   recommendation_engine.py    # Certification, Course, & Project advisor
│   gemini_api.py               # Google Gemini API connector
│   utils.py                    # PDF report generator helper
│   skills_database.json        # Predefined role-to-skill JSON data
│   courses.json                # Predefined online course recommendations
│   projects.json               # Predefined up-skilling projects
│
├───uploads/                    # Storage for uploaded PDFs & reports
│
├───docs/                       # Technical Documentation
│       DOCUMENTATION.md        # Capstone Project Report
│       PRESENTATION.md         # Final Presentation Slides Outline
│       VIVA.md                 # 50 Viva Questions & Answers
│
├───static/
│   ├───css/
│   │       style.css           # Global Theme & Typography Styles
│   │       dashboard.css       # Core components, charts, & chat styling
│   │
│   └───js/
│           script.js           # AJAX operations, dark mode, & chat actions
│           chart.js            # Chart.js helper adjustments
│
└───templates/
        base.html               # Shared navigation & footer shell
        index.html              # Landing Page
        login.html              # Sign-In Form
        register.html           # Registration Form
        dashboard.html          # Core statistics overview
        upload.html             # Resume PDF dropzone & manual input
        analysis.html           # Job Role selection form
        result.html             # Analysis scores & Chart.js graphs
        roadmap.html            # 8-week visual learning timeline
        recommendations.html    # Suggested courses, certs, & projects
        profile.html            # Email & password updates page
        about.html              # System technical specifications
        contact.html            # User feedback contact page
```

---

## Installation & Setup

### 1. Clone or Extract the Project
Make sure the folder contents are placed in your working directory (e.g. `C:\Users\USER\.gemini\antigravity\scratch\SkillGapAnalysisAgent`).

### 2. Set Up a Virtual Environment
Open PowerShell or command prompt inside the project directory and run:
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate
```

### 3. Install Dependencies
Install all package requirements defined in `requirements.txt`:
```powershell
pip install -r requirements.txt
```
*(Optional) Download spaCy English model:*
```powershell
python -m spacy download en_core_web_sm
```

### 4. Configure Environment Variables
Copy or set up your environment variables. To run with AI features, set your Google Gemini API key:
- **Windows (PowerShell):**
  ```powershell
  $env:GEMINI_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY"
  $env:SECRET_KEY="another-random-string-for-sessions"
  ```
- **Windows (CMD):**
  ```cmd
  set GEMINI_API_KEY=YOUR_ACTUAL_GEMINI_API_KEY
  set SECRET_KEY=another-random-string-for-sessions
  ```

*Note: If no API key is provided, the application runs seamlessly using the built-in local fallback rule engines.*

### 5. Initialize the SQLite Database
Run the setup module to initialize tables and populate seed data:
```powershell
python database.py
```

### 6. Run the Flask Web Server
Start the development server:
```powershell
python app.py
```
The application will launch on your local host port: [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## Deployment Instructions

### Render
1. Create a Web Service linked to your GitHub repo.
2. Select environment: **Python**.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app`
5. Configure Environment variables: Set `GEMINI_API_KEY` and `SECRET_KEY` in settings.

### Railway
1. Push your code to GitHub.
2. Link your Railway project to the repo.
3. Configure `PORT` environment variables (Railway will auto-deploy via its builder).
4. Add variables for `GEMINI_API_KEY` and `SECRET_KEY`.

### PythonAnywhere
1. Create a Python Web App (select Flask).
2. Upload files or pull repository using Git Bash console.
3. Configure the virtual environment path pointing to your dependencies.
4. Update your WSGI file (e.g. `/var/www/username_pythonanywhere_com_wsgi.py`) to import `app` from `app.py`:
   ```python
   import sys
   path = '/home/username/SkillGapAnalysisAgent'
   if path not in sys.path:
       sys.path.append(path)
   from app import app as application
   ```

---

## Future Scope
- **Real-time Job Listings Scraping:** Pull matches from LinkedIn, Indeed, or Glassdoor APIs matching identified missing competencies.
- **Skill Assessment Quizzes:** Implement small test interfaces inside weeks of the roadmap to let users verify acquired competencies.
- **Multi-resume Comparison:** Allow candidates to compare multiple resumes to see which one has the highest compatibility score for specific target fields.
