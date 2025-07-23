// Submit page functionality

(function() {
    // Elements
    const skillSelect = document.getElementById('skill-select');
    const skillInput = document.getElementById('skill-input');
    const addSkillBtn = document.getElementById('add-skill-btn');
    const selectedSkillsDiv = document.getElementById('selected-skills');
    const submitForm = document.getElementById('submit-form');
    
    // State
    const selectedSkills = new Map(); // Map of skill id/name to skill object
    
    // Initialize
    async function init() {
        await loadSkills();
        
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
    }
    
    // Load skills for dropdown
    async function loadSkills() {
        try {
            const skills = await utils.fetchJson('/api/skills');
            skillSelect.innerHTML = '<option value="">Select a skill...</option>';
            skills.forEach(skill => {
                const option = document.createElement('option');
                option.value = skill.id;
                option.textContent = skill.name;
                option.dataset.name = skill.name;
                skillSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading skills:', error);
        }
    }
    
    // Handle adding a skill
    function handleAddSkill() {
        let skillId, skillName;
        
        if (skillSelect.value) {
            // Selected from dropdown
            const selectedOption = skillSelect.options[skillSelect.selectedIndex];
            skillId = skillSelect.value;
            skillName = selectedOption.dataset.name;
        } else if (skillInput.value.trim()) {
            // Custom skill
            skillName = skillInput.value.trim();
            skillId = skillName; // Use name as ID for custom skills
        } else {
            return; // Nothing selected
        }
        
        // Check if already added
        if (selectedSkills.has(skillId)) {
            alert('This skill has already been added');
            return;
        }
        
        // Add to selected skills
        selectedSkills.set(skillId, { id: skillId, name: skillName });
        updateSelectedSkillsDisplay();
        
        // Clear inputs
        skillSelect.value = '';
        skillInput.value = '';
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
    init();
})();