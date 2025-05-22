# AI-ResumeMaker

## AI Powered Tailored Resume Making Tool

### Live Demo
[AI Resume Maker](https://airesumemaker.onrender.com/)

---

## About
AI ResumeMaker is an advanced web application that transforms your plain text resume into a professionally formatted LaTeX document. By leveraging Google Gemini AI, it can analyze, optimize, and tailor your resume to specific job descriptions, ensuring your resume is both ATS-friendly and highly relevant to your target role. The app also provides detailed skills analysis, feedback, and allows you to download or copy LaTeX code for use in Overleaf or other LaTeX editors.

---

## Features
- **Passcode-Protected Login:** Secure access to the app with a passcode`).
- **AI-Powered Resume Formatting:** Converts plain text resumes into professional LaTeX resumes using a customizable template.
- **Job Description Tailoring:** Optimizes and aligns your resume content to match any provided job description.
- **Dynamic Skills Analysis:**
  - Extracts, analyzes, and categorizes all skills and certifications from your resume.
  - Compares your skills to job requirements and recommends additional skills/certifications.
  - Profession-aware: adapts skill categories to your field (e.g., Data Science, Cybersecurity, Civil Engineering, etc.).
- **LaTeX Skills Section Generator:**
  - Generates a LaTeX-formatted skills & certifications section, always including certifications.
  - Ensures the section length is concise and similar to your original resume.
  - Copy the LaTeX code with one click for easy use in Overleaf.
- **Feedback & Scoring:**
  - Provides a match score (1-10) and detailed feedback on how well your resume fits the job description.
  - Automatic optimization if your initial score is low.
- **Download & Copy:**
  - Download the full LaTeX resume as a `.tex` file.
  - Copy the entire LaTeX code or just the skills section to your clipboard.
- **User-Friendly Interface:**
  - Modern, responsive UI with tabs for Resume, Skills Analysis, and Feedback.
  - Syntax highlighting for LaTeX code.
- **API Key Optional:**
  - Use your own [Google Gemini API Key](https://www.youtube.com/watch?v=RGgVdjI66rs) for best results, or use the default (limited) mode.

---

## How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/ibrahimsaleem/AI-ResumeMaker.git
cd AI-ResumeMaker
```

### 2. (Recommended) Create a Virtual Environment
```bash
python -m venv resumeENV
source resumeENV/bin/activate  # On Windows: resumeENV\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables (Optional)
- To use your own Gemini API key, set the environment variable:
  - On Linux/macOS:
    ```bash
    export GENAI_API_KEY=your-gemini-api-key
    ```
  - On Windows:
    ```powershell
    $env:GENAI_API_KEY="your-gemini-api-key"
    ```
- If not set, the app will use a default (limited) key.

### 5. Run the App
```bash
python app.py
```
- The app will start on [http://127.0.0.1:5000](http://127.0.0.1:5000)

### 6. Login
- Go to the app in your browser.
- Enter the passcode: `ibrahim@aplyease4139`

---

## Usage Instructions
1. (Optional) Enter your [Gemini API Key](https://www.youtube.com/watch?v=RGgVdjI66rs) for best AI results.
2. Paste your resume content in plain text.
3. Enter the company name and job description to tailor your resume.
4. Click "Generate Resume".
5. Explore the tabs for:
   - **LaTeX Resume:** View, copy, or download the full LaTeX code.
   - **Skills Analysis:** See extracted, missing, and recommended skills, plus a LaTeX skills section (with copy button).
   - **Feedback:** Read AI-generated feedback and your resume-job match score.
6. Use the "Regenerate" and "Re-analyze" buttons to further refine your resume and skills section.

---

## How to Convert LaTeX Code to PDF
1. Copy the generated LaTeX code (full resume or skills section).
2. Open [Overleaf](https://www.overleaf.com/).
3. Create a new LaTeX project.
4. Paste the code into Overleaf.
5. Click "Compile" to generate your PDF.
6. Download your professional, ATS-friendly resume.

---

## Developer
- **Mohammad Ibrahim Saleem**
- [LinkedIn](https://www.linkedin.com/in/ibrahimsaleem91/)
- [Buy me a coffee](https://buymeacoffee.com/ibrahimsaleem)

---

## License
This project is for educational and personal use. For commercial use, please contact the developer.
