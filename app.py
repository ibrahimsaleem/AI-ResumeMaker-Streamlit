import os 
import logging
import uuid
from flask import Flask, request, render_template, render_template_string, jsonify, Response, session, redirect, url_for
from functools import wraps

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False
    logging.warning("Google Generative AI module not found. Using mock implementation.")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Read the default Gemini API key from environment variable (or use a fallback)
DEFAULT_GENAI_API_KEY = os.environ.get("GENAI_API_KEY", "YOUR_DEFAULT_API_KEY")

# Create a default client using the default API key if the module is available
if HAS_GENAI:
    default_client = genai.Client(api_key=DEFAULT_GENAI_API_KEY)
else:
    default_client = None

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Set the passcode
PASSCODE = "ibrahim@aplyease4139"

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("passcode") == PASSCODE:
            session['authenticated'] = True
            return redirect(url_for('index'))
        return render_template("login.html", error="Invalid passcode")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

# In-memory store for resumes. Each entry will be a dict with keys:
# "latex_code": the LaTeX content, "score": the alignment score, "api_key": the API key used (if any)
resume_store = {}

# Load the default LaTeX template
def load_template(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logging.error(f"Error loading template file {file_path}: {str(e)}")
        return ""

# Load prompt template files
def load_prompt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logging.error(f"Error loading prompt file {file_path}: {str(e)}")
        return ""

# Default LaTeX resume template
DEFAULT_LATEX_TEMPLATE = load_template("templates/latex_template.tex")
RESUME_FORMATTER_PROMPT = load_prompt("prompts/resume_formatter.txt")
RESUME_EVALUATOR_PROMPT = load_prompt("prompts/resume_evaluator.txt")
RESUME_OPTIMIZER_PROMPT = load_prompt("prompts/resume_optimizer.txt")

@app.route("/", methods=["GET"]) 
@login_required
def index():
    return render_template("index.html")

@app.route("/generate_resume", methods=["POST"])
@login_required
def generate_resume():
    """Handles the resume generation process using Gemini AI."""
    try:
        resume_content = request.form.get("resume_content")
        job_description = request.form.get("job_description")
        company_name = request.form.get("company_name", "").strip()
        provided_api_key = request.form.get("api_key")
        
        if not resume_content:
            return jsonify({"error": "No resume content provided"}), 400
        
        if not job_description:
            return jsonify({"error": "Job description is required for tailoring"}), 400
        
        # Use the provided API key if available; otherwise, use default
        if HAS_GENAI:
            local_client = genai.Client(api_key=provided_api_key) if provided_api_key else default_client
            if not local_client:
                return jsonify({"error": "No valid API client available"}), 500
        else:
            local_client = None

        try:
            logging.info("Starting resume processing")
            
            # Process the resume content with Gemini
            latex_code = process_with_gemini(local_client, resume_content, job_description)
            if not latex_code:
                return jsonify({"error": "Failed to generate LaTeX code"}), 500
            
            # Evaluate the resume's alignment with the job description
            score, feedback = evaluate_resume_job_match(local_client, latex_code, job_description)
            
            # Analyze skills
            skills_analysis = analyze_skills(local_client, latex_code, job_description)
            if not skills_analysis:
                skills_analysis = {
                    "current_skills": ["Error analyzing skills"],
                    "missing_skills": [],
                    "recommended_skills": [],
                    "latex_skills_section": ""
                }
            
            optimized = False
            optimization_message = ''
            
            # If score is below 8, reprocess to better align with job description
            if score < 8:
                logging.info(f"Initial score {score}/10 is below threshold. Reprocessing resume...")
                latex_code = optimize_resume_for_job(local_client, latex_code, job_description, feedback)
                optimized = True
                optimization_message = 'Optimization was performed automatically because the initial score was low.'
                # Re-evaluate the optimized resume
                score, feedback = evaluate_resume_job_match(local_client, latex_code, job_description)
                logging.info(f"Optimized resume score: {score}/10")
            
            # Generate a unique ID and store the LaTeX code and score
            resume_id = str(uuid.uuid4())
            resume_store[resume_id] = {
                "latex_code": latex_code,
                "score": score,
                "feedback": feedback,
                "api_key": provided_api_key if provided_api_key else None
            }

            response_data = {
                "resume_id": resume_id,
                "latex_code": latex_code,
                "score": score,
                "feedback": feedback,
                "optimized": optimized,
                "optimization_message": optimization_message,
                "skills_analysis": skills_analysis,
                "message": "Resume generated successfully",
                "company_name": company_name
            }

            return jsonify(response_data), 200

        except Exception as e:
            logging.exception("An error occurred during resume generation")
            error_message = str(e) if str(e) else "An unknown error occurred during processing"
            return jsonify({"error": f"Processing error: {error_message}"}), 500

    except Exception as e:
        logging.exception("An error occurred in the generate_resume route")
        return jsonify({"error": "Server error occurred"}), 500

@app.route("/download_latex/<resume_id>", methods=["GET"])
@login_required
def download_latex(resume_id):
    """Allows downloading the LaTeX code as a .tex file."""
    if resume_id not in resume_store:
        return "Resume not found", 404
    
    latex_code = resume_store[resume_id].get("latex_code")
    if not latex_code:
        return "LaTeX code not found", 404
    
    # Return the LaTeX code as a downloadable .tex file
    return Response(
        latex_code,
        mimetype="application/x-tex",
        headers={"Content-Disposition": "attachment;filename=resume.tex"}
    )

def mock_process_resume(resume_content, job_description=None):
    """
    A mock implementation for when the Gemini API is not available.
    This function does basic parsing of the resume content and populates the template.
    If a job description is provided, a tailored note is inserted.
    """
    # Very basic parsing - extract name if it appears to be in the first line
    lines = resume_content.strip().split('\n')
    name = lines[0] if lines else "Your Name"
    
    # Try to extract contact info from first few lines
    contact_info = {
        "email": "your.email@example.com",
        "phone": "Your Phone",
        "linkedin": "Your LinkedIn",
        "github": "Your GitHub",
        "location": "Your Location",
        "website": "Your Website"
    }
    
    for i in range(min(5, len(lines))):
        line = lines[i].lower()
        if '@' in line and '.' in line:
            contact_info["email"] = lines[i].split()[-1]
        elif any(word in line for word in ["phone", "tel", "cell"]):
            contact_info["phone"] = lines[i].split(":")[-1].strip() if ":" in lines[i] else lines[i]
    
    # Create a basic LaTeX document with the extracted information
    latex_code = DEFAULT_LATEX_TEMPLATE.replace("Jake Ryan", name)
    latex_code = latex_code.replace("jake@su.edu", contact_info["email"])
    latex_code = latex_code.replace("123-456-7890", contact_info["phone"])
    
    # If a job description is provided, insert a tailored note after \begin{document}
    if job_description:
        tailored_line = f"\\textit{{Tailored for: {job_description[:100]}{'...' if len(job_description) > 100 else ''}}}\\\\"
        latex_code = latex_code.replace(r"\begin{document}", r"\begin{document}" + "\n" + tailored_line)
    
    return latex_code

def process_with_gemini(client, resume_content, job_description=None):
    """
    Sends the resume content (and optional job description) to Gemini AI for processing and formatting into LaTeX.
    Falls back to mock processing if Gemini is not available.
    """
    if not client or not HAS_GENAI:
        logging.warning("Using mock implementation for resume processing")
        return mock_process_resume(resume_content, job_description)
    
    try:
        logging.info("Sending resume content to Gemini AI for processing...")
        # If a job description is provided, include it in the prompt
        job_desc_section = f"\nHere is the job description to tailor the resume:\n```\n{job_description}\n```" if job_description else ""
        
        prompt = f"""
{RESUME_FORMATTER_PROMPT}

LaTeX Template
{DEFAULT_LATEX_TEMPLATE}


User Resume Content to Format:
```
{resume_content}
```

{job_desc_section}


  
    """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        if not response.text:
            logging.error("Error: No response from Gemini AI.")
            return DEFAULT_LATEX_TEMPLATE
        
        logging.info("Gemini AI processing completed.")
        return response.text.strip()

    except Exception as e:
        logging.exception("Exception occurred while processing with Gemini AI")
        return DEFAULT_LATEX_TEMPLATE


def evaluate_resume_job_match(client, latex_code, job_description):
    """
    Evaluates how well the resume matches the job description.
    Returns a score out of 10 and detailed feedback.
    """
    if not client or not HAS_GENAI:
        # Return a mock score if Gemini is not available
        return 6, "Resume appears well-tailored to the job description."
    
    try:
        logging.info("Evaluating resume-job match...")
        
        prompt = f"""
{RESUME_EVALUATOR_PROMPT}

JOB DESCRIPTION:
```
{job_description}
```
LATEX RESUME:
```
{latex_code}
```
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        
        if not response.text:
            logging.error("Error: No response from Gemini AI for evaluation.")
            return 7, "Unable to evaluate resume-job match."
        
        # Parse the response to extract score and feedback
        response_text = response.text.strip()
        
        # Extract score
        score_line = next((line for line in response_text.split('\n') if line.startswith('SCORE:')), None)
        if score_line:
            try:
                score = int(score_line.split('SCORE:')[1].strip())
                # Ensure score is within range 1-10
                score = max(1, min(10, score))
            except (ValueError, IndexError):
                score = 7  # Default if parsing fails
        else:
            score = 7  # Default if no score line found
        
        # Extract feedback
        feedback_parts = response_text.split('FEEDBACK:')
        if len(feedback_parts) > 1:
            feedback = feedback_parts[1].strip()
        else:
            feedback = "No specific feedback available."
        
        logging.info(f"Resume evaluation completed. Score: {score}/10")
        return score, feedback
        
    except Exception as e:
        logging.exception("Exception occurred during resume evaluation")
        return 7, f"Unable to evaluate resume-job match due to an error: {str(e)}"


def optimize_resume_for_job(client, latex_code, job_description, feedback):
    """
    Optimizes the resume LaTeX code to better match the job description based on feedback.
    """
    if not client or not HAS_GENAI:
        # Return the original code if Gemini is not available
        return latex_code
    
    try:
        logging.info("Optimizing resume for better job alignment...")
        
        prompt = f"""
{RESUME_OPTIMIZER_PROMPT}

LaTeX Template Reference:
Use the provided LaTeX template for formatting but do not return the template itself. Instead, apply its formatting principles to the user's resume content.

LaTeX Template:
{DEFAULT_LATEX_TEMPLATE}

Current LaTeX Resume to Optimize:
{latex_code}

Job Description:
{job_description}

Previous Evaluation Feedback (If Available):
{feedback}
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        
        if not response.text:
            logging.error("Error: No response from Gemini AI for optimization.")
            return latex_code
        
        optimized_latex = response.text.strip()
        logging.info("Resume optimization completed.")
        return optimized_latex
        
    except Exception as e:
        logging.exception("Exception occurred during resume optimization")
        return latex_code

def analyze_skills(client, latex_code, job_description):
    """
    Analyzes the skills section of the resume and compares it with job description requirements.
    Returns a dictionary containing current skills, missing skills, recommended skills, and a formatted LaTeX skills section.
    """
    if not client or not HAS_GENAI:
        return {
            "current_skills": ["Unable to analyze skills without AI service"],
            "missing_skills": [],
            "recommended_skills": [],
            "current_skills_by_category": {},
            "recommended_skills_by_category": {},
            "latex_skills_section": ""
        }
    
    try:
        logging.info("Analyzing skills comparison...")
        
        # First prompt to analyze skills and certifications
        analysis_prompt = f"""
You are a skilled resume analyzer. Analyze the resume and job description carefully.

Your tasks:
1. First, identify the profession type and required skill categories
2. Extract ALL skills from the resume, including those mentioned in project descriptions and experience
3. Compare with job description requirements
4. Recommend additional skills based on job market standards
5. Identify certifications (both current and recommended)

Format your response EXACTLY as follows:

PROFESSION_TYPE:
[Identify the profession type]

SKILL_CATEGORIES:
- [List main skill categories relevant to the profession]

CURRENT_SKILLS:
Technical Skills:
- [List all technical skills found in resume]
Security Skills:
- [List all security-related skills]
[Other Categories]:
- [List skills for each relevant category]

CURRENT_CERTIFICATIONS:
- [List all certifications mentioned in resume]

MISSING_SKILLS:
- [List skills mentioned in job description but missing from resume]

RECOMMENDED_SKILLS:
Technical Skills:
- [List recommended technical skills]
Security Skills:
- [List recommended security skills]
[Other Categories]:
- [List recommended skills by category]

RECOMMENDED_CERTIFICATIONS:
- [List recommended certifications based on job requirements and industry standards]

IMPORTANT INSTRUCTIONS:
1. Include ALL skills mentioned anywhere in the resume
2. Include skills mentioned in project descriptions and work experience
3. Do not mark a skill as missing if it's mentioned anywhere in the resume
4. Group skills logically by category
5. Be thorough in skill extraction - don't miss any skills

LaTeX Resume:
{latex_code}

Job Description:
{job_description}
"""

        analysis_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=analysis_prompt
        )
        
        if not analysis_response.text:
            return {
                "current_skills": ["Error: No response from AI"],
                "missing_skills": [],
                "recommended_skills": [],
                "current_skills_by_category": {},
                "recommended_skills_by_category": {},
                "latex_skills_section": ""
            }
        
        # Parse the analysis response
        response_text = analysis_response.text.strip()
        skills_data = {
            "profession_type": "",
            "skill_categories": [],
            "current_skills": [],
            "current_skills_by_category": {},
            "current_certifications": [],
            "missing_skills": [],
            "recommended_skills": [],
            "recommended_skills_by_category": {},
            "recommended_certifications": []
        }
        
        current_section = None
        current_category = None
        
        for line in response_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if 'PROFESSION_TYPE:' in line:
                current_section = "profession_type"
                skills_data["profession_type"] = line.split('PROFESSION_TYPE:')[1].strip()
            elif 'SKILL_CATEGORIES:' in line:
                current_section = "skill_categories"
            elif 'CURRENT_SKILLS:' in line:
                current_section = "current_skills"
                current_category = None
            elif 'CURRENT_CERTIFICATIONS:' in line:
                current_section = "current_certifications"
            elif 'MISSING_SKILLS:' in line:
                current_section = "missing_skills"
            elif 'RECOMMENDED_SKILLS:' in line:
                current_section = "recommended_skills"
                current_category = None
            elif 'RECOMMENDED_CERTIFICATIONS:' in line:
                current_section = "recommended_certifications"
            elif line.endswith(':') and current_section in ["current_skills", "recommended_skills"]:
                current_category = line[:-1]
                if current_section == "current_skills":
                    skills_data["current_skills_by_category"][current_category] = []
                else:
                    skills_data["recommended_skills_by_category"][current_category] = []
            elif line.startswith('- '):
                skill = line[2:].strip()
                if current_section == "skill_categories":
                    skills_data["skill_categories"].append(skill)
                elif current_section == "current_skills":
                    if current_category:
                        skills_data["current_skills_by_category"][current_category].append(skill)
                    skills_data["current_skills"].append(skill)
                elif current_section == "current_certifications":
                    skills_data["current_certifications"].append(skill)
                elif current_section == "missing_skills":
                    skills_data["missing_skills"].append(skill)
                elif current_section == "recommended_skills":
                    if current_category:
                        skills_data["recommended_skills_by_category"][current_category].append(skill)
                    skills_data["recommended_skills"].append(skill)
                elif current_section == "recommended_certifications":
                    skills_data["recommended_certifications"].append(skill)

        # Second prompt to generate LaTeX skills section
        latex_template = """%-----------SKILLS and CERTIFICATIONS-----------
\\section{Professional Skills \\& Certifications}
 \\begin{itemize}[leftmargin=0.15in, label={}]
    \\small{\\item{
<SKILLS_BY_CATEGORY>
     \\textbf{Certifications}{: <CERTS>}
    }}
 \\end{itemize}"""

        # Prepare skills data for formatting
        current_skills_text = ""
        for category, skills in skills_data["current_skills_by_category"].items():
            if skills:
                current_skills_text += f"{category}:\n- " + "\n- ".join(skills) + "\n\n"

        recommended_skills_text = ""
        for category, skills in skills_data["recommended_skills_by_category"].items():
            if skills:
                recommended_skills_text += f"{category}:\n- " + "\n- ".join(skills) + " (Recommended)\n\n"

        format_prompt = f"""
Based on the following skills and certifications analysis for a {skills_data['profession_type']} professional, 
generate a LaTeX skills section using the exact template below.

Current Skills:
{current_skills_text}

Current Certifications:
{', '.join(skills_data['current_certifications'])}

Recommended Skills:
{recommended_skills_text}

Recommended Certifications:
{', '.join(skills_data['recommended_certifications'])}

Use this exact LaTeX template format:
{latex_template}

Requirements:
1. Replace <SKILLS_BY_CATEGORY> with appropriate category sections
2. For each category, use the format: \\textbf{{Category Name}}{{: skill1, skill2, etc.}} \\\\
3. Include both current and recommended skills/certifications
4. Do not mark recommended skills/certifications with any special suffix
5. Use appropriate line breaks (\\\\) between sections
6. Escape any special LaTeX characters
7. ALWAYS include the Certifications section
8. If no certifications are found, add "No current certifications"
9. Group similar skills together within each category
10. Maintain professional formatting and organization
11. Keep the overall length of the generated skills section (number of lines/items) similar to the original skills section. Do not make the section significantly longer than the original.
"""

        latex_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=format_prompt
        )
        
        if latex_response.text:
            skills_data["latex_skills_section"] = latex_response.text.strip()
        else:
            skills_data["latex_skills_section"] = "Error generating LaTeX skills section"

        return {
            "current_skills": skills_data["current_skills"],
            "missing_skills": skills_data["missing_skills"],
            "recommended_skills": skills_data["recommended_skills"],
            "current_skills_by_category": skills_data["current_skills_by_category"],
            "recommended_skills_by_category": skills_data["recommended_skills_by_category"],
            "latex_skills_section": skills_data["latex_skills_section"]
        }

    except Exception as e:
        logging.exception("Error in analyze_skills")
        return {
            "current_skills": ["Error analyzing skills: " + str(e)],
            "missing_skills": [],
            "recommended_skills": [],
            "current_skills_by_category": {},
            "recommended_skills_by_category": {},
            "latex_skills_section": ""
        }

@app.route("/reoptimize_resume", methods=["POST"])
@login_required
def reoptimize_resume():
    try:
        latex_code = request.form.get("latex_code")
        job_description = request.form.get("job_description")
        feedback = request.form.get("feedback")
        provided_api_key = request.form.get("api_key")

        if not latex_code or not job_description:
            return jsonify({"error": "Missing required fields."}), 400

        if HAS_GENAI:
            local_client = genai.Client(api_key=provided_api_key) if provided_api_key else default_client
            if not local_client:
                return jsonify({"error": "No valid API client available"}), 500
        else:
            local_client = None

        try:
            # Re-optimize the resume
            optimized_latex = optimize_resume_for_job(local_client, latex_code, job_description, feedback)
            if not optimized_latex:
                return jsonify({"error": "Failed to optimize resume"}), 500
                
            # Re-evaluate
            score, new_feedback = evaluate_resume_job_match(local_client, optimized_latex, job_description)
            
            # Generate a new resume_id for download
            resume_id = str(uuid.uuid4())
            resume_store[resume_id] = {
                "latex_code": optimized_latex,
                "score": score,
                "feedback": new_feedback,
                "api_key": provided_api_key if provided_api_key else None
            }

            response_data = {
                "resume_id": resume_id,
                "latex_code": optimized_latex,
                "score": score,
                "feedback": new_feedback,
                "optimized": True,
                "optimization_message": 'Re-optimization was performed by user request.',
                "message": "Resume re-optimized successfully"
            }

            return jsonify(response_data), 200

        except Exception as e:
            logging.exception("An error occurred during re-optimization")
            error_message = str(e) if str(e) else "An unknown error occurred during re-optimization"
            return jsonify({"error": f"Processing error: {error_message}"}), 500

    except Exception as e:
        logging.exception("An error occurred in the reoptimize_resume route")
        return jsonify({"error": "Server error occurred"}), 500

@app.route("/reanalyze_skills", methods=["POST"])
@login_required
def reanalyze_skills():
    try:
        latex_code = request.form.get("latex_code")
        job_description = request.form.get("job_description")
        provided_api_key = request.form.get("api_key")

        if not latex_code or not job_description:
            return jsonify({"error": "Missing required fields."}), 400

        if HAS_GENAI:
            local_client = genai.Client(api_key=provided_api_key) if provided_api_key else default_client
            if not local_client:
                return jsonify({"error": "No valid API client available"}), 500
        else:
            local_client = None

        try:
            # Re-analyze skills
            skills_analysis = analyze_skills(local_client, latex_code, job_description)
            if not skills_analysis:
                return jsonify({"error": "Failed to analyze skills"}), 500

            return jsonify({
                "skills_analysis": skills_analysis,
                "message": "Skills re-analyzed successfully"
            }), 200

        except Exception as e:
            logging.exception("An error occurred during skills re-analysis")
            error_message = str(e) if str(e) else "An unknown error occurred during skills analysis"
            return jsonify({"error": f"Processing error: {error_message}"}), 500

    except Exception as e:
        logging.exception("An error occurred in the reanalyze_skills route")
        return jsonify({"error": "Server error occurred"}), 500

@app.route("/regenerate_skills_latex", methods=["POST"])
@login_required
def regenerate_skills_latex():
    try:
        skills_data = request.get_json()
        provided_api_key = request.form.get("api_key")

        if not skills_data:
            return jsonify({"error": "Missing skills data."}), 400

        if HAS_GENAI:
            local_client = genai.Client(api_key=provided_api_key) if provided_api_key else default_client
            if not local_client:
                return jsonify({"error": "No valid API client available"}), 500
        else:
            local_client = None

        try:
            # LaTeX template for skills section
            latex_template = """%-----------SKILLS and CERTIFICATIONS-----------
\\section{Professional Skills \\& Certifications}
 \\begin{itemize}[leftmargin=0.15in, label={}]
    \\small{\\item{
<SKILLS_BY_CATEGORY>
     \\textbf{Certifications}{: <CERTS>}
    }}
 \\end{itemize}"""

            # Prepare skills data for formatting
            current_skills_text = ""
            for category, skills in skills_data.get("current_skills_by_category", {}).items():
                if skills:
                    current_skills_text += f"{category}:\n- " + "\n- ".join(skills) + "\n\n"

            recommended_skills_text = ""
            for category, skills in skills_data.get("recommended_skills_by_category", {}).items():
                if skills:
                    recommended_skills_text += f"{category}:\n- " + "\n- ".join(skills) + " (Recommended)\n\n"

            format_prompt = f"""
Based on the following skills and certifications analysis for a {skills_data.get('profession_type', '')} professional, 
generate a LaTeX skills section using the exact template below.

Current Skills:
{current_skills_text}

Current Certifications:
{', '.join(skills_data.get('current_certifications', []))}

Recommended Skills:
{recommended_skills_text}

Recommended Certifications:
{', '.join(skills_data.get('recommended_certifications', []))}

Use this exact LaTeX template format:
{latex_template}

Requirements:
1. Replace <SKILLS_BY_CATEGORY> with appropriate category sections
2. For each category, use the format: \\textbf{{Category Name}}{{: skill1, skill2, etc.}} \\\\
3. Include both current and recommended skills/certifications
4. Mark recommended skills/certifications with "(Recommended)" suffix
5. Use appropriate line breaks (\\\\) between sections
6. Escape any special LaTeX characters
7. ALWAYS include the Certifications section
8. If no certifications are found, add "No current certifications"
9. Group similar skills together within each category
10. Maintain professional formatting and organization
11. Keep the overall length of the generated skills section (number of lines/items) similar to the original skills section. Do not make the section significantly longer than the original.
"""

            latex_response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=format_prompt
            )
            
            if not latex_response.text:
                return jsonify({"error": "Failed to generate LaTeX skills section"}), 500

            return jsonify({
                "latex_skills_section": latex_response.text.strip(),
                "message": "Skills LaTeX section regenerated successfully"
            }), 200

        except Exception as e:
            logging.exception("An error occurred during LaTeX skills regeneration")
            error_message = str(e) if str(e) else "An unknown error occurred during LaTeX generation"
            return jsonify({"error": f"Processing error: {error_message}"}), 500

    except Exception as e:
        logging.exception("An error occurred in the regenerate_skills_latex route")
        return jsonify({"error": "Server error occurred"}), 500

@app.route('/save_main_resume', methods=['POST'])
@login_required
def save_main_resume():
    data = request.get_json()
    resume_content = data.get('resume_content', '').strip()
    if not resume_content:
        return jsonify({'success': False, 'error': 'No resume content provided.'}), 400
    session['main_resume_content'] = resume_content
    return jsonify({'success': True})

@app.route('/get_main_resume', methods=['GET'])
@login_required
def get_main_resume():
    resume_content = session.get('main_resume_content', '')
    return jsonify({'resume_content': resume_content})

if __name__ == "__main__":
    app.run(debug=True)
