document.addEventListener('DOMContentLoaded', function() {
    const resumeForm = document.getElementById('resume-form');
    const processContainer = document.getElementById('process-container');
    const apiKeyContainer = document.getElementById('api-key-container');
    const apiKeyInput = document.getElementById('api-key');
    const resultContainer = document.getElementById('result-container');
    const latexCodeContainer = document.getElementById('latex-code');
    const latexTab = document.getElementById('latex-tab');
    const feedbackTab = document.getElementById('feedback-tab');
    const skillsTab = document.getElementById('skills-tab');
    const latexContent = document.getElementById('latex-content');
    const feedbackContent = document.getElementById('feedback-content');
    const skillsContent = document.getElementById('skills-content');
    const scoreDisplay = document.getElementById('score-display');
    const optimizedBadge = document.getElementById('optimized-badge');
    const companyNameInput = document.getElementById('company-name');
    const mainHeading = document.querySelector('.app-container h2');

    // Function to add a message to the process container
    function addMessage(message, className) {
        const messageElem = document.createElement('div');
        messageElem.className = `message ${className || 'system-message'}`;
        messageElem.textContent = message;
        processContainer.appendChild(messageElem);
        processContainer.scrollTop = processContainer.scrollHeight;
    }

    // Function to update skills lists
    function updateSkillsLists(skillsData) {
        console.log('Updating skills with data:', skillsData);  // Debug log
        
        const currentSkillsList = document.getElementById('current-skills-list');
        const missingSkillsList = document.getElementById('missing-skills-list');
        const recommendedSkillsList = document.getElementById('recommended-skills-list');
        const latexSkillsSection = document.getElementById('latex-skills-section');
        
        if (!currentSkillsList || !missingSkillsList || !recommendedSkillsList || !latexSkillsSection) {
            console.error('Skills list elements not found');  // Debug log
            return;
        }
        
        // Clear existing lists
        currentSkillsList.innerHTML = '';
        missingSkillsList.innerHTML = '';
        recommendedSkillsList.innerHTML = '';

        // Helper function to create category section
        const createCategorySection = (title) => {
            const section = document.createElement('div');
            section.className = 'skills-category';
            const titleElem = document.createElement('h4');
            titleElem.textContent = title;
            section.appendChild(titleElem);
            return section;
        };

        // Helper function to populate category
        const populateCategory = (container, skills) => {
            if (!Array.isArray(skills)) {
                console.error('Skills items is not an array:', skills);
                return false;
            }
            const ul = document.createElement('ul');
            skills.forEach(skill => {
                if (skill && skill.trim()) {
                    const li = document.createElement('li');
                    li.textContent = skill;
                    ul.appendChild(li);
                }
            });
            if (ul.children.length > 0) {
                container.appendChild(ul);
                return true;
            }
            return false;
        };

        // Handle current skills by category
        let hasCurrentSkills = false;
        if (skillsData.current_skills_by_category) {
            for (const [category, skills] of Object.entries(skillsData.current_skills_by_category)) {
                const section = createCategorySection(category);
                if (populateCategory(section, skills)) {
                    currentSkillsList.appendChild(section);
                    hasCurrentSkills = true;
                }
            }
        } else if (Array.isArray(skillsData.current_skills)) {
            // Fallback to flat list if no categories
            hasCurrentSkills = populateCategory(currentSkillsList, skillsData.current_skills);
        }
        
        if (!hasCurrentSkills) {
            const li = document.createElement('li');
            li.textContent = 'No skills found';
            li.style.fontStyle = 'italic';
            li.style.color = '#666';
            currentSkillsList.appendChild(li);
        }

        // Handle missing skills
        populateCategory(missingSkillsList, skillsData.missing_skills || []) || 
            (missingSkillsList.innerHTML = '<li style="font-style: italic; color: #666;">No missing skills</li>');

        // Handle recommended skills by category
        let hasRecommendedSkills = false;
        if (skillsData.recommended_skills_by_category) {
            for (const [category, skills] of Object.entries(skillsData.recommended_skills_by_category)) {
                const section = createCategorySection(category);
                if (populateCategory(section, skills)) {
                    recommendedSkillsList.appendChild(section);
                    hasRecommendedSkills = true;
                }
            }
        } else if (Array.isArray(skillsData.recommended_skills)) {
            // Fallback to flat list if no categories
            hasRecommendedSkills = populateCategory(recommendedSkillsList, skillsData.recommended_skills);
        }

        if (!hasRecommendedSkills) {
            const li = document.createElement('li');
            li.textContent = 'No recommended skills';
            li.style.fontStyle = 'italic';
            li.style.color = '#666';
            recommendedSkillsList.appendChild(li);
        }

        // Update LaTeX skills section
        if (skillsData.latex_skills_section) {
            latexSkillsSection.textContent = skillsData.latex_skills_section;
            // If Prism is available, highlight the syntax
            if (typeof Prism !== 'undefined') {
                Prism.highlightElement(latexSkillsSection);
            }
        } else {
            latexSkillsSection.textContent = 'No LaTeX skills section generated';
        }
    }

    // Tab switching
    latexTab.addEventListener('click', function() {
        latexTab.classList.add('active');
        feedbackTab.classList.remove('active');
        skillsTab.classList.remove('active');
        latexContent.style.display = 'block';
        feedbackContent.style.display = 'none';
        skillsContent.style.display = 'none';
    });

    feedbackTab.addEventListener('click', function() {
        feedbackTab.classList.add('active');
        latexTab.classList.remove('active');
        skillsTab.classList.remove('active');
        feedbackContent.style.display = 'block';
        latexContent.style.display = 'none';
        skillsContent.style.display = 'none';
    });

    skillsTab.addEventListener('click', function() {
        skillsTab.classList.add('active');
        latexTab.classList.remove('active');
        feedbackTab.classList.remove('active');
        skillsContent.style.display = 'block';
        latexContent.style.display = 'none';
        feedbackContent.style.display = 'none';
    });

    // Function to update tab and heading with company name
    function updateCompanyNameUI() {
        const company = companyNameInput.value.trim();
        if (company) {
            document.title = `${company}'s Resume | AI Resume Generator`;
            if (mainHeading) mainHeading.textContent = `AI Resume Generator – ${company}`;
        } else {
            document.title = 'AI Resume Generator by Mohammad Ibrahim Saleem (Ibrahimsaleem.com)';
            if (mainHeading) mainHeading.textContent = 'AI Resume Generator';
        }
    }
    if (companyNameInput) {
        companyNameInput.addEventListener('input', updateCompanyNameUI);
    }
    // On page load, set title/heading if company name is present
    updateCompanyNameUI();

    // Form submission
    resumeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const resumeContent = document.getElementById('resume-content').value;
        const jobDescription = document.getElementById('job-description').value;
        const apiKey = apiKeyInput.value;
        const companyName = companyNameInput.value;
        
        if (!resumeContent) {
            addMessage("Please provide your resume content.", "error-message");
            return;
        }
        
        if (!jobDescription) {
            addMessage("Please provide a job description for tailoring.", "error-message");
            return;
        }
        
        // Show the process container and add initial message
        processContainer.style.display = 'block';
        resultContainer.style.display = 'none';
        processContainer.innerHTML = '';
        
        addMessage("Submitting resume for processing...", "system-message");
        
        const formData = new FormData();
        formData.append('resume_content', resumeContent);
        formData.append('job_description', jobDescription);
        formData.append('company_name', companyName);
        if (apiKey) formData.append('api_key', apiKey);
        
        // Send the form data to the server
        fetch('/generate_resume', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json().catch(error => {
                throw new Error('Invalid JSON response from server');
            });
        })
        .then(data => {
            if (data.error) {
                addMessage("Error: " + data.error, "error-message");
                return;
            }
            
            addMessage("Resume processed successfully!", "system-message");
            
            // Debug log for skills analysis data
            console.log('Received skills analysis:', data.skills_analysis);
            
            if (data.optimized) {
                addMessage("Resume was optimized to better match the job description.", "system-message");
                optimizedBadge.style.display = 'inline-block';
            } else {
                optimizedBadge.style.display = 'none';
            }
            document.getElementById('optimization-status').textContent = data.optimization_message || '';
            
            // Display the results
            latexCodeContainer.textContent = data.latex_code || 'No LaTeX code generated';
            feedbackContent.innerHTML = (data.feedback || 'No feedback available').replace(/\n/g, '<br>');
            scoreDisplay.textContent = (data.score || 0) + "/10";
            
            // Update company name in tab and heading if present
            if (data.company_name) {
                companyNameInput.value = data.company_name;
                updateCompanyNameUI();
            }
            
            // Update skills analysis with better error handling
            if (data.skills_analysis) {
                updateSkillsLists(data.skills_analysis);
                addMessage("Skills analysis completed successfully.", "system-message");
            } else {
                console.error('No skills analysis data received');
                addMessage("Skills analysis data not available.", "error-message");
            }
            
            if (data.score >= 8) {
                scoreDisplay.className = 'badge badge-success';
            } else if (data.score >= 6) {
                scoreDisplay.className = 'badge badge-primary';
            } else {
                scoreDisplay.className = 'badge badge-info';
            }
            
            // Show the result container
            resultContainer.style.display = 'block';
            
            // Set up the download link
            if (data.resume_id) {
                document.getElementById('download-link').href = '/download_latex/' + data.resume_id;
            }
            
            // Highlight syntax if Prism is available
            if (typeof Prism !== 'undefined' && latexCodeContainer.textContent) {
                Prism.highlightElement(latexCodeContainer);
            }
            
            document.getElementById('reoptimize-btn').style.display = 'inline-block';
        })
        .catch(error => {
            console.error('Error processing resume:', error);
            addMessage(`Error: ${error.message || 'Failed to process resume. Please try again.'}`, "error-message");
            resultContainer.style.display = 'none';
        });
    });

    // Reset form
    document.getElementById('new-resume-btn').addEventListener('click', function() {
        resultContainer.style.display = 'none';
        processContainer.style.display = 'none';
    });

    // Copy LaTeX button functionality
    document.getElementById('copy-latex-btn').addEventListener('click', function() {
        const latexCode = latexCodeContainer.textContent;
        navigator.clipboard.writeText(latexCode).then(function() {
            addMessage('LaTeX code copied to clipboard!', 'system-message');
        }, function(err) {
            addMessage('Failed to copy LaTeX code.', 'error-message');
        });
    });

    // Copy Skills LaTeX button functionality
    document.getElementById('copy-skills-latex-btn').addEventListener('click', function() {
        const skillsLatexCode = document.getElementById('latex-skills-section').textContent;
        navigator.clipboard.writeText(skillsLatexCode).then(function() {
            addMessage('Skills LaTeX code copied to clipboard!', 'system-message');
        }, function(err) {
            addMessage('Failed to copy skills LaTeX code.', 'error-message');
        });
    });

    // Re-optimize button functionality
    document.getElementById('reoptimize-btn').addEventListener('click', function() {
        const latexCode = latexCodeContainer.textContent;
        const jobDescription = document.getElementById('job-description').value;
        const feedback = document.getElementById('feedback-content').innerText;
        const apiKey = apiKeyInput.value;
        
        const formData = new FormData();
        formData.append('latex_code', latexCode);
        formData.append('job_description', jobDescription);
        formData.append('feedback', feedback);
        if (apiKey) formData.append('api_key', apiKey);
        
        addMessage('Re-optimizing resume...', 'system-message');
        document.getElementById('optimization-status').textContent = 'Re-optimization in progress...';
        
        fetch('/reoptimize_resume', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json().catch(error => {
                throw new Error('Invalid JSON response from server');
            });
        })
        .then(data => {
            if (data.error) {
                addMessage("Error: " + data.error, "error-message");
                document.getElementById('optimization-status').textContent = '';
                return;
            }
            addMessage("Resume re-optimized!", "system-message");
            latexCodeContainer.textContent = data.latex_code || 'No LaTeX code generated';
            feedbackContent.innerHTML = (data.feedback || 'No feedback available').replace(/\n/g, '<br>');
            scoreDisplay.textContent = (data.score || 0) + "/10";
            if (data.score >= 8) {
                scoreDisplay.className = 'badge badge-success';
            } else if (data.score >= 6) {
                scoreDisplay.className = 'badge badge-primary';
            } else {
                scoreDisplay.className = 'badge badge-info';
            }
            if (data.resume_id) {
                document.getElementById('download-link').href = '/download_latex/' + data.resume_id;
            }
            document.getElementById('optimization-status').textContent = data.optimization_message || '';
            
            // Highlight syntax if Prism is available
            if (typeof Prism !== 'undefined' && latexCodeContainer.textContent) {
                Prism.highlightElement(latexCodeContainer);
            }
        })
        .catch(error => {
            console.error('Error during re-optimization:', error);
            addMessage(`Error: ${error.message || 'Failed to re-optimize resume. Please try again.'}`, "error-message");
            document.getElementById('optimization-status').textContent = '';
        });
    });

    // Re-analyze skills button functionality
    document.getElementById('reanalyze-skills-btn').addEventListener('click', function() {
        const latexCode = latexCodeContainer.textContent;
        const jobDescription = document.getElementById('job-description').value;
        const apiKey = apiKeyInput.value;
        
        const formData = new FormData();
        formData.append('latex_code', latexCode);
        formData.append('job_description', jobDescription);
        if (apiKey) formData.append('api_key', apiKey);
        
        addMessage('Re-analyzing skills...', 'system-message');
        
        fetch('/reanalyze_skills', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json().catch(error => {
                throw new Error('Invalid JSON response from server');
            });
        })
        .then(data => {
            if (data.error) {
                addMessage("Error: " + data.error, "error-message");
                return;
            }
            
            // Update skills analysis
            if (data.skills_analysis) {
                updateSkillsLists(data.skills_analysis);
                addMessage("Skills re-analyzed successfully!", "system-message");
            } else {
                console.error('No skills analysis data received');
                addMessage("Skills analysis data not available.", "error-message");
            }
        })
        .catch(error => {
            console.error('Error during skills re-analysis:', error);
            addMessage(`Error: ${error.message || 'Failed to re-analyze skills. Please try again.'}`, "error-message");
        });
    });

    // Regenerate skills LaTeX button functionality
    document.getElementById('regenerate-skills-latex-btn').addEventListener('click', function() {
        const currentSkillsList = document.getElementById('current-skills-list');
        const missingSkillsList = document.getElementById('missing-skills-list');
        const recommendedSkillsList = document.getElementById('recommended-skills-list');
        
        // Get current skills data from the UI
        const getSkillsFromCategory = (container) => {
            const skills = [];
            container.querySelectorAll('.skills-category').forEach(category => {
                const categoryName = category.querySelector('h4').textContent;
                const categorySkills = Array.from(category.querySelectorAll('li')).map(li => li.textContent);
                if (categorySkills.length > 0) {
                    skills[categoryName] = categorySkills;
                }
            });
            return skills;
        };
        
        const skillsData = {
            current_skills_by_category: getSkillsFromCategory(currentSkillsList),
            recommended_skills_by_category: getSkillsFromCategory(recommendedSkillsList),
            missing_skills: Array.from(missingSkillsList.querySelectorAll('li')).map(li => li.textContent),
            current_certifications: [], // Add if you have certifications in the UI
            recommended_certifications: [] // Add if you have certifications in the UI
        };
        
        const apiKey = apiKeyInput.value;
        
        addMessage('Regenerating skills LaTeX section...', 'system-message');
        
        fetch('/regenerate_skills_latex', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(skillsData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json().catch(error => {
                throw new Error('Invalid JSON response from server');
            });
        })
        .then(data => {
            if (data.error) {
                addMessage("Error: " + data.error, "error-message");
                return;
            }
            
            // Update LaTeX skills section
            const latexSkillsSection = document.getElementById('latex-skills-section');
            latexSkillsSection.textContent = data.latex_skills_section;
            
            // Highlight syntax if Prism is available
            if (typeof Prism !== 'undefined') {
                Prism.highlightElement(latexSkillsSection);
            }
            
            addMessage("Skills LaTeX section regenerated successfully!", "system-message");
        })
        .catch(error => {
            console.error('Error during LaTeX skills regeneration:', error);
            addMessage(`Error: ${error.message || 'Failed to regenerate skills LaTeX. Please try again.'}`, "error-message");
        });
    });

    // Save Resume button functionality
    const saveResumeBtn = document.getElementById('save-main-resume-btn');
    if (saveResumeBtn) {
        saveResumeBtn.addEventListener('click', function() {
            const resumeContent = document.getElementById('resume-content').value;
            if (!resumeContent) {
                addMessage('Please enter your resume content before saving.', 'error-message');
                return;
            }
            fetch('/save_main_resume', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ resume_content: resumeContent })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addMessage('Resume saved successfully!', 'system-message');
                } else {
                    addMessage('Failed to save resume.', 'error-message');
                }
            })
            .catch(() => {
                addMessage('Error saving resume.', 'error-message');
            });
        });
    }

    // On page load, fetch saved resume content (if any)
    fetch('/get_main_resume')
        .then(response => response.json())
        .then(data => {
            if (data.resume_content) {
                document.getElementById('resume-content').value = data.resume_content;
            }
        });
}); 