import google.generativeai as genai
import json
import re
from config import Config

_gemini_api_working = True

def init_gemini():
    """Initializes the Gemini API client if a key is available and working."""
    global _gemini_api_working
    if not _gemini_api_working:
        return False
        
    # Check if key is empty or still set to a template/placeholder value
    key = Config.GEMINI_API_KEY
    if not key or not key.strip() or key.startswith("YOUR_") or "placeholder" in key.lower():
        return False
        
    try:
        genai.configure(api_key=key.strip())
        return True
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        _gemini_api_working = False
        return False

def generate_content(prompt, system_instruction=None):
    """Core function to send a prompt to the Gemini API with a timeout and circuit breaker."""
    global _gemini_api_working
    if not init_gemini():
        return None
    try:
        if system_instruction:
            model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=system_instruction)
        else:
            model = genai.GenerativeModel("gemini-2.5-flash")
            
        # Configure request options with a strict 8-second timeout to prevent server freezes
        response = model.generate_content(
            prompt,
            request_options={"timeout": 8.0}
        )
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        
        # Check if the error is due to an invalid key or authentication blocks
        err_msg = str(e).lower()
        if "api_key" in err_msg or "invalid" in err_msg or "unauthorized" in err_msg or "key not found" in err_msg or "400" in err_msg:
            print("Invalid or inactive Gemini API key detected. Tripping circuit breaker and disabling further API requests.")
            _gemini_api_working = False
            
        return None

def analyze_resume_with_gemini(resume_text):
    """Asks Gemini to extract skills and summarize the resume text in JSON format."""
    system_instruction = "You are a professional recruiting coordinator. Your job is to extract candidate details from resume texts."
    prompt = f"""
    Analyze the following resume text. Extract all identified technical and soft skills, and summarize the candidate's professional profile.
    
    Format your response EXACTLY as a valid JSON object with the following structure:
    {{
        "candidate_name": "Full Name or 'Unknown'",
        "summary": "A 2-3 sentence summary of the candidate's background and experience",
        "skills": ["Skill 1", "Skill 2", "Skill 3", ...]
    }}
    
    Do not add markdown formatting outside the JSON, do not add trailing commas, and ensure it is valid JSON.
    
    Resume Text:
    ---
    {resume_text}
    ---
    """
    
    result = generate_content(prompt, system_instruction)
    if result:
        try:
            # Clean potential markdown JSON syntax
            cleaned = re.sub(r"^```json\s*", "", result.strip())
            cleaned = re.sub(r"\s*```$", "", cleaned)
            return json.loads(cleaned)
        except Exception as e:
            print(f"Failed to parse Gemini resume analysis JSON: {e}. Output was: {result}")
    return None

def get_skill_gap_report_with_gemini(user_skills, target_role, required_skills):
    """Queries Gemini to perform a detailed skill gap analysis."""
    system_instruction = "You are an expert technical recruiter and career consultant."
    prompt = f"""
    Analyze the skill gap for a candidate aiming to become a '{target_role}'.
    Candidate's Current Skills: {', '.join(user_skills)}
    Target Role Required Skills: {', '.join(required_skills)}
    
    Compare the current skills with the target role requirements. Generate a detailed improvement report containing:
    1. An explanation of why the missing skills are critical for the role.
    2. Suggested certifications that would boost the candidate's credibility.
    3. Interview preparation tips tailored to the missing skill areas.
    
    Format your response EXACTLY as a valid JSON object with the following structure:
    {{
        "missing_skills_explanation": {{
            "SkillName1": "Why it is critical...",
            "SkillName2": "Why it is critical..."
        }},
        "recommended_certifications": [
            {{
                "name": "Certification Name",
                "issuer": "Issuing Organization (e.g. AWS, Scrum Alliance)",
                "description": "Short description of why it fits this gap"
            }}
        ],
        "interview_prep_tips": [
            "Tip 1 regarding missing skills",
            "Tip 2 regarding interview questions",
            ...
        ]
    }}
    
    Do not add markdown formatting outside the JSON. Ensure it is valid JSON.
    """
    
    result = generate_content(prompt, system_instruction)
    if result:
        try:
            cleaned = re.sub(r"^```json\s*", "", result.strip())
            cleaned = re.sub(r"\s*```$", "", cleaned)
            return json.loads(cleaned)
        except Exception as e:
            print(f"Failed to parse Gemini skill gap JSON: {e}. Output was: {result}")
    return None

def get_roadmap_with_gemini(target_role, missing_skills):
    """Asks Gemini to generate an 8-week structured roadmap to learn missing skills."""
    system_instruction = "You are an experienced technical mentor and educator."
    prompt = f"""
    Create a highly structured, 8-week learning roadmap for a candidate who wants to transition into a '{target_role}' but is missing these skills: {', '.join(missing_skills)}.
    
    Provide concrete topics, practice plans, mini projects, and assignments for EACH week (Week 1 to Week 8).
    
    Format your response EXACTLY as a valid JSON object with the following structure:
    {{
        "weeks": [
            {{
                "week_number": 1,
                "title": "Week 1 Focus Area Title",
                "topics": ["Topic 1", "Topic 2", ...],
                "practice": "Description of what they should practice on their computer",
                "mini_project": "A small project to build",
                "assignment": "A specific assignment or quiz prompt to complete"
            }},
            ...
            {{
                "week_number": 8,
                "title": "Week 8 Focus Area Title",
                "topics": [...],
                "practice": "...",
                "mini_project": "...",
                "assignment": "..."
            }}
        ]
    }}
    
    Ensure you return exactly 8 weeks. Do not add markdown formatting outside the JSON.
    """
    
    result = generate_content(prompt, system_instruction)
    if result:
        try:
            cleaned = re.sub(r"^```json\s*", "", result.strip())
            cleaned = re.sub(r"\s*```$", "", cleaned)
            return json.loads(cleaned)
        except Exception as e:
            print(f"Failed to parse Gemini roadmap JSON: {e}. Output was: {result}")
    return None

def get_recommendations_with_gemini(target_role, missing_skills):
    """Generates courses, projects, and certifications based on missing skills."""
    system_instruction = "You are a career development specialist."
    prompt = f"""
    Suggest online courses (with hypothetical or realistic titles and platforms like Coursera/Udemy/YouTube) and hands-on projects for a candidate missing these skills: {', '.join(missing_skills)} for the role of '{target_role}'.
    
    Format your response EXACTLY as a valid JSON object with the following structure:
    {{
        "courses": [
            {{
                "title": "Course Title",
                "provider": "Coursera / Udemy / YouTube",
                "url": "https://www.coursera.org/ or https://www.udemy.com/ or https://www.youtube.com/",
                "level": "Beginner / Intermediate / Advanced"
            }}
        ],
        "projects": [
            {{
                "title": "Project Title",
                "description": "Detailed description of the project, goals, and what the student will build.",
                "difficulty": "Beginner / Intermediate / Advanced",
                "tech_stack": "Comma-separated list of technologies"
            }}
        ]
    }}
    
    Do not add markdown formatting outside the JSON. Ensure it is valid JSON.
    """
    
    result = generate_content(prompt, system_instruction)
    if result:
        try:
            cleaned = re.sub(r"^```json\s*", "", result.strip())
            cleaned = re.sub(r"\s*```$", "", cleaned)
            return json.loads(cleaned)
        except Exception as e:
            print(f"Failed to parse Gemini recommendations JSON: {e}. Output was: {result}")
    return None

def get_chat_response_with_gemini(user_message, chat_history, current_skills=None, target_role=None):
    """Handles an interactive career advisor chat session with context."""
    system_instruction = f"""You are 'Career Buddy', an empathetic, intelligent AI Career Advisor.
    Your job is to answer the user's questions about career planning, learning paths, interviews, resumes, and skill gaps.
    
    Context:
    - User's current skills: {', '.join(current_skills) if current_skills else 'Not specified yet'}
    - User's target role: {target_role if target_role else 'Not selected yet'}
    
    Provide helpful, professional, encouraging, and highly specific advice. Avoid generic responses. Keep messages concise and formatted using markdown.
    """
    
    # Build a prompt that includes history
    history_str = ""
    for speaker, msg in chat_history[-6:]:  # Keep last 6 exchanges for context limits
        history_str += f"{speaker}: {msg}\n"
    
    prompt = f"""
    {history_str}
    User: {user_message}
    Career Buddy:"""
    
    response = generate_content(prompt, system_instruction)
    if response:
        return response.strip()
    return "I'm sorry, I am currently facing network issues connecting with my AI core. How else can I assist you with your skills analysis?"
