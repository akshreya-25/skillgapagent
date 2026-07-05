import os
from werkzeug.utils import secure_filename
from config import Config
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def allowed_file(filename):
    """Checks if the uploaded file is in the allowed format list (PDF)."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def generate_pdf_report(dest_path, user_name, analysis, recs, roadmap):
    """
    Generates a professional PDF report containing the skill gap analysis details.
    """
    doc = SimpleDocTemplate(dest_path, pagesize=letter,
                            rightMargin=40, leftMargin=40, topMargin=45, bottomMargin=45)
    story = []
    styles = getSampleStyleSheet()

    # Define clean, modern color scheme (Blue/Dark Slate/Gray)
    primary_color = colors.HexColor('#0d6efd')  # Royal Blue
    dark_neutral = colors.HexColor('#212529')   # Slate Dark
    light_neutral = colors.HexColor('#f8f9fa')  # Light Gray
    border_color = colors.HexColor('#dee2e6')   # Soft divider

    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=15
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=dark_neutral,
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#495057')
    )

    bold_body_style = ParagraphStyle(
        'BoldBodyText',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=15,
        bulletIndent=5,
        spaceBefore=2,
        spaceAfter=2
    )

    # Document Header Page Title
    story.append(Paragraph("SKILL GAP ANALYSIS REPORT", title_style))
    story.append(Paragraph("<b>Intelligent AI Career Advisor</b>", body_style))
    story.append(Spacer(1, 15))

    # Metadata Panel (Candidate & Target Role Info)
    meta_data = [
        [Paragraph("Candidate Name:", bold_body_style), Paragraph(user_name, body_style),
         Paragraph("Target Job Role:", bold_body_style), Paragraph(analysis['job_role'], body_style)],
        [Paragraph("Readiness Score:", bold_body_style), Paragraph(f"<b>{analysis['match_percentage']}% Match</b>", bold_body_style),
         Paragraph("Report Generated:", bold_body_style), Paragraph(analysis['created_at'][:10] if 'created_at' in analysis else "Today", body_style)]
    ]
    meta_table = Table(meta_data, colWidths=[110, 150, 110, 150])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_neutral),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-1), 1, border_color),
        ('LINEABOVE', (0,0), (-1,-1), 1, border_color),
        ('LINELEFT', (0,0), (-1,-1), 1, border_color),
        ('LINERIGHT', (0,0), (-1,-1), 1, border_color),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # Skill Gap Summary Section
    story.append(Paragraph("Skill Comparison Summary", section_style))
    
    # Grid containing Matched vs Missing Skills
    matched_list = analysis['matched_skills'].split(',') if analysis['matched_skills'] else []
    missing_list = analysis['missing_skills'].split(',') if analysis['missing_skills'] else []
    
    matched_html = "<br/>".join([f"• {m.strip()}" for m in matched_list if m.strip()]) if matched_list else "None"
    missing_html = "<br/>".join([f"• {m.strip()}" for m in missing_list if m.strip()]) if missing_list else "None"
    
    skills_data = [
        [Paragraph("<b>Matched Skills</b> (Acquired)", bold_body_style), Paragraph("<b>Missing Skills</b> (Requires Action)", bold_body_style)],
        [Paragraph(matched_html, body_style), Paragraph(missing_html, body_style)]
    ]
    skills_table = Table(skills_data, colWidths=[260, 260])
    skills_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#d1e7dd')),  # Soft green
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#f8d7da')),  # Soft red
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINEBELOW', (0,0), (-1,-1), 1, border_color),
        ('LINEABOVE', (0,0), (-1,-1), 1, border_color),
        ('LINELEFT', (0,0), (-1,-1), 1, border_color),
        ('LINERIGHT', (0,0), (-1,-1), 1, border_color),
    ]))
    story.append(skills_table)
    story.append(Spacer(1, 15))

    # Missing Skills Explanations
    if recs and 'missing_skills_explanation' in recs and recs['missing_skills_explanation']:
        story.append(Paragraph("Why the Missing Skills are Critical", section_style))
        for skill, expl in recs['missing_skills_explanation'].items():
            story.append(Paragraph(f"<b>{skill}</b>: {expl}", bullet_style))
        story.append(Spacer(1, 10))

    # Course & Certification Recommendations
    story.append(Paragraph("Recommended Courses & Certifications", section_style))
    if recs and 'certifications' in recs and recs['certifications']:
        story.append(Paragraph("<b>Certifications:</b>", bold_body_style))
        for cert in recs['certifications'][:3]:  # Top 3
            story.append(Paragraph(f"• <b>{cert['name']}</b> issued by {cert.get('issuer', 'Various')} - <i>{cert.get('description', '')}</i>", bullet_style))
        story.append(Spacer(1, 5))
        
    if recs and 'courses' in recs and recs['courses']:
        story.append(Paragraph("<b>Online Courses:</b>", bold_body_style))
        for course in recs['courses'][:3]:  # Top 3
            story.append(Paragraph(f"• <b>{course['title']}</b> ({course.get('provider', 'Coursera')}) - Level: {course.get('level', 'All levels')}", bullet_style))
        story.append(Spacer(1, 10))

    # Project Recommendations
    if recs and 'projects' in recs and recs['projects']:
        story.append(Paragraph("Recommended Up-Skilling Projects", section_style))
        for proj in recs['projects'][:2]:  # Top 2
            story.append(Paragraph(f"• <b>{proj['title']}</b> ({proj.get('difficulty', 'Intermediate')})", bold_body_style))
            story.append(Paragraph(f"Description: {proj.get('description', '')}", bullet_style))
            story.append(Paragraph(f"Tech Stack: {proj.get('tech_stack', '')}", bullet_style))
            story.append(Spacer(1, 5))
        story.append(Spacer(1, 10))

    # Learning Roadmap (First 4 Weeks Summary to fit single page, or simple full description)
    if roadmap:
        story.append(Paragraph("Step-by-Step 8-Week Roadmap Preview", section_style))
        for week in roadmap[:4]:  # Show weeks 1 to 4 in PDF print
            story.append(Paragraph(f"<b>Week {week['week_number']}: {week['title']}</b>", bold_body_style))
            story.append(Paragraph(f"Topics: {', '.join(week['topics'])}", bullet_style))
            story.append(Paragraph(f"Mini-Project: {week.get('mini_project', 'N/A')}", bullet_style))
            story.append(Spacer(1, 3))
        story.append(Paragraph("<i>Refer to the online dashboard for the full 8-week structured roadmap including practices and assignments.</i>", body_style))

    # Build the document
    doc.build(story)
