import os
import logging
import uuid
import streamlit as st
from datetime import datetime
import json
import PyPDF2
import docx
from io import BytesIO

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

# Set the passcode
PASSCODE = "ibrahim@aplyease4139"

# Page configuration
st.set_page_config(
    page_title="AI Resume Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .score-badge {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 1.5rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
        font-size: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
        min-width: 140px;
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    .score-badge.warning {
        background: linear-gradient(135deg, #ffc107, #fd7e14);
        color: white;
        box-shadow: 0 4px 12px rgba(255, 193, 7, 0.3);
    }
    .score-badge.danger {
        background: linear-gradient(135deg, #dc3545, #e83e8c);
        box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
    }
    .optimized-badge {
        background: linear-gradient(135deg, #17a2b8, #6f42c1);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 1.2rem;
        font-weight: bold;
        display: inline-block;
        margin: 0.5rem 0;
        font-size: 1rem;
        text-align: center;
        box-shadow: 0 3px 10px rgba(23, 162, 184, 0.3);
        min-width: 120px;
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    .score-container {
        display: flex;
        gap: 1rem;
        align-items: center;
        justify-content: center;
        margin: 1rem 0;
        flex-wrap: wrap;
    }
    .feature-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
    .latex-code {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        white-space: pre-wrap;
        max-height: 400px;
        overflow-y: auto;
    }
    .section-header {
        background: linear-gradient(90deg, #1f77b4, #17a2b8);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        font-weight: bold;
    }
    .input-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
    .results-section {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .skills-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 1rem;
        margin: 1rem 0;
    }
    .skill-category {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .button-group {
        display: flex;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    .stButton > button {
        width: 100%;
        border-radius: 0.5rem;
        font-weight: bold;
    }
    .stDownloadButton > button {
        width: 100%;
        border-radius: 0.5rem;
        font-weight: bold;
    }
    .stTextArea > div > div > textarea {
        border-radius: 0.5rem;
    }
    .stTextInput > div > div > input {
        border-radius: 0.5rem;
    }
    .stSelectbox > div > div > select {
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'resume_store' not in st.session_state:
    st.session_state.resume_store = {}
if 'main_resume_content' not in st.session_state:
    st.session_state.main_resume_content = ""
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = None
if 'last_processed_file' not in st.session_state:
    st.session_state.last_processed_file = None
if 'base_resume_content' not in st.session_state:
    st.session_state.base_resume_content = ""
if 'uploaded_base_file_name' not in st.session_state:
    st.session_state.uploaded_base_file_name = None
if 'last_processed_base_file' not in st.session_state:
    st.session_state.last_processed_base_file = None

# Load template and prompt files
def load_template(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logging.error(f"Error loading template file {file_path}: {str(e)}")
        return ""

def load_prompt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logging.error(f"Error loading prompt file {file_path}: {str(e)}")
        return ""

# Load templates and prompts
DEFAULT_LATEX_TEMPLATE = load_template("templates/latex_template.tex")
RESUME_FORMATTER_PROMPT = load_prompt("prompts/resume_formatter.txt")
RESUME_EVALUATOR_PROMPT = load_prompt("prompts/resume_evaluator.txt")
RESUME_OPTIMIZER_PROMPT = load_prompt("prompts/resume_optimizer.txt")
COVER_LETTER_PROMPT = load_prompt("prompts/cover_letter_generator.txt")

# File processing functions
def extract_text_from_pdf(file_content):
    """Extract text from PDF file content."""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def extract_text_from_docx(file_content):
    """Extract text from DOCX file content."""
    try:
        doc = docx.Document(BytesIO(file_content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
        return ""

def process_uploaded_file(uploaded_file):
    """Process uploaded file and extract text."""
    if uploaded_file is None:
        return ""
    
    file_content = uploaded_file.read()
    
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(file_content)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file_content)
    elif uploaded_file.type == "application/msword":
        return extract_text_from_docx(file_content)
    else:
        st.error("Unsupported file type. Please upload a PDF or Word document.")
        return ""

# Authentication function
def authenticate():
    if not st.session_state.authenticated:
        st.markdown("## 🔐 Login Required")
        st.markdown("Please enter the passcode to access the AI Resume Generator.")
        
        passcode = st.text_input("Passcode", type="password", key="login_passcode")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Login", key="login_btn"):
                if passcode == PASSCODE:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid passcode. Please try again.")
        
        st.stop()

# Mock processing function
def mock_process_resume(resume_content, job_description=None):
    """Mock implementation for when Gemini API is not available."""
    return "AI processing not available. Please set your API key in Settings."

def generate_base_resume(client, resume_content):
    """Generate a high ATS-score base resume without job description."""
    # Check if we have a valid API key
    api_key = st.session_state.get('api_key', '')
    env_api_key = os.getenv('GENAI_API_KEY', '')
    
    if not client or not HAS_GENAI or (not api_key and not env_api_key):
        return "AI processing not available. Please set your API key in Settings.", 0
    
    try:
        logging.info("Generating base resume with Gemini AI...")
        
        # First, let's extract key information from the resume content
        lines = resume_content.strip().split('\n')
        
        # Extract name (usually first line)
        name = lines[0].strip() if lines else "Your Name"
        
        # Extract contact info
        contact_info = ""
        for line in lines[:5]:  # Check first 5 lines for contact info
            if any(char in line for char in ['@', '|', 'linkedin', 'github', 'phone', 'tel']):
                contact_info = line.strip()
                break
        
        base_resume_prompt = f"""
You are a professional resume writer specializing in ATS-optimized resumes. Create a complete LaTeX resume using ONLY the content provided below.

RESUME CONTENT TO CONVERT:
{resume_content}

TASK: Generate a complete LaTeX document that starts with \\documentclass and ends with \\end{{document}}.

CRITICAL RESUME OPTIMIZATION RULES:

1. QUANTIFY IMPACT WITH NUMBERS:
   - Add specific metrics, percentages, dollar amounts, timeframes, and quantities to EVERY bullet point
   - Examples: "Increased efficiency by 35%", "Reduced costs by $50K annually", "Managed team of 12 employees", "Improved processing time by 2 hours daily"
   - Even for entry-level positions, find ways to quantify impact (e.g., "Processed 200+ invoices monthly", "Reduced data entry errors by 15%")

2. AVOID REPETITIVE ACTION VERBS (CRITICAL):
   - NEVER use the same action verb more than 2 times in the entire resume
   - Use diverse action verbs: Achieved, Accelerated, Amplified, Boosted, Delivered, Enhanced, Exceeded, Generated, Improved, Increased, Led, Optimized, Reduced, Streamlined, Transformed, Developed, Implemented, Executed, Coordinated, Facilitated, Spearheaded, Orchestrated, Pioneered, Revitalized, Maximized, Minimized, Eliminated, Established, Created, Built, Designed, Launched, Initiated, Restructured, Reorganized, Modernized, Upgraded, Refined, Cultivated, Nurtured, Mentored, Trained, Educated, Guided, Directed, Supervised, Oversaw, Administered, Managed, Coordinated, Collaborated, Partnered, Negotiated, Resolved, Solved, Addressed, Tackled, Handled, Processed, Analyzed, Evaluated, Assessed, Reviewed, Audited, Monitored, Tracked, Measured, Calculated, Computed, Forecasted, Predicted, Planned, Strategized, Organized, Scheduled, Prioritized, Allocated, Distributed, Assigned, Delegated, Recruited, Hired, Onboarded, Retained, Motivated, Inspired, Influenced, Persuaded, Convinced, Negotiated, Mediated, Facilitated, Enabled, Empowered, Supported, Assisted, Helped, Contributed, Participated, Engaged, Interacted, Communicated, Presented, Demonstrated, Showcased, Exhibited, Displayed, Highlighted, Emphasized, Focused, Concentrated, Specialized, Expertised, Mastered, Excelled, Surpassed, Outperformed, Exceeded, Beat, Won, Succeeded, Accomplished, Completed, Finished, Delivered, Produced, Generated, Created, Built, Constructed, Assembled, Manufactured, Fabricated, Crafted, Designed, Developed, Invented, Innovated, Pioneered, Introduced, Launched, Initiated, Started, Began, Commenced, Opened, Established, Founded, Created, Built, Constructed, Assembled, Manufactured, Fabricated, Crafted, Designed, Developed, Invented, Innovated, Pioneered, Introduced, Launched, Initiated, Started, Began, Commenced, Opened, Established, Founded
   - AVOID weak verbs: Was responsible for, Helped with, Assisted in, Worked on, Participated in

3. ELIMINATE FILLER WORDS:
   - Remove superfluous words that add no value: "various", "several", "many", "some", "different", "multiple", "numerous", "extensive", "comprehensive", "significant", "substantial", "considerable", "effective", "successful", "excellent", "outstanding", "exceptional", "remarkable", "notable", "important", "valuable", "useful", "beneficial", "helpful", "supportive", "collaborative", "team-oriented", "detail-oriented", "results-driven", "goal-oriented", "customer-focused", "quality-focused", "performance-driven", "innovative", "creative", "strategic", "tactical", "operational", "administrative", "managerial", "leadership", "professional", "experienced", "skilled", "talented", "capable", "competent", "proficient", "expert", "advanced", "intermediate", "beginner", "entry-level", "senior", "junior", "associate", "principal", "lead", "head", "chief", "director", "manager", "supervisor", "coordinator", "specialist", "analyst", "consultant", "advisor", "expert", "professional", "representative", "agent", "executive", "officer", "president", "vice president", "CEO", "CTO", "CFO", "COO", "VP", "SVP", "EVP", "AVP", "Director", "Manager", "Supervisor", "Coordinator", "Specialist", "Analyst", "Consultant", "Advisor", "Expert", "Professional", "Representative", "Agent", "Executive", "Officer", "President", "Vice President", "CEO", "CTO", "CFO", "COO", "VP", "SVP", "EVP", "AVP"
   - Be concise and direct: "Led team of 8 developers" instead of "Successfully led a team of 8 skilled developers"

4. OPTIMAL RESUME LENGTH & DEPTH:
   - Target 400-675 words total (not 765+ words)
   - Use 12-20 bullet points maximum (not 24+)
   - Be concise for career level - new job seekers should be brief
   - Focus on quality over quantity

5. BULLET POINT STRUCTURE:
   - Use the CAR (Challenge-Action-Result) or STAR (Situation-Task-Action-Result) method
   - Each bullet should show: What you did + How you did it + What was the measurable result
   - Example: "Streamlined inventory management system, reducing processing time by 40% and saving $25K annually"

6. ACHIEVEMENT-FOCUSED LANGUAGE:
   - Focus on accomplishments, not just duties
   - Show impact and value delivered to the organization
   - Use past tense for completed work, present tense for current role

REQUIREMENTS:
1. Use the exact LaTeX template structure provided below
2. Replace ALL example content (Jake Ryan, jake@su.edu, etc.) with the actual content from the resume
3. Extract the person's name: {name}
4. Extract contact information and place it in the main body
5. Extract education, experience, projects, and skills from the provided content
6. Use proper LaTeX formatting and commands
7. Ensure the document compiles to a PDF
8. Apply ALL optimization rules above to enhance the resume content
9. Keep total word count between 400-675 words
10. Use maximum 20 bullet points across all experience sections
11. Ensure NO action verb is repeated more than 2 times

LaTeX Template to Use:
{DEFAULT_LATEX_TEMPLATE}

CRITICAL INSTRUCTIONS:
- Start your response with \\documentclass[letterpaper,10pt]{{article}}
- End your response with \\end{{document}}
- Replace "Jake Ryan" with "{name}"
- Replace "jake@su.edu" with the actual email from the resume content
- Replace all example content with real content from the resume
- Use the exact same LaTeX structure and commands
- Apply ALL optimization rules to enhance bullet points with numbers, diverse action verbs, and eliminate filler words
- Do not add explanations or markdown formatting
- Output ONLY the complete LaTeX code

OUTPUT FORMAT: Complete LaTeX document starting with \\documentclass and ending with \\end{{document}}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=base_resume_prompt
        )
        
        if response and response.text:
            latex_code = response.text.strip()
            
            # Clean up the response
            if latex_code.startswith("```latex"):
                latex_code = latex_code[8:]
            if latex_code.startswith("```"):
                latex_code = latex_code[3:]
            if latex_code.endswith("```"):
                latex_code = latex_code[:-3]
            
            latex_code = latex_code.strip()
            
            # Ensure it starts with documentclass
            if not latex_code.startswith("\\documentclass"):
                logging.warning("Generated content doesn't start with documentclass, using template")
                return DEFAULT_LATEX_TEMPLATE, 0
            
            # Now evaluate the ATS score
            ats_score = evaluate_ats_score(client, latex_code, resume_content)
            
            logging.info(f"Base resume generated successfully with ATS score: {ats_score}")
            return latex_code, ats_score
        else:
            logging.error("No response received from Gemini AI")
            return DEFAULT_LATEX_TEMPLATE, 0
            
    except Exception as e:
        logging.exception("Exception occurred while generating base resume with Gemini AI")
        return DEFAULT_LATEX_TEMPLATE, 0

def evaluate_ats_score(client, latex_code, original_content):
    """Evaluate the ATS score of the generated resume."""
    # Check if we have a valid API key
    api_key = st.session_state.get('api_key', '')
    env_api_key = os.getenv('GENAI_API_KEY', '')
    
    if not client or not HAS_GENAI or (not api_key and not env_api_key):
        return 0
    
    try:
        logging.info("Evaluating ATS score...")
        
        ats_evaluation_prompt = f"""
You are an ATS (Applicant Tracking System) specialist. Evaluate the LaTeX resume below and return a single integer ATS score from 1–100. Be strict and apply deductions for any ATS parsing risks. If a JOB DESCRIPTION is provided, weight keyword alignment heavily; if not, evaluate based on general ATS best practices and fidelity to the ORIGINAL CONTENT.

ORIGINAL CONTENT (ground truth of facts/keywords; do not reward invented data):
{original_content}

GENERATED LATEX RESUME (evaluate this):
{latex_code}

OPTIONAL JOB DESCRIPTION (use for keyword matching if present):
{job_description if 'job_description' in globals() else ''}

SCORING RUBRIC (Total = 100 points):

A) CONTACT INFO – 8 pts
- Name, professional email, phone, city/state present and clearly visible in body (not header/footer).
- Email looks valid; phone has 10+ digits; optional LinkedIn/portfolio is a plus.
- Deduct for missing items, nonstandard placement, or obfuscation.

B) SECTION PRESENCE & ORDER – 8 pts
- Standard, ATS-recognizable headings present: Summary/Professional Summary (optional), Work/Professional Experience, Education, Skills; Projects/Certifications if provided.
- Reverse-chronological order for dated sections.
- Deduct for quirky/ambiguous headings or missing core sections.

C) FORMATTING & LAYOUT – 10 pts
- Single-column layout, left-aligned body text, readable font (Arial/Calibri/Times-like), consistent bullets.
- No graphics, photos, icons, sidebars, text boxes, or multi-column tricks.
- Deduct for tables used for layout, content inside headers/footers, decorative bullets/symbols, or cramped spacing.

D) PARSING & TECHNICAL COMPATIBILITY – 8 pts
- Plain text content (not images); consistent Month YYYY–Month YYYY dates; no unusual characters or hidden text.
- No macros/embedded objects; links are plain text.
- Deduct for tabular layout that risks out-of-order parsing, inconsistent date formats, missing months, or header/footer text.

E) QUANTIFIED IMPACT (CRITICAL) – 20 pts
- MANDATORY: Every bullet point should contain specific numbers, percentages, dollar amounts, timeframes, or quantities.
- Examples: "Increased efficiency by 35%", "Reduced costs by $50K annually", "Managed team of 12 employees", "Processed 500+ documents weekly"
- Deduct heavily for vague statements without metrics (e.g., "Was responsible for maintaining efficiency" = 0 points)
- Reward specific, measurable achievements with clear impact

F) AVOID REPETITIVE ACTION VERBS (CRITICAL) – 15 pts
- NEVER use the same action verb more than 2 times in the entire resume
- Deduct heavily for repetition: "Managed (4 times)" = -10 points, "Optimized (3 times)" = -8 points
- Reward diverse action verbs: Achieved, Accelerated, Amplified, Boosted, Delivered, Enhanced, Exceeded, Generated, Improved, Increased, Led, Optimized, Reduced, Streamlined, Transformed, Developed, Implemented, Executed, Coordinated, Facilitated, Spearheaded, Orchestrated, Pioneered, etc.
- AVOID weak verbs: Was responsible for, Helped with, Assisted in, Worked on, Participated in

G) ELIMINATE FILLER WORDS – 10 pts
- Remove superfluous words that add no value: "various", "several", "many", "some", "different", "multiple", "numerous", "extensive", "comprehensive", "significant", "substantial", "considerable", "effective", "successful", "excellent", "outstanding", "exceptional", "remarkable", "notable", "important", "valuable", "useful", "beneficial", "helpful", "supportive", "collaborative", "team-oriented", "detail-oriented", "results-driven", "goal-oriented", "customer-focused", "quality-focused", "performance-driven", "innovative", "creative", "strategic", "tactical", "operational", "administrative", "managerial", "leadership", "professional", "experienced", "skilled", "talented", "capable", "competent", "proficient", "expert", "advanced", "intermediate", "beginner", "entry-level", "senior", "junior", "associate", "principal", "lead", "head", "chief", "director", "manager", "supervisor", "coordinator", "specialist", "analyst", "consultant", "advisor", "expert", "professional", "representative", "agent", "executive", "officer", "president", "vice president", "CEO", "CTO", "CFO", "COO", "VP", "SVP", "EVP", "AVP"
- Be concise and direct: "Led team of 8 developers" instead of "Successfully led a team of 8 skilled developers"
- Deduct for each filler word found

H) OPTIMAL RESUME LENGTH & DEPTH – 8 pts
- Target 400-675 words total (not 765+ words)
- Use 12-20 bullet points maximum (not 24+)
- Be concise for career level - new job seekers should be brief
- Focus on quality over quantity
- Deduct for excessive length or too many bullet points

I) BULLET POINT QUALITY – 8 pts
- Use CAR (Challenge-Action-Result) or STAR (Situation-Task-Action-Result) method
- Each bullet should show: What you did + How you did it + What was the measurable result
- Focus on accomplishments, not just duties
- Deduct for vague, duty-only descriptions without impact

J) SKILLS & KEYWORDS – 5 pts
- Skills section includes 6–12 relevant competencies; includes acronyms and their expansions when reasonable (e.g., "SQL (Structured Query Language)").
- If JOB DESCRIPTION provided: measure alignment (hard skills, tools, certs, domain terms). Reward natural integration across bullets, summary, and skills; penalize keyword stuffing or irrelevant terms.
- If JD not provided: reward preservation and accurate placement of role-relevant keywords present in ORIGINAL CONTENT.

K) EDUCATION – 2 pts
- Degree, institution, graduation (or expected) month/year clearly stated; honors/certs if provided.

BONUS/DEDUCTIONS (already bounded within categories above; do not exceed 100 total):
- Minor + for concise, high-signal Summary tailored to JD (if provided).
- Minor − for excessive length (e.g., >2 pages without strong justification), dense walls of text, or obvious keyword dumping.

OUTPUT REQUIREMENT:
Return ONLY a single integer from 1 to 100. No words, no explanations."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=ats_evaluation_prompt
        )
        
        if response and response.text:
            score_text = response.text.strip()
            # Extract number from response
            import re
            score_match = re.search(r'\b(\d+)\b', score_text)
            if score_match:
                score = int(score_match.group(1))
                return max(1, min(100, score))  # Ensure score is between 1-100
        
        return 70  # Default score if evaluation fails
        
    except Exception as e:
        logging.exception("Exception occurred during ATS evaluation")
        return 70  # Default score

def improve_base_resume_with_feedback(client, latex_code, original_content, user_feedback, current_score):
    """Improve the base resume based on specific user feedback."""
    # Check if we have a valid API key
    api_key = st.session_state.get('api_key', '')
    env_api_key = os.getenv('GENAI_API_KEY', '')
    
    if not client or not HAS_GENAI or (not api_key and not env_api_key):
        return latex_code, current_score
    
    try:
        logging.info(f"Improving base resume based on user feedback...")
        
        feedback_prompt = f"""
The following resume has an ATS score of {current_score}/100. Based on the specific user feedback provided below, rewrite and improve the resume to address the exact issues mentioned.

ORIGINAL CONTENT (ground truth – do not invent new employers, degrees, or dates):
{original_content}

CURRENT LATEX RESUME (Score: {current_score}/100):
{latex_code}

USER FEEDBACK TO ADDRESS:
{user_feedback}

IMPROVEMENT INSTRUCTIONS:
Based on the user feedback above, make the following improvements:

1. **ADDRESS SPECIFIC ISSUES MENTIONED**
   - Carefully read the user feedback and address each specific issue mentioned
   - If feedback mentions repetitive action verbs, replace them with diverse alternatives
   - If feedback mentions filler words, remove all specified filler words
   - If feedback mentions length issues, reduce word count and bullet points as specified
   - If feedback mentions weak action verbs, replace with strong action verbs
   - If feedback mentions quantification issues, add specific numbers and metrics

2. **QUANTIFY IMPACT WITH NUMBERS**
   - Add specific metrics, percentages, dollar amounts, timeframes, and quantities to EVERY bullet point
   - Examples: "Increased efficiency by 35%", "Reduced costs by $50K annually", "Managed team of 12 employees"

3. **USE DIVERSE ACTION VERBS**
   - NEVER use the same action verb more than 2 times in the entire resume
   - Use diverse action verbs: Achieved, Accelerated, Amplified, Boosted, Delivered, Enhanced, Exceeded, Generated, Improved, Increased, Led, Optimized, Reduced, Streamlined, Transformed, Developed, Implemented, Executed, Coordinated, Facilitated, Spearheaded, Orchestrated, Pioneered, etc.

4. **ELIMINATE FILLER WORDS**
   - Remove superfluous words that add no value: "various", "several", "many", "some", "different", "multiple", "numerous", "extensive", "comprehensive", "significant", "substantial", "considerable", "effective", "successful", "excellent", "outstanding", "exceptional", "remarkable", "notable", "important", "valuable", "useful", "beneficial", "helpful", "supportive", "collaborative", "team-oriented", "detail-oriented", "results-driven", "goal-oriented", "customer-focused", "quality-focused", "performance-driven", "innovative", "creative", "strategic", "tactical", "operational", "administrative", "managerial", "leadership", "professional", "experienced", "skilled", "talented", "capable", "competent", "proficient", "expert", "advanced", "intermediate", "beginner", "entry-level", "senior", "junior", "associate", "principal", "lead", "head", "chief", "director", "manager", "supervisor", "coordinator", "specialist", "analyst", "consultant", "advisor", "expert", "professional", "representative", "agent", "executive", "officer", "president", "vice president", "CEO", "CTO", "CFO", "COO", "VP", "SVP", "EVP", "AVP"

5. **OPTIMAL RESUME LENGTH & DEPTH**
   - Target 400-675 words total (not 765+ words)
   - Use 12-20 bullet points maximum (not 24+)
   - Be concise for career level - new job seekers should be brief

6. **BULLET POINT STRUCTURE**
   - Use the CAR (Challenge-Action-Result) or STAR (Situation-Task-Action-Result) method
   - Each bullet should show: What you did + How you did it + What was the measurable result

7. **ACHIEVEMENT-FOCUSED LANGUAGE**
   - Focus on accomplishments, not just duties
   - Show impact and value delivered to the organization
   - Use past tense for completed work, present tense for current role

8. **PRESERVE ACCURACY**
   - Do not fabricate new employers, degrees, or certifications
   - Use only information from the original content
   - Maintain factual accuracy while improving presentation

OUTPUT REQUIREMENT:
Generate an improved LaTeX resume that uses the same LaTeX structure but addresses all the specific issues mentioned in the user feedback.
Do not include explanations—output only the LaTeX code.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=feedback_prompt
        )
        
        if response and response.text:
            improved_latex = response.text.strip()
            
            # Clean up the response
            if improved_latex.startswith("```latex"):
                improved_latex = improved_latex[8:]
            if improved_latex.startswith("```"):
                improved_latex = improved_latex[3:]
            if improved_latex.endswith("```"):
                improved_latex = improved_latex[:-3]
            
            improved_latex = improved_latex.strip()
            
            if improved_latex.startswith("\\documentclass"):
                # Re-evaluate the improved resume
                new_score = evaluate_ats_score(client, improved_latex, original_content)
                logging.info(f"Base resume improved based on feedback. New ATS score: {new_score}")
                return improved_latex, new_score
        
        return latex_code, current_score
        
    except Exception as e:
        logging.exception("Exception occurred during base resume improvement with feedback")
        return latex_code, current_score

def improve_ats_resume(client, latex_code, original_content, current_score):
    """Improve the resume to achieve higher ATS score."""
    # Check if we have a valid API key
    api_key = st.session_state.get('api_key', '')
    env_api_key = os.getenv('GENAI_API_KEY', '')
    
    if not client or not HAS_GENAI or (not api_key and not env_api_key):
        return latex_code, current_score
    
    try:
        logging.info(f"Improving resume from ATS score {current_score}...")
        
        improvement_prompt = f"""
The following resume has an ATS score of {current_score}/100. Rewrite and improve it to achieve a target score of 90+ (minimum 80) by applying ATS best practices.

ORIGINAL CONTENT (ground truth – do not invent new employers, degrees, or dates):
{original_content}

CURRENT LATEX RESUME (Score: {current_score}/100):
{latex_code}

CRITICAL IMPROVEMENT RULES:

1. **QUANTIFY IMPACT WITH NUMBERS (CRITICAL - 20 points)**
   - MANDATORY: Add specific metrics, percentages, dollar amounts, timeframes, and quantities to EVERY bullet point
   - Examples: "Increased efficiency by 35%", "Reduced costs by $50K annually", "Managed team of 12 employees", "Improved processing time by 2 hours daily"
   - Even for entry-level positions, find ways to quantify impact (e.g., "Processed 200+ invoices monthly", "Reduced data entry errors by 15%")
   - Convert vague statements like "Was responsible for maintaining efficiency" to "Maintained 95% operational efficiency across 3 warehouse locations, reducing downtime by 25%"

2. **AVOID REPETITIVE ACTION VERBS (CRITICAL - 15 points)**
   - NEVER use the same action verb more than 2 times in the entire resume
   - Use diverse action verbs: Achieved, Accelerated, Amplified, Boosted, Delivered, Enhanced, Exceeded, Generated, Improved, Increased, Led, Optimized, Reduced, Streamlined, Transformed, Developed, Implemented, Executed, Coordinated, Facilitated, Spearheaded, Orchestrated, Pioneered, Revitalized, Maximized, Minimized, Eliminated, Established, Created, Built, Designed, Launched, Initiated, Restructured, Reorganized, Modernized, Upgraded, Refined, Cultivated, Nurtured, Mentored, Trained, Educated, Guided, Directed, Supervised, Oversaw, Administered, Managed, Coordinated, Collaborated, Partnered, Negotiated, Resolved, Solved, Addressed, Tackled, Handled, Processed, Analyzed, Evaluated, Assessed, Reviewed, Audited, Monitored, Tracked, Measured, Calculated, Computed, Forecasted, Predicted, Planned, Strategized, Organized, Scheduled, Prioritized, Allocated, Distributed, Assigned, Delegated, Recruited, Hired, Onboarded, Retained, Motivated, Inspired, Influenced, Persuaded, Convinced, Negotiated, Mediated, Facilitated, Enabled, Empowered, Supported, Assisted, Helped, Contributed, Participated, Engaged, Interacted, Communicated, Presented, Demonstrated, Showcased, Exhibited, Displayed, Highlighted, Emphasized, Focused, Concentrated, Specialized, Expertised, Mastered, Excelled, Surpassed, Outperformed, Exceeded, Beat, Won, Succeeded, Accomplished, Completed, Finished, Delivered, Produced, Generated, Created, Built, Constructed, Assembled, Manufactured, Fabricated, Crafted, Designed, Developed, Invented, Innovated, Pioneered, Introduced, Launched, Initiated, Started, Began, Commenced, Opened, Established, Founded
   - AVOID weak verbs: Was responsible for, Helped with, Assisted in, Worked on, Participated in
   - Examples of transformations:
     * "Was responsible for" → "Led", "Managed", "Oversaw"
     * "Helped with" → "Contributed to", "Supported", "Facilitated"
     * "Worked on" → "Developed", "Implemented", "Executed"

3. **ELIMINATE FILLER WORDS (10 points)**
   - Remove superfluous words that add no value: "various", "several", "many", "some", "different", "multiple", "numerous", "extensive", "comprehensive", "significant", "substantial", "considerable", "effective", "successful", "excellent", "outstanding", "exceptional", "remarkable", "notable", "important", "valuable", "useful", "beneficial", "helpful", "supportive", "collaborative", "team-oriented", "detail-oriented", "results-driven", "goal-oriented", "customer-focused", "quality-focused", "performance-driven", "innovative", "creative", "strategic", "tactical", "operational", "administrative", "managerial", "leadership", "professional", "experienced", "skilled", "talented", "capable", "competent", "proficient", "expert", "advanced", "intermediate", "beginner", "entry-level", "senior", "junior", "associate", "principal", "lead", "head", "chief", "director", "manager", "supervisor", "coordinator", "specialist", "analyst", "consultant", "advisor", "expert", "professional", "representative", "agent", "executive", "officer", "president", "vice president", "CEO", "CTO", "CFO", "COO", "VP", "SVP", "EVP", "AVP"
   - Be concise and direct: "Led team of 8 developers" instead of "Successfully led a team of 8 skilled developers"

4. **OPTIMAL RESUME LENGTH & DEPTH (8 points)**
   - Target 400-675 words total (not 765+ words)
   - Use 12-20 bullet points maximum (not 24+)
   - Be concise for career level - new job seekers should be brief
   - Focus on quality over quantity

5. **BULLET POINT STRUCTURE (8 points)**
   - Use the CAR (Challenge-Action-Result) or STAR (Situation-Task-Action-Result) method
   - Each bullet should show: What you did + How you did it + What was the measurable result
   - Example transformation:
     * Weak: "Reviewed and approved construction plans"
     * Strong: "Analyzed and approved 50+ construction plans monthly, ensuring 100% compliance with safety standards and reducing approval time by 30%"

6. **ACHIEVEMENT-FOCUSED LANGUAGE**
   - Focus on accomplishments, not just duties
   - Show impact and value delivered to the organization
   - Use past tense for completed work, present tense for current role

7. **Keywords & Skills**
   - Add relevant technical and industry keywords drawn naturally from the ORIGINAL CONTENT.
   - Expand acronyms with full terms at least once (e.g., SQL (Structured Query Language)).
   - Ensure a dedicated "Skills" section contains 6–12 competencies tailored to industry roles.
   - Integrate keywords into work bullets, summary, and projects without keyword stuffing.

8. **Formatting & ATS Compatibility**
   - Keep a single-column layout, standard section headings (Experience, Education, Skills, Projects).
   - Remove any risky elements: tables, graphics, text boxes, multiple columns, icons.
   - Ensure consistent date formatting: Month YYYY – Month YYYY (or Present).

9. **Experience Section**
   - Each role must include: Job Title, Company, Location, Dates.
   - Rewrite bullets to start with strong action verbs.
   - Add measurable outcomes/achievements (e.g., "Improved processing speed by 25%," "Reduced costs by $50K annually").
   - Maintain reverse-chronological order.

10. **Education Section**
    - Include degree, institution, location, and graduation (or expected) month/year.
    - Keep formatting consistent and ATS-readable.

11. **Projects (if any provided)**
    - Show outcomes, tools used, and skills demonstrated.
    - Keep concise but keyword-rich.

12. **Clarity & Consistency**
    - Use clean bullets (● or -).
    - No text in headers/footers.
    - Ensure spacing and indentation is consistent.
    - Preserve accuracy: do not fabricate new employers, degrees, or certifications.

13. **Industry Terminology**
    - Add common role-specific terms for U.S. job market (e.g., Agile, Scrum, CI/CD, Cloud platforms, Cybersecurity frameworks, Data Science tools) if supported by the ORIGINAL CONTENT.
    - Use terminology naturally in bullets or skills.

OUTPUT REQUIREMENT:
Generate an improved LaTeX resume that uses the same LaTeX structure but integrates all enhancements above. 
Do not include explanations—output only the LaTeX code.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=improvement_prompt
        )
        
        if response and response.text:
            improved_latex = response.text.strip()
            
            # Clean up the response
            if improved_latex.startswith("```latex"):
                improved_latex = improved_latex[8:]
            if improved_latex.startswith("```"):
                improved_latex = improved_latex[3:]
            if improved_latex.endswith("```"):
                improved_latex = improved_latex[:-3]
            
            improved_latex = improved_latex.strip()
            
            if improved_latex.startswith("\\documentclass"):
                # Re-evaluate the improved resume
                new_score = evaluate_ats_score(client, improved_latex, original_content)
                logging.info(f"Improved resume ATS score: {new_score}")
                return improved_latex, new_score
        
        return latex_code, current_score
        
    except Exception as e:
        logging.exception("Exception occurred during resume improvement")
        return latex_code, current_score

# AI processing functions
def process_with_gemini(client, resume_content, job_description=None):
    """Process resume with Gemini AI."""
    # Check if we have a valid API key
    api_key = st.session_state.get('api_key', '')
    env_api_key = os.getenv('GENAI_API_KEY', '')
    
    if not client or not HAS_GENAI or (not api_key and not env_api_key):
        logging.warning("Using mock implementation for resume processing")
        return mock_process_resume(resume_content, job_description)
    
    try:
        logging.info("Sending resume content to Gemini AI for processing...")
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
    """Evaluate resume-job match."""
    # Check if we have a valid API key
    api_key = st.session_state.get('api_key', '')
    env_api_key = os.getenv('GENAI_API_KEY', '')
    
    if not client or not HAS_GENAI or (not api_key and not env_api_key):
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
            model="gemini-2.5-flash", 
            contents=prompt
        )
        
        if not response.text:
            logging.error("Error: No response from Gemini AI for evaluation.")
            return 7, "Unable to evaluate resume-job match."
        
        response_text = response.text.strip()
        
        # Extract score
        score_line = next((line for line in response_text.split('\n') if line.startswith('SCORE:')), None)
        if score_line:
            try:
                score = int(score_line.split('SCORE:')[1].strip())
                score = max(1, min(10, score))
            except (ValueError, IndexError):
                score = 7
        else:
            score = 7
        
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
    """Optimize resume for better job alignment."""
    # Check if we have a valid API key
    api_key = st.session_state.get('api_key', '')
    env_api_key = os.getenv('GENAI_API_KEY', '')
    
    if not client or not HAS_GENAI or (not api_key and not env_api_key):
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
            model="gemini-2.5-flash",
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

def generate_cover_letter(client, latex_code, company_name, job_description):
    """Generate a cover letter based on the resume, company name, and job description."""
    # Check if we have a valid API key
    api_key = st.session_state.get('api_key', '')
    env_api_key = os.getenv('GENAI_API_KEY', '')
    
    if not client or not HAS_GENAI or (not api_key and not env_api_key):
        return "AI processing not available. Please set your API key in Settings."
    
    try:
        logging.info("Generating cover letter with Gemini AI...")
        
        # Extract key information from the LaTeX resume
        lines = latex_code.split('\n')
        name = "Your Name"
        email = "your.email@example.com"
        
        # Extract name and email from LaTeX code
        for line in lines:
            if '\\textbf{\\Huge' in line and 'scshape' in line:
                # Extract name from LaTeX formatting
                name_match = line.split('\\textbf{\\Huge \\scshape ')[1].split('}')[0] if '\\textbf{\\Huge \\scshape ' in line else None
                if name_match:
                    name = name_match
            elif 'href{mailto:' in line:
                # Extract email from LaTeX formatting
                email_match = line.split('href{mailto:')[1].split('}')[0] if 'href{mailto:' in line else None
                if email_match:
                    email = email_match
        
        cover_letter_prompt = f"""
{COVER_LETTER_PROMPT}

CANDIDATE INFORMATION:
- Name: {name}
- Email: {email}
- Company: {company_name}

RESUME CONTENT (LaTeX format):
{latex_code}

JOB DESCRIPTION:
{job_description}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=cover_letter_prompt
        )
        
        if response and response.text:
            cover_letter = response.text.strip()
            
            # Clean up the response
            if cover_letter.startswith("```"):
                cover_letter = cover_letter[3:]
            if cover_letter.endswith("```"):
                cover_letter = cover_letter[:-3]
            
            cover_letter = cover_letter.strip()
            
            logging.info("Cover letter generated successfully")
            return cover_letter
        else:
            logging.error("No response received from Gemini AI for cover letter generation")
            return "Error: Unable to generate cover letter. Please try again."
            
    except Exception as e:
        logging.exception("Exception occurred while generating cover letter with Gemini AI")
        return f"Error generating cover letter: {str(e)}"

def analyze_skills(client, latex_code, job_description):
    """Analyze skills and compare with job requirements."""
    # Check if we have a valid API key
    api_key = st.session_state.get('api_key', '')
    env_api_key = os.getenv('GENAI_API_KEY', '')
    
    if not client or not HAS_GENAI or (not api_key and not env_api_key):
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
            model="gemini-2.5-flash",
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

        # Generate LaTeX skills section
        latex_template = """%-----------SKILLS and CERTIFICATIONS-----------
\\section{Professional Skills \\& Certifications}
 \\begin{itemize}[leftmargin=0.15in, label={}]
    \\small{\\item{
<SKILLS_BY_CATEGORY>
     \\textbf{Certifications}{: <CERTS>}
    }}
 \\end{itemize}"""

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
generate a CONCISE LaTeX skills section using the exact template below.

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
11. KEEP IT SHORT AND CONCISE - Maximum 4-5  skill categories, 7-10 skills per category
12. Prioritize the most important/relevant skills for the job
13. Use abbreviations where appropriate (e.g., "AI/ML" instead of "Artificial Intelligence and Machine Learning")
14. Focus on key technical skills and certifications only
15. Avoid redundant or overly detailed skill descriptions
"""

        latex_response = client.models.generate_content(
            model="gemini-2.5-flash",
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

# Main application
def main():
    authenticate()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Resume Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; margin-bottom: 2rem;">Transform your resume into a professional LaTeX document tailored to your target job description</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🔧 Settings")
        
        # API Key input
        api_key = st.text_input(
            "Google Gemini API Key (optional)",
            type="password",
            help="Enter your Gemini API key for best results. Leave empty to use default (limited) mode.",
            key="api_key"
        )
        
        # Logout button
        if st.button("🚪 Logout", key="logout_btn"):
            st.session_state.authenticated = False
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 App Info")
        st.info("**Developer:** Mohammad Ibrahim Saleem\n\n**Features:**\n- AI-powered resume formatting\n- Job description tailoring\n- Skills analysis\n- LaTeX generation\n- Download functionality")
    
    # Check if API key is properly set
    api_key = st.session_state.get('api_key', '')
    if not api_key and not os.getenv('GENAI_API_KEY'):
        st.warning("🔑 Please set your Google Gemini API key in Settings to use AI features.")
        st.info("Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)")
        st.stop()
    
    # Main content - Tabbed layout
    tab1, tab2, tab3 = st.tabs(["📝 Generate Resume", "📊 Skills Analysis", "🎯 Base Resume Generator"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("## 📝 Input & Processing")
        
            # File upload section
            st.markdown("### 📄 Upload Resume File (Optional)")
            uploaded_file = st.file_uploader(
                "Choose a PDF or Word document",
                type=['pdf', 'docx', 'doc'],
                help="Upload your resume as a PDF or Word document. The text will be automatically extracted.",
                key="resume_file"
            )
            
            # Process uploaded file
            if uploaded_file is not None:
                # Check if this is a new file (not already processed)
                if not hasattr(st.session_state, 'last_processed_file') or st.session_state.last_processed_file != uploaded_file.name:
                    with st.spinner("Extracting text from uploaded file..."):
                        extracted_text = process_uploaded_file(uploaded_file)
                        if extracted_text:
                            st.success(f"✅ Successfully extracted text from {uploaded_file.name}")
                            # Auto-fill the text area with extracted text
                            st.session_state.main_resume_content = extracted_text
                            st.session_state.uploaded_file_name = uploaded_file.name
                            st.session_state.last_processed_file = uploaded_file.name
                        else:
                            st.error("❌ Failed to extract text from the uploaded file.")
            
            # Show uploaded file info and clear option
            if hasattr(st.session_state, 'uploaded_file_name') and st.session_state.uploaded_file_name:
                col_file_info, col_clear_file = st.columns([3, 1])
                with col_file_info:
                    st.info(f"📎 File loaded: {st.session_state.uploaded_file_name}")
                with col_clear_file:
                    if st.button("🗑️ Clear", key="clear_file"):
                        st.session_state.uploaded_file_name = None
                        st.session_state.main_resume_content = ""
                        st.session_state.last_processed_file = None
                        st.rerun()
            
            # Form
            with st.form("resume_form"):
                resume_content = st.text_area(
                    "Paste your current resume text:",
                    height=200,
                    placeholder="Paste your current resume content here or upload a file above...",
                    value=st.session_state.main_resume_content,
                    key="resume_content"
                )
                
                col_save, col_clear = st.columns(2)
                with col_save:
                    if st.form_submit_button("💾 Save Resume", key="save_resume"):
                        if resume_content:
                            st.session_state.main_resume_content = resume_content
                            st.success("Resume saved successfully!")
                        else:
                            st.error("Please enter resume content first.")
                
                with col_clear:
                    if st.form_submit_button("🗑️ Clear", key="clear_resume"):
                        st.session_state.main_resume_content = ""
                        st.rerun()
                
                company_name = st.text_input(
                    "Company Name:",
                    placeholder="Enter the company name (e.g., Google)",
                    key="company_name"
                )
                
                # Job description with edit capability
                st.markdown("### 🎯 Job Description")
                job_description = st.text_area(
                    "Paste the job description here:",
                    height=150,
                    placeholder="Paste the job description here to tailor your resume...",
                    key="job_description"
                )
                
                # Quick edit buttons for job description
                if job_description:
                    col_edit1, col_edit2, col_edit3 = st.columns(3)
                    with col_edit1:
                        if st.form_submit_button("📝 Edit Job", key="edit_job"):
                            st.session_state.editing_job = True
                    
                    with col_edit2:
                        if st.form_submit_button("🔄 Reset Job", key="reset_job"):
                            st.session_state.job_description = ""
                            st.rerun()
                    
                    with col_edit3:
                        if st.form_submit_button("💾 Save Job", key="save_job"):
                            st.session_state.saved_job_description = job_description
                            st.success("Job description saved!")
                
                submitted = st.form_submit_button("🚀 Generate Tailored Resume", type="primary", use_container_width=True)
            
                if submitted:
                    if not resume_content:
                        st.error("Please provide your resume content.")
                    elif not job_description:
                        st.error("Please provide a job description for tailoring.")
                    else:
                        # Process the resume
                        with st.spinner("🤖 Processing your resume with AI..."):
                            # Set up client
                            if HAS_GENAI:
                                local_client = genai.Client(api_key=api_key) if api_key else default_client
                                if not local_client:
                                    st.error("No valid API client available")
                                    st.stop()
                            else:
                                local_client = None
                            
                            try:
                                # Process with Gemini
                                latex_code = process_with_gemini(local_client, resume_content, job_description)
                                if not latex_code:
                                    st.error("Failed to generate LaTeX code")
                                    st.stop()
                                
                                # Evaluate resume
                                score, feedback = evaluate_resume_job_match(local_client, latex_code, job_description)
                                
                                # Analyze skills
                                skills_analysis = analyze_skills(local_client, latex_code, job_description)
                                
                                optimized = False
                                optimization_message = ''
                                
                                # Auto-optimize if score is low
                                if score < 8:
                                    st.warning(f"Initial score {score}/10 is below threshold. Optimizing resume...")
                                    latex_code = optimize_resume_for_job(local_client, latex_code, job_description, feedback)
                                    optimized = True
                                    optimization_message = 'Optimization was performed automatically because the initial score was low.'
                                    score, feedback = evaluate_resume_job_match(local_client, latex_code, job_description)
                                
                                # Store results
                                resume_id = str(uuid.uuid4())
                                st.session_state.resume_store[resume_id] = {
                                    "latex_code": latex_code,
                                    "score": score,
                                    "feedback": feedback,
                                    "skills_analysis": skills_analysis,
                                    "optimized": optimized,
                                    "optimization_message": optimization_message,
                                    "company_name": company_name,
                                    "job_description": job_description,
                                    "timestamp": datetime.now().isoformat()
                                }
                                
                                st.session_state.current_resume_id = resume_id
                                st.success("✅ Resume processed successfully!")
                                
                                if optimized:
                                    st.info("🔄 Resume was automatically optimized to better match the job description.")
                                
                            except Exception as e:
                                st.error(f"Error processing resume: {str(e)}")
        
        with col2:
            st.markdown("## 📄 Results & LaTeX Code")
        
            # Display results if available
            if 'current_resume_id' in st.session_state and st.session_state.current_resume_id in st.session_state.resume_store:
                resume_data = st.session_state.resume_store[st.session_state.current_resume_id]
            
                # Score and status
                score = resume_data.get("score", 0)
                if score >= 8:
                    score_class = "score-badge"
                elif score >= 6:
                    score_class = "score-badge warning"
                else:
                    score_class = "score-badge danger"
                
                # Score, status, and re-optimize container
                col_score, col_status, col_reopt = st.columns([1, 1, 1])
                
                with col_score:
                    st.markdown(f'<div class="{score_class}">Resume Score: {score}/10</div>', unsafe_allow_html=True)
                
                with col_status:
                    if resume_data.get("optimized"):
                        st.markdown('<div class="optimized-badge">✨ Optimized</div>', unsafe_allow_html=True)
                
                with col_reopt:
                    if st.button("🔄 Re-optimize", key="reoptimize", use_container_width=True):
                        with st.spinner("Re-optimizing resume..."):
                            if HAS_GENAI:
                                local_client = genai.Client(api_key=api_key) if api_key else default_client
                            else:
                                local_client = None
                            
                            optimized_latex = optimize_resume_for_job(
                                local_client, 
                                resume_data["latex_code"], 
                                resume_data.get("job_description", ""),
                                resume_data.get("feedback", "")
                            )
                            
                            if optimized_latex:
                                resume_data["latex_code"] = optimized_latex
                                resume_data["optimized"] = True
                                resume_data["optimization_message"] = "Resume has been re-optimized for better job alignment."
                                st.session_state.resume_store[st.session_state.current_resume_id] = resume_data
                                st.success("Resume re-optimized successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to re-optimize resume.")
                
                if resume_data.get("optimization_message"):
                    st.info(resume_data["optimization_message"])
                
                # LaTeX code with real-time preview
                st.markdown("### 📄 Generated LaTeX Code")
                latex_code = resume_data.get("latex_code", "")
                if latex_code:
                    # LaTeX code display with proper syntax highlighting
                    st.code(latex_code, language="latex", line_numbers=True)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download LaTeX File",
                        data=latex_code,
                        file_name=f"resume_{resume_data.get('company_name', 'generated')}.tex",
                        mime="application/x-tex",
                        key="download_latex",
                        use_container_width=True
                    )
                else:
                    st.info("Generate a resume to see LaTeX code here")
                
                # Cover Letter Section
                if latex_code and resume_data.get('company_name') and resume_data.get('job_description'):
                    st.markdown("### 📝 Cover Letter")
                    
                    # Check if cover letter is already generated
                    if 'cover_letter' not in resume_data:
                        resume_data['cover_letter'] = None
                    
                    if resume_data['cover_letter']:
                        # Display existing cover letter
                        st.text_area(
                            "Generated Cover Letter:",
                            value=resume_data['cover_letter'],
                            height=300,
                            key="cover_letter_display",
                            disabled=True
                        )
                        
                        col_cover_copy, col_cover_regen = st.columns(2)
                        with col_cover_copy:
                            if st.button("📋 Copy Cover Letter", key="copy_cover_letter", use_container_width=True):
                                st.success("Cover letter copied to clipboard!")
                        
                        with col_cover_regen:
                            if st.button("🔄 Regenerate Cover Letter", key="regenerate_cover_letter", use_container_width=True):
                                with st.spinner("🤖 Generating new cover letter..."):
                                    if HAS_GENAI:
                                        local_client = genai.Client(api_key=api_key) if api_key else default_client
                                    else:
                                        local_client = None
                                    
                                    new_cover_letter = generate_cover_letter(
                                        local_client,
                                        latex_code,
                                        resume_data.get('company_name', ''),
                                        resume_data.get('job_description', '')
                                    )
                                    
                                    if new_cover_letter and not new_cover_letter.startswith("Error"):
                                        resume_data['cover_letter'] = new_cover_letter
                                        st.session_state.resume_store[st.session_state.current_resume_id] = resume_data
                                        st.success("Cover letter regenerated successfully!")
                                        st.rerun()
                                    else:
                                        st.error(f"Failed to regenerate cover letter: {new_cover_letter}")
                    else:
                        # Generate cover letter button
                        if st.button("📝 Generate Cover Letter", key="generate_cover_letter", use_container_width=True):
                            with st.spinner("🤖 Generating cover letter..."):
                                if HAS_GENAI:
                                    local_client = genai.Client(api_key=api_key) if api_key else default_client
                                else:
                                    local_client = None
                                
                                cover_letter = generate_cover_letter(
                                    local_client,
                                    latex_code,
                                    resume_data.get('company_name', ''),
                                    resume_data.get('job_description', '')
                                )
                                
                                if cover_letter and not cover_letter.startswith("Error"):
                                    resume_data['cover_letter'] = cover_letter
                                    st.session_state.resume_store[st.session_state.current_resume_id] = resume_data
                                    st.success("Cover letter generated successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to generate cover letter: {cover_letter}")
                elif latex_code:
                    st.info("💡 Company name and job description are required to generate a cover letter")
                
                # AI Feedback
                st.markdown("### 💬 AI Feedback")
                feedback = resume_data.get("feedback", "No feedback available")
                st.markdown(feedback)
                
            else:
                st.info("👈 Fill out the form and click 'Generate Tailored Resume' to see results here")
    
    with tab2:
        st.markdown("## 📊 Skills Analysis")
        
        # Display skills analysis if available
        if 'current_resume_id' in st.session_state and st.session_state.current_resume_id in st.session_state.resume_store:
            resume_data = st.session_state.resume_store[st.session_state.current_resume_id]
            
            if resume_data.get("skills_analysis"):
                skills_data = resume_data["skills_analysis"]
                
                # LaTeX Skills Section - Moved to top
                st.markdown("### 📝 LaTeX Skills Section")
                if skills_data.get("latex_skills_section"):
                    # Skills LaTeX code display with proper syntax highlighting
                    st.code(skills_data["latex_skills_section"], language="latex", line_numbers=True)
                    
                    col_skills_copy, col_skills_regen = st.columns(2)
                    with col_skills_copy:
                        if st.button("📋 Copy Skills LaTeX", key="copy_skills", use_container_width=True):
                            st.success("Skills LaTeX code copied to clipboard!")
                    
                    with col_skills_regen:
                        if st.button("🔄 Regenerate Skills", key="regen_skills", use_container_width=True):
                            with st.spinner("Regenerating skills section..."):
                                if HAS_GENAI:
                                    local_client = genai.Client(api_key=api_key) if api_key else default_client
                                else:
                                    local_client = None
                                
                                # Re-analyze skills
                                new_skills_analysis = analyze_skills(
                                    local_client, 
                                    resume_data.get("latex_code", ""), 
                                    resume_data.get("job_description", "")
                                )
                                
                                # Update stored data
                                st.session_state.resume_store[st.session_state.current_resume_id]["skills_analysis"] = new_skills_analysis
                                
                                st.success("Skills section regenerated successfully!")
                                st.rerun()
                else:
                    st.info("No LaTeX skills section generated")
                
                st.markdown("---")
                
                # Skills Lists - Moved below LaTeX section
                col_skills1, col_skills2, col_skills3 = st.columns(3)
                
                with col_skills1:
                    st.markdown("### ✅ Current Skills")
                    if skills_data.get("current_skills_by_category"):
                        for category, skills in skills_data["current_skills_by_category"].items():
                            if skills:
                                st.markdown(f"**{category}:**")
                                for skill in skills:
                                    st.markdown(f"• {skill}")
                    elif skills_data.get("current_skills"):
                        for skill in skills_data["current_skills"]:
                            st.markdown(f"• {skill}")
                    else:
                        st.info("No skills found")
                
                with col_skills2:
                    st.markdown("### ❌ Missing Skills")
                    if skills_data.get("missing_skills"):
                        for skill in skills_data["missing_skills"]:
                            st.markdown(f"• {skill}")
                    else:
                        st.info("No missing skills identified")
                
                with col_skills3:
                    st.markdown("### 💡 Recommended Skills")
                    if skills_data.get("recommended_skills_by_category"):
                        for category, skills in skills_data["recommended_skills_by_category"].items():
                            if skills:
                                st.markdown(f"**{category}:**")
                                for skill in skills:
                                    st.markdown(f"• {skill}")
                    elif skills_data.get("recommended_skills"):
                        for skill in skills_data["recommended_skills"]:
                            st.markdown(f"• {skill}")
                    else:
                        st.info("No additional skills recommended")
            else:
                st.info("No skills analysis available. Generate a resume first.")
        else:
            st.info("👈 Generate a resume first to see skills analysis here")
    
    with tab3:
        st.markdown("## 🎯 Base Resume Generator")
        st.markdown("Create a high ATS-score, one-page resume from your existing content without needing a specific job description.")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📄 Input Your Resume Content")
            
            # File upload section for base resume
            st.markdown("#### 📁 Upload Resume File (Optional)")
            uploaded_base_file = st.file_uploader(
                "Choose a PDF or Word document",
                type=['pdf', 'docx', 'doc'],
                help="Upload your existing resume as a PDF or Word document.",
                key="base_resume_file"
            )
            
            # Process uploaded file for base resume
            if uploaded_base_file is not None:
                # Check if this is a new file (not already processed)
                if not hasattr(st.session_state, 'last_processed_base_file') or st.session_state.last_processed_base_file != uploaded_base_file.name:
                    with st.spinner("Extracting text from uploaded file..."):
                        extracted_text = process_uploaded_file(uploaded_base_file)
                        if extracted_text:
                            st.success(f"✅ Successfully extracted text from {uploaded_base_file.name}")
                            # Auto-fill the text area with extracted text
                            st.session_state.base_resume_content = extracted_text
                            st.session_state.uploaded_base_file_name = uploaded_base_file.name
                            st.session_state.last_processed_base_file = uploaded_base_file.name
                        else:
                            st.error("❌ Failed to extract text from the uploaded file.")
            
            # Show uploaded file info and clear option for base resume
            if hasattr(st.session_state, 'uploaded_base_file_name') and st.session_state.uploaded_base_file_name:
                col_file_info, col_clear_file = st.columns([3, 1])
                with col_file_info:
                    st.info(f"📎 File loaded: {st.session_state.uploaded_base_file_name}")
                with col_clear_file:
                    if st.button("🗑️ Clear", key="clear_base_file"):
                        st.session_state.uploaded_base_file_name = None
                        st.session_state.base_resume_content = ""
                        st.session_state.last_processed_base_file = None
                        st.rerun()
            
            # Resume content input
            base_resume_content = st.text_area(
                "Paste your current resume text:",
                height=200,
                placeholder="Paste your current resume content here or upload a file above...",
                value=st.session_state.get('base_resume_content', ''),
                key="base_resume_content"
            )
            
            # Show preview if content exists
            if base_resume_content.strip():
                st.markdown("### 👀 Content Preview")
                with st.expander("View your resume content", expanded=False):
                    st.text(base_resume_content)
                
                # Generate button
                if st.button("🚀 Generate Base Resume", use_container_width=True):
                    with st.spinner("🤖 Creating your optimized base resume..."):
                        # Set up client
                        if HAS_GENAI:
                            local_client = genai.Client(api_key=api_key) if api_key else default_client
                            if not local_client:
                                st.error("No valid API client available")
                                st.stop()
                        else:
                            local_client = None
                        
                        # Generate base resume
                        base_latex_code, ats_score = generate_base_resume(local_client, base_resume_content)
                        
                        if base_latex_code and base_latex_code != "AI processing not available. Please set your API key in Settings.":
                            # Check if ATS score is too low and improve if needed
                            if ats_score < 80:
                                st.warning(f"⚠️ Initial ATS score: {ats_score}/100. Improving resume...")
                                base_latex_code, ats_score = improve_ats_resume(local_client, base_latex_code, base_resume_content, ats_score)
                            
                            # Store the generated base resume
                            base_resume_id = str(uuid.uuid4())
                            st.session_state.resume_store[base_resume_id] = {
                                "latex_code": base_latex_code,
                                "company_name": "base_resume",
                                "job_description": "Base resume optimized for ATS systems",
                                "score": ats_score,  # Actual ATS score
                                "feedback": f"Base resume generated with ATS score: {ats_score}/100",
                                "optimized": ats_score >= 80,
                                "optimization_message": f"Base resume optimized for ATS systems. Final ATS score: {ats_score}/100",
                                "skills_analysis": None,
                                "created_at": datetime.now().isoformat()
                            }
                            st.session_state.current_base_resume_id = base_resume_id
                            
                            if ats_score >= 80:
                                st.success(f"✅ Base resume generated successfully! ATS Score: {ats_score}/100")
                            else:
                                st.warning(f"⚠️ Base resume generated with ATS Score: {ats_score}/100. Consider manual improvements.")
                            st.rerun()
                        else:
                            st.error("❌ Failed to generate base resume. Please check your API key.")
            else:
                st.info("👆 Upload a file or paste your resume content above to get started")
        
        with col2:
            st.markdown("### 📄 Generated Base Resume")
            
            # Display base resume results if available
            if 'current_base_resume_id' in st.session_state and st.session_state.current_base_resume_id in st.session_state.resume_store:
                base_resume_data = st.session_state.resume_store[st.session_state.current_base_resume_id]
                
                # ATS Score badge for base resume
                ats_score = base_resume_data.get("score", 0)
                if ats_score >= 80:
                    score_class = "score-badge"
                    status_badge = '<div class="optimized-badge">✨ ATS Optimized</div>'
                elif ats_score >= 60:
                    score_class = "score-badge warning"
                    status_badge = '<div class="optimized-badge" style="background: linear-gradient(135deg, #ffc107, #fd7e14);">⚠️ Needs Improvement</div>'
                else:
                    score_class = "score-badge danger"
                    status_badge = '<div class="optimized-badge" style="background: linear-gradient(135deg, #dc3545, #e83e8c);">❌ Low ATS Score</div>'
                
                st.markdown(f'<div class="{score_class}">ATS Score: {ats_score}/100</div>', unsafe_allow_html=True)
                st.markdown(status_badge, unsafe_allow_html=True)
                
                # User Feedback Section
                st.markdown("### 📝 Provide Feedback to Improve Resume")
                st.markdown("Share specific feedback about the resume (like Resume Worded feedback) and we'll regenerate it to address those issues.")
                
                user_feedback = st.text_area(
                    "Enter your feedback:",
                    height=100,
                    placeholder="Example: 'The resume scored 65/100. Issues found: 1) Repetitive action verbs - Managed used 4 times, Optimized used 3 times. 2) Filler words found - remove words like various, several, many. 3) Resume too long - 765 words, should be 400-675 words. 4) Too many bullet points - 24 bullets, should be 12-20. 5) Weak action verbs - replace Was responsible for with stronger verbs.'",
                    key="base_resume_feedback"
                )
                
                col_feedback1, col_feedback2 = st.columns(2)
                with col_feedback1:
                    if st.button("🔄 Regenerate Based on Feedback", key="regenerate_base_feedback", use_container_width=True):
                        if user_feedback.strip():
                            with st.spinner("🤖 Regenerating resume based on your feedback..."):
                                # Set up client
                                if HAS_GENAI:
                                    local_client = genai.Client(api_key=api_key) if api_key else default_client
                                    if not local_client:
                                        st.error("No valid API client available")
                                        st.stop()
                                else:
                                    local_client = None
                                
                                # Regenerate based on feedback
                                improved_latex, new_score = improve_base_resume_with_feedback(
                                    local_client, 
                                    base_resume_data["latex_code"], 
                                    st.session_state.get('base_resume_content', ''),
                                    user_feedback,
                                    base_resume_data.get("score", 0)
                                )
                                
                                if improved_latex:
                                    # Update the stored resume data
                                    base_resume_data["latex_code"] = improved_latex
                                    base_resume_data["score"] = new_score
                                    base_resume_data["feedback"] = f"Resume regenerated based on user feedback. New ATS score: {new_score}/100"
                                    base_resume_data["optimization_message"] = f"Resume improved based on your feedback. ATS score improved from {base_resume_data.get('score', 0)} to {new_score}/100"
                                    st.session_state.resume_store[st.session_state.current_base_resume_id] = base_resume_data
                                    
                                    st.success(f"✅ Resume regenerated successfully! New ATS Score: {new_score}/100")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to regenerate resume. Please try again.")
                        else:
                            st.error("Please provide feedback first.")
                
                with col_feedback2:
                    if st.button("🗑️ Clear Feedback", key="clear_base_feedback", use_container_width=True):
                        st.rerun()
                
                # AI Feedback
                st.markdown("### 💬 AI Feedback")
                if base_resume_data.get("feedback"):
                    st.info(base_resume_data["feedback"])
                
                if base_resume_data.get("optimization_message"):
                    st.success(base_resume_data["optimization_message"])
                
                # LaTeX code display
                st.markdown("### 📄 Generated LaTeX Code")
                base_latex_code = base_resume_data.get("latex_code", "")
                if base_latex_code:
                    st.code(base_latex_code, language="latex", line_numbers=True)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Base Resume",
                        data=base_latex_code,
                        file_name=f"base_resume_{base_resume_data.get('company_name', 'generated')}.tex",
                        mime="application/x-tex",
                        key="download_base_latex",
                        use_container_width=True
                    )
                else:
                    st.info("Generate a base resume to see LaTeX code here")
            else:
                st.info("👆 Fill in the form on the left to generate your base resume")
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666;">Developed by <a href="https://ibrahimsaleem.com" target="_blank">Mohammad Ibrahim Saleem</a></p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
