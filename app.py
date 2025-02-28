import os 
import logging
import uuid
from flask import Flask, request, render_template_string, jsonify, Response

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

# In-memory store for resumes. Each entry will be a dict with keys:
# "latex_code": the LaTeX content, "score": the alignment score, "api_key": the API key used (if any)
resume_store = {}

# Default LaTeX resume template
DEFAULT_LATEX_TEMPLATE = r""" %-------------------------
% Resume in Latex
% Author : Jake Gutierrez
% Based off of: https://github.com/sb2nov/resume
% License : MIT
%------------------------

\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\input{glyphtounicode}


%----------FONT OPTIONS----------
% sans-serif
% \usepackage[sfdefault]{FiraSans}
% \usepackage[sfdefault]{roboto}
% \usepackage[sfdefault]{noto-sans}
% \usepackage[default]{sourcesanspro}

% serif
% \usepackage{CormorantGaramond}
% \usepackage{charter}


\pagestyle{fancy}
\fancyhf{} % clear all header and footer fields
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

% Ensure that generate pdf is machine readable/ATS parsable
\pdfgentounicode=1

%-------------------------
% Custom commands
\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small#1} & \textit{\small #2} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

%-------------------------------------------
%%%%%%  RESUME STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%


\begin{document}

%----------HEADING----------
% \begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}}r}
%   \textbf{\href{http://sourabhbajaj.com/}{\Large Sourabh Bajaj}} & Email : \href{mailto:sourabh@sourabhbajaj.com}{sourabh@sourabhbajaj.com}\\
%   \href{http://sourabhbajaj.com/}{http://www.sourabhbajaj.com} & Mobile : +1-123-456-7890 \\
% \end{tabular*}

\begin{center}
    \textbf{\Huge \scshape Jake Ryan} \\ \vspace{1pt}
    \small 123-456-7890 $|$ \href{mailto:x@x.com}{\underline{jake@su.edu}} $|$ 
    \href{https://linkedin.com/in/...}{\underline{linkedin.com/in/jake}} $|$
    \href{https://github.com/...}{\underline{github.com/jake}}
\end{center}


%-----------EDUCATION-----------
\section{Education}
  \resumeSubHeadingListStart
    \resumeSubheading
      {Southwestern University}{Georgetown, TX}
      {Bachelor of Arts in Computer Science, Minor in Business}{Aug. 2018 -- May 2021}
    \resumeSubheading
      {Blinn College}{Bryan, TX}
      {Associate's in Liberal Arts}{Aug. 2014 -- May 2018}
  \resumeSubHeadingListEnd


%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart

    \resumeSubheading
      {Undergraduate Research Assistant}{June 2020 -- Present}
      {Texas A\&M University}{College Station, TX}
      \resumeItemListStart
        \resumeItem{Developed a REST API using FastAPI and PostgreSQL to store data from learning management systems}
        \resumeItem{Developed a full-stack web application using Flask, React, PostgreSQL and Docker to analyze GitHub data}
        \resumeItem{Explored ways to visualize GitHub collaboration in a classroom setting}
      \resumeItemListEnd
      
% -----------Multiple Positions Heading-----------
%    \resumeSubSubheading
%     {Software Engineer I}{Oct 2014 - Sep 2016}
%     \resumeItemListStart
%        \resumeItem{Apache Beam}
%          {Apache Beam is a unified model for defining both batch and streaming data-parallel processing pipelines}
%     \resumeItemListEnd
%    \resumeSubHeadingListEnd
%-------------------------------------------

    \resumeSubheading
      {Information Technology Support Specialist}{Sep. 2018 -- Present}
      {Southwestern University}{Georgetown, TX}
      \resumeItemListStart
        \resumeItem{Communicate with managers to set up campus computers used on campus}
        \resumeItem{Assess and troubleshoot computer problems brought by students, faculty and staff}
        \resumeItem{Maintain upkeep of computers, classroom equipment, and 200 printers across campus}
    \resumeItemListEnd

    \resumeSubheading
      {Artificial Intelligence Research Assistant}{May 2019 -- July 2019}
      {Southwestern University}{Georgetown, TX}
      \resumeItemListStart
        \resumeItem{Explored methods to generate video game dungeons based off of \emph{The Legend of Zelda}}
        \resumeItem{Developed a game in Java to test the generated dungeons}
        \resumeItem{Contributed 50K+ lines of code to an established codebase via Git}
        \resumeItem{Conducted  a human subject study to determine which video game dungeon generation technique is enjoyable}
        \resumeItem{Wrote an 8-page paper and gave multiple presentations on-campus}
        \resumeItem{Presented virtually to the World Conference on Computational Intelligence}
      \resumeItemListEnd

  \resumeSubHeadingListEnd


%-----------PROJECTS-----------
\section{Projects}
    \resumeSubHeadingListStart
      \resumeProjectHeading
          {\textbf{Gitlytics} $|$ \emph{Python, Flask, React, PostgreSQL, Docker}}{June 2020 -- Present}
          \resumeItemListStart
            \resumeItem{Developed a full-stack web application using with Flask serving a REST API with React as the frontend}
            \resumeItem{Implemented GitHub OAuth to get data from user’s repositories}
            \resumeItem{Visualized GitHub data to show collaboration}
            \resumeItem{Used Celery and Redis for asynchronous tasks}
          \resumeItemListEnd
      \resumeProjectHeading
          {\textbf{Simple Paintball} $|$ \emph{Spigot API, Java, Maven, TravisCI, Git}}{May 2018 -- May 2020}
          \resumeItemListStart
            \resumeItem{Developed a Minecraft server plugin to entertain kids during free time for a previous job}
            \resumeItem{Published plugin to websites gaining 2K+ downloads and an average 4.5/5-star review}
            \resumeItem{Implemented continuous delivery using TravisCI to build the plugin upon new a release}
            \resumeItem{Collaborated with Minecraft server administrators to suggest features and get feedback about the plugin}
          \resumeItemListEnd
    \resumeSubHeadingListEnd



%
%-----------PROGRAMMING SKILLS-----------
\section{Technical Skills}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
     \textbf{Languages}{: Java, Python, C/C++, SQL (Postgres), JavaScript, HTML/CSS, R} \\
     \textbf{Frameworks}{: React, Node.js, Flask, JUnit, WordPress, Material-UI, FastAPI} \\
     \textbf{Developer Tools}{: Git, Docker, TravisCI, Google Cloud Platform, VS Code, Visual Studio, PyCharm, IntelliJ, Eclipse} \\
     \textbf{Libraries}{: pandas, NumPy, Matplotlib}
    }}
 \end{itemize}


%-------------------------------------------
\end{document}

"""

@app.route("/", methods=["GET"])
def index():
    html_template = '''
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <title>AI Resume Generator</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 20px auto;
                padding: 20px;
                background-color: #f9f9f9;
            }
            .app-container {
                background: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
            }
            .app-container h2 {
                margin-bottom: 15px;
                font-size: 26px;
                color: #222;
                text-align: center;
            }
            /* Process container */
            #process-container {
                margin-bottom: 20px;
                max-height: 300px;
                overflow-y: auto;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background-color: #fafafa;
            }
            /* Message bubbles */
            .message {
                margin: 10px 0;
                padding: 10px;
                border-radius: 10px;
                width: fit-content;
                max-width: 80%;
                word-wrap: break-word;
            }
            .user-message {
                background-color: #d1ecf1;
                color: #0c5460;
                font-weight: bold;
                margin-left: auto;
            }
            .system-message {
                background-color: #d4edda;
                color: #155724;
                margin-right: auto;
            }
            .error-message {
                background-color: #f8d7da;
                color: #721c24;
                margin-right: auto;
            }
            .input-area {
                width: 100%;
                padding: 12px;
                margin-top: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 16px;
                box-sizing: border-box;
            }
            textarea.input-area {
                min-height: 150px;
                resize: vertical;
            }
            .submit-btn {
                margin-top: 10px;
                padding: 12px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                width: 100%;
            }
            .submit-btn:hover {
                opacity: 0.9;
            }
            pre {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                white-space: pre-wrap;
                margin-top: 5px;
                border: 1px solid #ddd;
                max-height: 300px;
                overflow-y: auto;
                font-size: 12px;
            }
            .hidden {
                display: none;
            }
            .action-btn {
                display: inline-block;
                margin-right: 10px;
                margin-top: 10px;
                padding: 10px 15px;
                border-radius: 5px;
                color: white;
                cursor: pointer;
                text-decoration: none;
                text-align: center;
                font-size: 14px;
            }
            .view-latex-btn {
                background-color: #17a2b8;
            }
            .new-resume-btn {
                background-color: #6c757d;
            }
            .code-container {
                margin-top: 20px;
                display: none;
            }
            .tabs {
                display: flex;
                margin-top: 20px;
                border-bottom: 1px solid #ddd;
            }
            .tab {
                padding: 10px 15px;
                cursor: pointer;
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-bottom: none;
                border-radius: 5px 5px 0 0;
                margin-right: 5px;
            }
            .tab.active {
                background-color: white;
                border-bottom: 1px solid white;
                margin-bottom: -1px;
            }
            .tab-content {
                display: none;
                padding: 15px;
                border: 1px solid #ddd;
                border-top: none;
                background-color: white;
            }
            .tab-content.active {
                display: block;
            }
            .score-container {
                text-align: center;
                margin: 20px 0;
                padding: 15px;
                border-radius: 5px;
                background-color: #f8f9fa;
                border: 1px solid #ddd;
            }
            .score {
                font-size: 32px;
                font-weight: bold;
                margin: 10px 0;
            }
            .score-high {
                color: #28a745;
            }
            .score-medium {
                color: #ffc107;
            }
            .score-low {
                color: #dc3545;
            }
            .score-label {
                font-size: 14px;
                color: #6c757d;
            }
        </style>
      </head>
      <body>
        <div class="app-container">
            <h2>AI Resume Generator</h2>
            
            <!-- Process area -->
            <div id="process-container"></div>
            
            <!-- Form for resume input -->
            <form id="resume-form">
                <!-- Optional field for user's Gemini API key -->
                <input type="text" id="api_key" name="api_key" class="input-area"
                       placeholder="Enter your Gemini API key (optional)" /><br>
                <textarea id="resume_content" name="resume_content" class="input-area"
                       placeholder="Paste your resume content in plain text..."></textarea><br>
                <!-- Job Description Field -->
                <textarea id="job_description" name="job_description" class="input-area"
                       placeholder="Enter the job description to tailor your resume..."></textarea><br>
                <button type="submit" class="submit-btn">Generate Resume</button>
            </form>
            
            <!-- Tabs for LaTeX code and actions -->
            <div id="result-tabs" class="hidden">
                <!-- Job Match Score -->
                <div id="score-container" class="score-container">
                    <div class="score-label">JOB MATCH SCORE</div>
                    <div id="match-score" class="score">0/10</div>
                    <div id="score-feedback">Processing your resume...</div>
                </div>
                
                <div class="tabs">
                    <div class="tab active" data-tab="latex-tab">LaTeX Code</div>
                    <div class="tab" data-tab="actions-tab">Actions</div>
                </div>
                
                <!-- LaTeX Code Tab -->
                <div id="latex-tab" class="tab-content active">
                    <pre id="latex-code"></pre>
                    <button id="copy-latex-btn" class="action-btn view-latex-btn">Copy LaTeX Code</button>
                </div>
                
               <!-- Add this to the Actions Tab in the HTML -->
                <div id="actions-tab" class="tab-content">
                  <p>Your resume has been processed. You can:</p>
                 <div id="download-options">
                   <a id="download-latex" href="#" class="action-btn view-latex-btn">Download LaTeX File</a>
                 </div>
                 <button type="button" id="reoptimize-btn" class="action-btn view-latex-btn" style="background-color: #28a745;">Re-optimize Resume</button>
                 <button type="button" id="new-resume-btn" class="action-btn new-resume-btn">Create New Resume</button>
                </div>
            </div>
        </div>
        
        <script>
            const processContainer = document.getElementById("process-container");
            const resumeForm = document.getElementById("resume-form");
            const apiKeyInput = document.getElementById("api_key");
            const resumeContentInput = document.getElementById("resume_content");
            const jobDescriptionInput = document.getElementById("job_description");
            const resultTabs = document.getElementById("result-tabs");
            const latexCodeElement = document.getElementById("latex-code");
            const copyLatexBtn = document.getElementById("copy-latex-btn");
            const downloadLatexLink = document.getElementById("download-latex");
            const newResumeBtn = document.getElementById("new-resume-btn");
            const matchScoreElement = document.getElementById("match-score");
            const scoreFeedbackElement = document.getElementById("score-feedback");
            let currentResumeId = null;

            // Set up tabs
            document.querySelectorAll('.tab').forEach(tab => {
                tab.addEventListener('click', () => {
                    // Remove active class from all tabs and content
                    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                    
                    // Add active class to clicked tab
                    tab.classList.add('active');
                    
                    // Show corresponding content
                    const tabId = tab.getAttribute('data-tab');
                    document.getElementById(tabId).classList.add('active');
                });
            });

            // Function to update the match score display
            function updateScoreDisplay(score) {
                matchScoreElement.textContent = score + "/10";
                
                // Remove any existing score classes
                matchScoreElement.classList.remove("score-high", "score-medium", "score-low");
                
                // Add appropriate class based on score
                if (score >= 8) {
                    matchScoreElement.classList.add("score-high");
                    scoreFeedbackElement.textContent = "Excellent match with the job description!";
                } else if (score >= 6) {
                    matchScoreElement.classList.add("score-medium");
                    scoreFeedbackElement.textContent = "Good match with the job description.";
                } else {
                    matchScoreElement.classList.add("score-low");
                    scoreFeedbackElement.textContent = "Could be better aligned with the job description.";
                }
            }

            // Handle the resume generation
            resumeForm.addEventListener("submit", function(e) {
                e.preventDefault();
                const apiKey = apiKeyInput.value.trim();
                const resumeContent = resumeContentInput.value.trim();
                const jobDescription = jobDescriptionInput.value.trim();
                if (!resumeContent) {
                    addMessage("Please enter your resume content.", "error-message");
                    return;
                }
                
                if (!jobDescription) {
                    addMessage("Please provide a job description for better resume tailoring.", "error-message");
                    return;
                }

                addMessage("Submitting resume content...", "user-message");
                addMessage("Job description included for tailoring.", "user-message");
                addMessage("Processing... please wait.", "system-message");
                
                // Build POST body including API key and job description
                let body = "resume_content=" + encodeURIComponent(resumeContent);
                body += "&job_description=" + encodeURIComponent(jobDescription);
                if(apiKey) {
                    body += "&api_key=" + encodeURIComponent(apiKey);
                }

                // Send POST request to /generate_resume
                fetch("/generate_resume", {
                    method: "POST",
                    headers: {"Content-Type": "application/x-www-form-urlencoded"},
                    body: body
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        addMessage("Error: " + data.error, "error-message");
                    } else {
                        addMessage("Resume processed successfully!", "system-message");
                        addMessage("Job match score: " + data.score + "/10", "system-message");
                        
                        if (data.optimized) {
                            addMessage("Resume was automatically optimized to better match the job description.", "system-message");
                        }
                        
                        resumeForm.classList.add("hidden");
                        resultTabs.classList.remove("hidden");
                        currentResumeId = data.resume_id;
                        
                        // Display LaTeX code
                        latexCodeElement.textContent = data.latex_code;
                        
                        // Update score display
                        updateScoreDisplay(data.score);
                        
                        // Set up download link
                        downloadLatexLink.href = "/download_latex/" + currentResumeId;
                        downloadLatexLink.download = "resume.tex";
                    }
                })
                .catch(error => {
                    addMessage("Error: " + error, "error-message");
                });
            });

            // Copy LaTeX code to clipboard
            copyLatexBtn.addEventListener("click", () => {
                navigator.clipboard.writeText(latexCodeElement.textContent)
                    .then(() => {
                        addMessage("LaTeX code copied to clipboard", "system-message");
                    })
                    .catch(err => {
                        addMessage("Failed to copy: " + err, "error-message");
                    });
            });

            // Handle "Create New Resume"
            newResumeBtn.addEventListener("click", () => {
                resumeForm.classList.remove("hidden");
                resultTabs.classList.add("hidden");
                // Clear previous values
                // resumeContentInput.value = "";
                // jobDescriptionInput.value = "";
                currentResumeId = null;
            });

            // Helper function to add messages to the process container
            function addMessage(text, className) {
                const messageDiv = document.createElement("div");
                messageDiv.className = "message " + className;
                messageDiv.textContent = text;
                processContainer.appendChild(messageDiv);
                processContainer.scrollTop = processContainer.scrollHeight;
            }
        // Handle "Re-optimize Resume"
const reoptimizeBtn = document.getElementById("reoptimize-btn");
reoptimizeBtn.addEventListener("click", () => {
    const currentLatex = latexCodeElement.textContent;
    const jobDescription = jobDescriptionInput.value.trim();
    const apiKey = apiKeyInput.value.trim();
    
    if (!currentLatex || !jobDescription) {
        addMessage("Missing information for re-optimization.", "error-message");
        return;
    }
    
    addMessage("Requesting further optimization...", "user-message");
    addMessage("Processing... please wait.", "system-message");
    
    // Build POST body including the current LaTeX code
    let body = "resume_content=" + encodeURIComponent(currentLatex);
    body += "&job_description=" + encodeURIComponent(jobDescription);
    body += "&is_reoptimization=true"; // Flag to indicate this is a re-optimization request
    
    if(apiKey) {
        body += "&api_key=" + encodeURIComponent(apiKey);
    }
    
    // Send POST request to /generate_resume
    fetch("/generate_resume", {
        method: "POST",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: body
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            addMessage("Error: " + data.error, "error-message");
        } else {
            addMessage("Resume re-optimized successfully!", "system-message");
            addMessage("New job match score: " + data.score + "/10", "system-message");
            
            // Update current resume ID
            currentResumeId = data.resume_id;
            
            // Display updated LaTeX code
            latexCodeElement.textContent = data.latex_code;
            
            // Update score display
            updateScoreDisplay(data.score);
            
            // Update download link
            downloadLatexLink.href = "/download_latex/" + currentResumeId;
        }
    })
    .catch(error => {
        addMessage("Error: " + error, "error-message");
    });
});
        </script>
      </body>
    </html>
    '''
    return render_template_string(html_template)

@app.route("/generate_resume", methods=["POST"])
def generate_resume():
    """Handles the resume generation process using Gemini AI."""
    resume_content = request.form.get("resume_content")
    job_description = request.form.get("job_description")
    provided_api_key = request.form.get("api_key")
    
    if not resume_content:
        return jsonify({"error": "No resume content provided"})
    
    if not job_description:
        return jsonify({"error": "Job description is required for tailoring"})
    
    # Use the provided API key if available; otherwise, use default
    if HAS_GENAI:
        local_client = genai.Client(api_key=provided_api_key) if provided_api_key else default_client
    else:
        local_client = None

    try:
        logging.info("Starting resume processing")
        
        # Process the resume content with Gemini
        latex_code = process_with_gemini(local_client, resume_content, job_description)
        
        # Evaluate the resume's alignment with the job description
        score, feedback = evaluate_resume_job_match(local_client, latex_code, job_description)
        
        optimized = False
        
        # If score is below 7, reprocess to better align with job description
        if score < 8:
            logging.info(f"Initial score {score}/10 is below threshold. Reprocessing resume...")
            latex_code = optimize_resume_for_job(local_client, latex_code, job_description, feedback)
            optimized = True
            
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

        return jsonify({
            "resume_id": resume_id,
            "latex_code": latex_code,
            "score": score,
            "feedback": feedback,
            "optimized": optimized,
            "message": "Resume generated successfully"
        })

    except Exception as e:
        logging.exception("An error occurred during resume generation")
        return jsonify({"error": f"An error occurred: {e}"})

@app.route("/download_latex/<resume_id>", methods=["GET"])
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
    latex_code = latex_code.replace("Jakeryan@example.com", contact_info["email"])
    latex_code = latex_code.replace("(123) 456-7890", contact_info["phone"])
    
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
You are a professional resume formatter specializing in LaTeX documents. Your task is to transform the provided plain text resume into a structured LaTeX document that aligns precisely with the job description (when provided).

If a job description is included, use it to strategically tailor the resume, emphasizing relevant skills and experiences that meet the position's requirements.

FORMATTING REQUIREMENTS:

- Strict One-Page Limit: Ensure the resume does not exceed a single page while preserving all user-provided content, including experience and projects.
- Proper LaTeX Syntax: Maintain correct LaTeX formatting and escape special characters where necessary.
- Document Structure: Preserve the structural integrity and formatting of the given LaTeX template.
- Complete Information: Populate all relevant fields, including name, contact details, education, experience, and skills.

Content Tailoring (If Job Description is Provided):
- Incorporate job-specific keywords and skills seamlessly into work experience and projects.
- Prioritize experiences and skills that directly align with the job’s requirements.
- Highlight relevant achievements with quantifiable metrics (e.g., "Optimized performance, increasing efficiency by 40%").
- Adjust coursework listings (if applicable) to emphasize relevant academic background.

Space Optimization (Without Removing Content):
- Use concise and impactful language while keeping all provided experience and projects.
- Optimize formatting elements like font size, margin adjustments, and section spacing to fit within one page without loss of content.
- Utilize line spacing effectively to avoid single-word lines and maximize readability.
- Balance content density for a clean, professional layout without overcrowding.

Output Instructions:
Return only the complete, properly formatted LaTeX code. Do not include explanations, comments, markdown syntax, or code block markers.

LaTeX Template Reference:
Use the provided LaTeX template structure for formatting but do not return the template itself. Instead, format the user’s resume content accordingly.

LaTeX Template
```
{DEFAULT_LATEX_TEMPLATE}
```

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
You are an expert ATS (Applicant Tracking System) resume evaluator with 15+ years of technical recruiting experience. Conduct a comprehensive analysis of how well this LaTeX resume aligns with the specified job description.

JOB DESCRIPTION:
```
{job_description}
```
LATEX RESUME:
```
{latex_code}
```

EVALUATION INSTRUCTIONS:

1. First, extract the top 10-15 critical requirements from the job description:
   - Required technical skills and tools
   - Experience level and background needed
   - Educational requirements
   - Specific domain knowledge
   - Soft skills and competencies

2. For each requirement, analyze whether the resume effectively demonstrates qualification:
   - Exact keyword match (highest value)
   - Semantic match using related terminology
   - Demonstrated experience with quantifiable results
   - Missing or inadequately addressed requirements

3. Evaluate resume optimization factors:
   - Prominence of key qualifications (position on page, emphasis)
   - Use of job-specific terminology and language
   - Quantification of relevant achievements
   - Overall content prioritization for this specific role

4. Calculate a precise match score from 1-10 based on:
   - 8-10: Excellent match (80%+ of key requirements addressed effectively)
   - 6-7: Good match (60-79% of requirements addressed)
   - 4-5: Average match (40-59% of requirements addressed)
   - 1-3: Poor match (under 40% of requirements addressed)

RESPONSE FORMAT:
SCORE: [whole number 1-10]
FEEDBACK: [150-300 word analysis including:
- Overall assessment of match quality
- 3-5 specific strengths (with examples from the resume)
- 3-5 specific improvement opportunities with actionable recommendations
- Key missing elements or terms that should be added]
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
You are an expert LaTeX resume optimizer with extensive experience in professional resume tailoring. Your task is to transform the provided LaTeX resume to precisely match the job requirements while maintaining perfect LaTeX formatting.

If a job description is included, use it to strategically tailor the resume, ensuring that relevant skills and experiences align with the position's requirements.

OPTIMIZATION REQUIREMENTS:

1. ONE-PAGE MAXIMUM: Ensure the resume remains within a single page while retaining all user-provided content, including experience and projects.

2. JOB-SPECIFIC ALIGNMENT:
   - Integrate key terms and phrases from the job description naturally throughout the resume.
   - Reorder and prioritize experiences/skills to match job requirements.
   - Replace generic statements with job-relevant accomplishments.
   - Adjust section ordering if necessary to emphasize the most relevant qualifications first.

3. QUANTIFIABLE ACHIEVEMENTS:
   - Convert general statements into specific, measurable outcomes (e.g., "Increased efficiency by 35%").
   - Add metrics and specific results wherever possible.
   - Emphasize achievements that directly relate to the job requirements.

4. SPACE OPTIMIZATION (Without Removing Content):
   - Utilize line space efficiently (avoid lines with just one or two words).
   - Balance content density while maintaining readability.
   - Eliminate redundancies and non-essential information.
   - Use full lines of text rather than leaving white space.
   - Adjust formatting elements like font size, margin adjustments, and section spacing to fit within one page.

5. COURSEWORK RELEVANCE:
   - Adjust coursework listings to showcase an academic background relevant to the position.
   - Replace less relevant courses with more applicable ones based on the job description.

6. LANGUAGE ENHANCEMENT:
   - Use action verbs and impactful language that mirrors job description terminology.
   - Replace passive voice with active, accomplishment-focused statements.
   - Eliminate filler words and redundancies for maximum impact.

7. PERFECT LATEX FORMATTING:
   - Maintain proper LaTeX syntax and correct escaping of special characters.
   - Preserve document structure while optimizing content.
   - Ensure formatting consistency throughout the document.

Output Instructions:
- Return only the complete, optimized LaTeX code.
- Do not include explanations, comments, markdown syntax, or code block markers.

LaTeX Template Reference:
Use the provided LaTeX template for formatting but do not return the template itself. Instead, apply its formatting principles to the user’s resume content.

LaTeX Template:
```
{DEFAULT_LATEX_TEMPLATE}
```

Current LaTeX Resume to Optimize:
```
{latex_code}
```

Job Description:
```
{job_description}
```

Previous Evaluation Feedback (If Available):
```
{feedback}
```


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

def iterative_resume_optimization(client, latex_code, job_description, feedback, max_iterations=2):
    """
    Calls the optimize_resume_for_job function iteratively, passing its output back into itself
    to further refine the resume until a desired optimization level is reached or max iterations are met.

    :param client: AI client used for content generation
    :param latex_code: Initial LaTeX resume code
    :param job_description: Job description text
    :param feedback: Feedback on the resume's alignment with the job
    :param max_iterations: Maximum number of iterations to refine the resume
    :return: Final optimized LaTeX resume code
    """
    optimized_resume = latex_code
    for i in range(max_iterations):
        logging.info(f"Iteration {i+1}: Optimizing resume...")
        
        new_feedback = f"Iteration {i+1} feedback: Improve alignment further."  # Can be dynamically set
        optimized_resume = optimize_resume_for_job(client, optimized_resume, job_description, new_feedback)
        
        if optimized_resume == latex_code:
            logging.info("No further improvements made. Stopping iterations.")
            break  # Stop if no improvements were made

        latex_code = optimized_resume  # Update the latest version for the next iteration

    logging.info("Final resume optimization complete.")
    return optimized_resume


if __name__ == "__main__":
    app.run(debug=True)
