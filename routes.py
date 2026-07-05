from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, send_file, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import json
import sqlite3
from datetime import datetime

from database import get_db_connection
from models import User
from resume_parser import extract_text_from_pdf
from skill_extractor import extract_skills
from skill_matcher import match_skills
from roadmap_generator import generate_roadmap
from recommendation_engine import get_recommendations
from utils import allowed_file, generate_pdf_report
from gemini_api import get_chat_response_with_gemini

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

# --- AUTHENTICATION ROUTES ---

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template('register.html')
            
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                           (username, email, hashed_password))
            conn.commit()
            
            # Fetch the new user
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user_row = cursor.fetchone()
            user = User(user_row['id'], user_row['username'], user_row['email'], user_row['password'])
            login_user(user)
            
            flash("Registration successful! Welcome to Skill Gap Analysis Agent.", "success")
            return redirect(url_for('main.dashboard'))
        except sqlite3.IntegrityError as e:
            conn.rollback()
            # Determine if username or email is duplicate
            if 'email' in str(e).lower():
                flash("Email already registered. Try logging in.", "danger")
            else:
                flash("Username already taken. Please choose another.", "danger")
        except Exception as e:
            conn.rollback()
            flash(f"Database error: {e}", "danger")
        finally:
            conn.close()
            
    return render_template('register.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username_or_email or not password:
            flash("Please fill in all fields.", "danger")
            return render_template('login.html')
            
        user = User.get_by_username(username_or_email) or User.get_by_email(username_or_email)
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('main.dashboard'))
        else:
            flash("Invalid credentials. Please try again.", "danger")
            
    return render_template('login.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.index'))

# --- CORE DASHBOARD ROUTES ---

@main_bp.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Fetch Resume Info
    cursor.execute("SELECT * FROM resumes WHERE user_id = ? ORDER BY uploaded_at DESC LIMIT 1", (current_user.id,))
    resume = cursor.fetchone()
    
    # 2. Fetch User Skills
    cursor.execute("SELECT skills_list FROM skills WHERE user_id = ?", (current_user.id,))
    skills_row = cursor.fetchone()
    skills_list = []
    if skills_row and skills_row['skills_list']:
        skills_list = [s.strip() for s in skills_row['skills_list'].split(',') if s.strip()]
        
    # 3. Fetch Job Roles List for target selection
    cursor.execute("SELECT role_name FROM job_roles ORDER BY role_name")
    roles = [r['role_name'] for r in cursor.fetchall()]
    
    # 4. Fetch Analysis History
    cursor.execute("SELECT * FROM analysis WHERE user_id = ? ORDER BY created_at DESC", (current_user.id,))
    history = cursor.fetchall()
    
    conn.close()
    
    # Statistics calculations
    total_analyses = len(history)
    avg_match = 0
    if total_analyses > 0:
        avg_match = round(sum(h['match_percentage'] for h in history) / total_analyses, 1)
        
    recent_role = history[0]['job_role'] if total_analyses > 0 else "None"
    recent_match = history[0]['match_percentage'] if total_analyses > 0 else 0
    
    # Notifications List (Mock for Dashboard alerts)
    notifications = []
    if not resume:
        notifications.append({"type": "warning", "message": "You haven't uploaded a resume yet! Head to Upload Resume."})
    if total_analyses == 0:
        notifications.append({"type": "info", "message": "Run your first Skill Gap Analysis to get a learning roadmap."})
    elif recent_match < 60:
        notifications.append({"type": "danger", "message": f"Your readiness match for '{recent_role}' is below 60%. Review your roadmap!"})
    else:
        notifications.append({"type": "success", "message": f"Great! You have a solid {recent_match}% match for '{recent_role}'."})
        
    return render_template(
        'dashboard.html',
        resume=resume,
        skills_count=len(skills_list),
        skills_list=skills_list,
        roles=roles,
        history=history[:5],  # show top 5 on dashboard
        total_analyses=total_analyses,
        avg_match=avg_match,
        recent_role=recent_role,
        recent_match=recent_match,
        notifications=notifications
    )

# --- RESUME UPLOAD & SKILLS ENTER ---

@main_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT skills_list FROM skills WHERE user_id = ?", (current_user.id,))
    skills_row = cursor.fetchone()
    current_skills_str = skills_row['skills_list'] if skills_row else ""
    conn.close()
    
    if request.method == 'POST':
        # Check if manual input or PDF upload
        submission_type = request.form.get('submission_type')
        
        if submission_type == 'manual':
            skills_input = request.form.get('skills_input', '').strip()
            if not skills_input:
                flash("Skills field cannot be empty.", "warning")
                return redirect(url_for('main.upload'))
                
            # Store manual input skills list
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO skills (user_id, skills_list, updated_at) VALUES (?, ?, ?)",
                           (current_user.id, skills_input, datetime.now()))
            conn.commit()
            conn.close()
            flash("Skills profile updated successfully!", "success")
            return redirect(url_for('main.upload'))
            
        elif submission_type == 'upload':
            if 'resume_file' not in request.files:
                flash("No file parts found.", "danger")
                return redirect(url_for('main.upload'))
                
            file = request.files['resume_file']
            if file.filename == '':
                flash("No file selected.", "warning")
                return redirect(url_for('main.upload'))
                
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                # Save resume PDF file
                upload_dir = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_dir, exist_ok=True)
                # Prefix filename with user ID to prevent overlap
                file_basename = f"user_{current_user.id}_{filename}"
                dest_path = os.path.join(upload_dir, file_basename)
                file.save(dest_path)
                
                # Parse PDF to text
                try:
                    extracted_text = extract_text_from_pdf(dest_path)
                    if not extracted_text.strip():
                        flash("Could not extract text from the PDF. Please check if the PDF is scanned/image-only.", "warning")
                        return redirect(url_for('main.upload'))
                except Exception as e:
                    flash(f"Resume parsing error: {e}", "danger")
                    return redirect(url_for('main.upload'))
                    
                # Extract skills from text
                extracted_skills = extract_skills(extracted_text)
                
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Store resume in database
                cursor.execute("INSERT OR REPLACE INTO resumes (user_id, filename, file_path, extracted_text, uploaded_at) VALUES (?, ?, ?, ?, ?)",
                               (current_user.id, filename, dest_path, extracted_text, datetime.now()))
                
                # Update user skills profile
                skills_list_str = ", ".join(extracted_skills)
                cursor.execute("INSERT OR REPLACE INTO skills (user_id, skills_list, updated_at) VALUES (?, ?, ?)",
                               (current_user.id, skills_list_str, datetime.now()))
                
                conn.commit()
                conn.close()
                
                flash(f"Resume parsed! Extracted {len(extracted_skills)} skills successfully.", "success")
                return redirect(url_for('main.upload'))
            else:
                flash("Allowed file type: PDF only.", "danger")
                return redirect(url_for('main.upload'))
                
    return render_template('upload.html', current_skills=current_skills_str)

# --- ANALYZE SKILLS GAP & JOB SELECTION ---

@main_bp.route('/analysis', methods=['GET', 'POST'])
@login_required
def analysis():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user skills
    cursor.execute("SELECT skills_list FROM skills WHERE user_id = ?", (current_user.id,))
    skills_row = cursor.fetchone()
    user_skills_list = []
    if skills_row and skills_row['skills_list']:
        user_skills_list = [s.strip() for s in skills_row['skills_list'].split(',') if s.strip()]
        
    # Get job roles
    cursor.execute("SELECT role_name FROM job_roles ORDER BY role_name")
    roles = [r['role_name'] for r in cursor.fetchall()]
    conn.close()
    
    if request.method == 'POST':
        target_role = request.form.get('target_role')
        if not target_role:
            flash("Please select a target job role.", "warning")
            return redirect(url_for('main.analysis'))
            
        if not user_skills_list:
            flash("Please upload a resume or enter your skills first.", "warning")
            return redirect(url_for('main.upload'))
            
        # Match skills
        match_results = match_skills(user_skills_list, target_role)
        
        # Serialize lists
        matched_str = ", ".join(match_results["matched_skills"])
        missing_str = ", ".join(match_results["missing_skills"])
        extra_str = ", ".join(match_results["extra_skills"])
        
        # 1. Insert into analysis history table
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analysis (user_id, job_role, match_percentage, matched_skills, missing_skills, extra_skills, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (current_user.id, target_role, match_results["match_percentage"], matched_str, missing_str, extra_str, datetime.now()))
        
        analysis_id = cursor.lastrowid
        
        # 2. Generate Recommendations & Roadmap
        recs = get_recommendations(target_role, match_results["missing_skills"], user_skills_list)
        roadmap = generate_roadmap(target_role, match_results["missing_skills"])
        
        # 3. Store Recommendations
        cursor.execute("""
            INSERT OR REPLACE INTO recommendations (analysis_id, certifications, courses, projects, interview_tips, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (analysis_id, json.dumps(recs["certifications"]), json.dumps(recs["courses"]), 
              json.dumps(recs["projects"]), json.dumps(recs["interview_prep_tips"]), datetime.now()))
              
        # 4. Store Learning Roadmap
        cursor.execute("""
            INSERT OR REPLACE INTO learning_roadmap (analysis_id, roadmap_data, created_at)
            VALUES (?, ?, ?)
        """, (analysis_id, json.dumps(roadmap), datetime.now()))
        
        conn.commit()
        conn.close()
        
        flash(f"Skill Gap Analysis completed for {target_role}!", "success")
        return redirect(url_for('main.result', analysis_id=analysis_id))
        
    return render_template('analysis.html', user_skills=user_skills_list, roles=roles)

# --- VIEWS FOR ANALYSIS RESULTS ---

@main_bp.route('/result/<int:analysis_id>')
@login_required
def result(analysis_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch analysis record
    cursor.execute("SELECT * FROM analysis WHERE id = ? AND user_id = ?", (analysis_id, current_user.id))
    analysis_row = cursor.fetchone()
    
    if not analysis_row:
        conn.close()
        flash("Analysis report not found.", "danger")
        return redirect(url_for('main.dashboard'))
        
    # Fetch recommendation record
    cursor.execute("SELECT * FROM recommendations WHERE analysis_id = ?", (analysis_id,))
    recs_row = cursor.fetchone()
    
    conn.close()
    
    # Format lists for display
    matched_skills = [s.strip() for s in analysis_row['matched_skills'].split(',') if s.strip()]
    missing_skills = [s.strip() for s in analysis_row['missing_skills'].split(',') if s.strip()]
    extra_skills = [s.strip() for s in analysis_row['extra_skills'].split(',') if s.strip()]
    
    recs = {}
    if recs_row:
        recs = {
            "certifications": json.loads(recs_row['certifications']),
            "courses": json.loads(recs_row['courses']),
            "projects": json.loads(recs_row['projects']),
            "interview_prep_tips": json.loads(recs_row['interview_tips'])
        }
        
    return render_template(
        'result.html',
        analysis=analysis_row,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        extra_skills=extra_skills,
        recs=recs
    )

@main_bp.route('/roadmap/<int:analysis_id>')
@login_required
def roadmap(analysis_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch analysis metadata
    cursor.execute("SELECT job_role FROM analysis WHERE id = ? AND user_id = ?", (analysis_id, current_user.id))
    analysis_row = cursor.fetchone()
    
    if not analysis_row:
        conn.close()
        flash("Roadmap data not found.", "danger")
        return redirect(url_for('main.dashboard'))
        
    # Fetch roadmap data
    cursor.execute("SELECT roadmap_data FROM learning_roadmap WHERE analysis_id = ?", (analysis_id,))
    roadmap_row = cursor.fetchone()
    conn.close()
    
    roadmap_data = []
    if roadmap_row:
        roadmap_data = json.loads(roadmap_row['roadmap_data'])
        
    return render_template('roadmap.html', analysis_id=analysis_id, job_role=analysis_row['job_role'], roadmap=roadmap_data)

@main_bp.route('/recommendations/<int:analysis_id>')
@login_required
def recommendations(analysis_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch analysis metadata
    cursor.execute("SELECT job_role FROM analysis WHERE id = ? AND user_id = ?", (analysis_id, current_user.id))
    analysis_row = cursor.fetchone()
    
    if not analysis_row:
        conn.close()
        flash("Recommendations data not found.", "danger")
        return redirect(url_for('main.dashboard'))
        
    # Fetch recommendations
    cursor.execute("SELECT * FROM recommendations WHERE analysis_id = ?", (analysis_id,))
    recs_row = cursor.fetchone()
    conn.close()
    
    recs = {}
    if recs_row:
        recs = {
            "certifications": json.loads(recs_row['certifications']),
            "courses": json.loads(recs_row['courses']),
            "projects": json.loads(recs_row['projects']),
            "interview_prep_tips": json.loads(recs_row['interview_tips'])
        }
        
    return render_template('recommendations.html', analysis_id=analysis_id, job_role=analysis_row['job_role'], recs=recs)

# --- PDF REPORT EXPORT ---

@main_bp.route('/export_pdf/<int:analysis_id>')
@login_required
def export_pdf(analysis_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Fetch analysis metadata
    cursor.execute("SELECT * FROM analysis WHERE id = ? AND user_id = ?", (analysis_id, current_user.id))
    analysis_row = cursor.fetchone()
    
    if not analysis_row:
        conn.close()
        flash("Report data not found.", "danger")
        return redirect(url_for('main.dashboard'))
        
    # 2. Fetch recommendations
    cursor.execute("SELECT * FROM recommendations WHERE analysis_id = ?", (analysis_id,))
    recs_row = cursor.fetchone()
    recs = {}
    if recs_row:
        recs = {
            "certifications": json.loads(recs_row['certifications']),
            "courses": json.loads(recs_row['courses']),
            "projects": json.loads(recs_row['projects']),
            "missing_skills_explanation": {s.strip(): f"Required for {analysis_row['job_role']} implementations." for s in analysis_row['missing_skills'].split(',') if s.strip()}
        }
        
    # 3. Fetch roadmap
    cursor.execute("SELECT roadmap_data FROM learning_roadmap WHERE analysis_id = ?", (analysis_id,))
    roadmap_row = cursor.fetchone()
    roadmap = []
    if roadmap_row:
        roadmap = json.loads(roadmap_row['roadmap_data'])
        
    conn.close()
    
    # Define PDF download path
    pdf_filename = f"SkillGapReport_{analysis_id}.pdf"
    pdf_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'reports')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, pdf_filename)
    
    try:
        generate_pdf_report(pdf_path, current_user.username, analysis_row, recs, roadmap)
        return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)
    except Exception as e:
        flash(f"PDF Generation failed: {e}", "danger")
        return redirect(url_for('main.result', analysis_id=analysis_id))

# --- PROFILE PAGE & SETTINGS ---

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (current_user.id,))
    user_info = cursor.fetchone()
    conn.close()
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        new_password = request.form.get('password', '').strip()
        
        if not email:
            flash("Email cannot be empty.", "warning")
            return redirect(url_for('main.profile'))
            
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            if new_password:
                hashed = generate_password_hash(new_password, method='pbkdf2:sha256')
                cursor.execute("UPDATE users SET email = ?, password = ? WHERE id = ?", (email, hashed, current_user.id))
            else:
                cursor.execute("UPDATE users SET email = ? WHERE id = ?", (email, current_user.id))
            conn.commit()
            flash("Profile updated successfully!", "success")
        except sqlite3.IntegrityError:
            conn.rollback()
            flash("Email is already used by another user.", "danger")
        except Exception as e:
            conn.rollback()
            flash(f"Error updating profile: {e}", "danger")
        finally:
            conn.close()
            
        return redirect(url_for('main.profile'))
        
    return render_template('profile.html', user=user_info)

# --- STATIC/INFO PAGES ---

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        # We just flash success since it's a academic demonstration contact page
        flash(f"Thank you, {name}! Your message has been received.", "success")
        return redirect(url_for('main.contact'))
    return render_template('contact.html')

# --- CHAT ASSISTANT API ---

@main_bp.route('/api/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Message content is required"}), 400
        
    user_message = data['message']
    
    # Retrieve current user context (skills & target role)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT skills_list FROM skills WHERE user_id = ?", (current_user.id,))
    skills_row = cursor.fetchone()
    current_skills = [s.strip() for s in skills_row['skills_list'].split(',') if s.strip()] if skills_row else []
    
    # Fetch most recent analysis target role
    cursor.execute("SELECT job_role FROM analysis WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (current_user.id,))
    analysis_row = cursor.fetchone()
    target_role = analysis_row['job_role'] if analysis_row else None
    conn.close()
    
    # Manage session based chat history
    if 'chat_history' not in session:
        session['chat_history'] = []
        
    chat_history = session['chat_history']
    
    # Get Gemini response
    bot_response = get_chat_response_with_gemini(user_message, chat_history, current_skills, target_role)
    
    # Keep history within session
    chat_history.append(("User", user_message))
    chat_history.append(("Career Buddy", bot_response))
    session['chat_history'] = chat_history[-10:]  # cap last 10 messages
    
    return jsonify({"response": bot_response})
