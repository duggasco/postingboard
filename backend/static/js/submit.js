// Submit page functionality

(function() {
    // Elements
    const skillSelect = document.getElementById('skill-select');
    const skillInput = document.getElementById('skill-input');
    const addSkillBtn = document.getElementById('add-skill-btn');
    const selectedSkillsDiv = document.getElementById('selected-skills');
    const submitForm = document.getElementById('submit-form');
    const teamSelect = document.getElementById('team-select');
    const teamInput = document.getElementById('team-input');
    
    // State
    const selectedSkills = new Map(); // Map of skill id/name to skill object
    
    // Storage keys
    const STORAGE_KEYS = {
        team: 'submitForm_team'
    };
    
    // Initialize
    async function init() {
        console.log('Initializing submit form...');
        
        // Check if elements exist
        if (!skillSelect || !skillInput || !addSkillBtn || !selectedSkillsDiv || !submitForm) {
            console.error('Required elements not found:', {
                skillSelect: !!skillSelect,
                skillInput: !!skillInput,
                addSkillBtn: !!addSkillBtn,
                selectedSkillsDiv: !!selectedSkillsDiv,
                submitForm: !!submitForm
            });
            return;
        }
        
        await loadSkills();
        
        // Only load teams if user doesn't have an assigned team
        if (teamSelect) {
            await loadTeams();
        }
        
        // Load persisted data only if user doesn't have an assigned team
        if (!teamInput || !teamInput.hasAttribute('readonly')) {
            loadPersistedData();
        }
        
        // Event listeners
        addSkillBtn.addEventListener('click', handleAddSkill);
        skillSelect.addEventListener('change', function() {
            if (this.value) {
                skillInput.value = '';
            }
        });
        skillInput.addEventListener('input', function() {
            if (this.value) {
                skillSelect.value = '';
            }
        });
        
        // Handle form submission
        submitForm.addEventListener('submit', handleSubmit);
        
        // Allow Enter key to add skills
        skillInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                handleAddSkill();
            }
        });
        
        // Handle team selection mutual exclusivity (only if user doesn't have assigned team)
        if (teamSelect) {
            teamSelect.addEventListener('change', function() {
                if (this.value) {
                    teamInput.value = '';
                    localStorage.setItem(STORAGE_KEYS.team, this.value);
                }
            });
        }
        
        if (teamInput && !teamInput.hasAttribute('readonly')) {
            teamInput.addEventListener('input', function() {
                if (this.value) {
                    teamSelect.value = '';
                }
            });
            
            teamInput.addEventListener('change', function() {
                localStorage.setItem(STORAGE_KEYS.team, this.value);
            });
        }
        
        // Add clear saved data functionality
        const clearLink = document.getElementById('clear-saved-data');
        if (clearLink) {
            clearLink.addEventListener('click', function(e) {
                e.preventDefault();
                if (confirm('Clear saved team name?')) {
                    clearPersistedData();
                }
            });
        }
        
        console.log('Submit form initialized successfully');
    }
    
    // Load skills for dropdown
    async function loadSkills() {
        try {
            console.log('Loading skills...');
            const skills = await utils.fetchJson('/api/skills');
            console.log('Loaded skills:', skills.length);
            
            skillSelect.innerHTML = '<option value="">Select a skill...</option>';
            skills.forEach(skill => {
                const option = document.createElement('option');
                option.value = skill.id;
                option.textContent = skill.name;
                option.dataset.name = skill.name;
                skillSelect.appendChild(option);
            });
            
            console.log('Skills dropdown populated');
        } catch (error) {
            console.error('Error loading skills:', error);
            alert('Error loading skills. Please refresh the page and try again.');
        }
    }
    
    // Load teams for dropdown
    async function loadTeams() {
        try {
            console.log('Loading teams...');
            const teams = await utils.fetchJson('/api/teams');
            console.log('Loaded teams:', teams.length);
            
            teamSelect.innerHTML = '<option value="">Select a team...</option>';
            teams.forEach(team => {
                const option = document.createElement('option');
                option.value = team.name;  // Use name as value for consistency
                option.textContent = team.name;
                teamSelect.appendChild(option);
            });
            
            console.log('Teams dropdown populated');
        } catch (error) {
            console.error('Error loading teams:', error);
            // Don't alert for teams as it's not critical
        }
    }
    
    // Handle adding a skill
    function handleAddSkill() {
        console.log('Add skill clicked');
        let skillId, skillName;
        
        if (skillSelect.value) {
            // Selected from dropdown
            const selectedOption = skillSelect.options[skillSelect.selectedIndex];
            skillId = skillSelect.value;
            skillName = selectedOption.dataset.name;
            console.log('Adding skill from dropdown:', skillName, 'ID:', skillId);
        } else if (skillInput.value.trim()) {
            // Custom skill
            skillName = skillInput.value.trim();
            skillId = skillName; // Use name as ID for custom skills
            console.log('Adding custom skill:', skillName);
        } else {
            console.log('No skill selected');
            alert('Please select a skill from the dropdown or enter a custom skill');
            return; // Nothing selected
        }
        
        // Check if already added
        if (selectedSkills.has(skillId)) {
            alert('This skill has already been added');
            return;
        }
        
        // Add to selected skills
        selectedSkills.set(skillId, { id: skillId, name: skillName });
        console.log('Current selected skills:', Array.from(selectedSkills.values()));
        updateSelectedSkillsDisplay();
        
        // Clear inputs
        skillSelect.value = '';
        skillInput.value = '';
    }
    
    
    // Load persisted data from localStorage
    function loadPersistedData() {
        // Load team name
        const savedTeam = localStorage.getItem(STORAGE_KEYS.team);
        if (savedTeam) {
            // Check if it matches a team in the select
            if (teamSelect) {
                const matchingOption = Array.from(teamSelect.options).find(opt => opt.value === savedTeam);
                if (matchingOption) {
                    teamSelect.value = savedTeam;
                } else if (teamInput) {
                    teamInput.value = savedTeam;
                }
            } else if (teamInput) {
                teamInput.value = savedTeam;
            }
        }
    }
    
    // Clear persisted data from localStorage
    function clearPersistedData() {
        // Clear localStorage
        localStorage.removeItem(STORAGE_KEYS.team);
        
        // Clear form fields
        if (teamSelect) {
            teamSelect.value = '';
        }
        if (teamInput) {
            teamInput.value = '';
        }
        
        alert('Saved team has been cleared.');
    }
    
    // Update the display of selected skills
    function updateSelectedSkillsDisplay() {
        selectedSkillsDiv.innerHTML = '';
        
        selectedSkills.forEach((skill, skillId) => {
            const chip = document.createElement('div');
            chip.className = 'skill-chip';
            chip.innerHTML = `
                ${utils.escapeHtml(skill.name)}
                <button type="button" class="remove-btn" data-skill-id="${skillId}">×</button>
            `;
            selectedSkillsDiv.appendChild(chip);
        });
        
        // Add remove event listeners
        document.querySelectorAll('.skill-chip .remove-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const skillId = this.dataset.skillId;
                selectedSkills.delete(skillId);
                updateSelectedSkillsDisplay();
            });
        });
    }
    
    // Handle form submission
    function handleSubmit(e) {
        // Check if team is selected
        const teamValue = teamInput ? teamInput.value.trim() : '';
        if (!teamValue) {
            e.preventDefault();
            alert('Please select or enter a team');
            return;
        }
        
        // Check if skills are selected
        if (selectedSkills.size === 0) {
            e.preventDefault();
            alert('Please select at least one skill');
            return;
        }
        
        // Remove any existing hidden skill inputs
        document.querySelectorAll('input[name="skills[]"]').forEach(input => input.remove());
        
        // Add hidden inputs for each selected skill
        selectedSkills.forEach((skill, skillId) => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'skills[]';
            input.value = skillId;
            submitForm.appendChild(input);
        });
        
        // Form will submit normally
    }
    
    // Initialize on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();