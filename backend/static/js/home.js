// Home page functionality

(function() {
    // Elements
    const skillFilter = document.getElementById('skill-filter');
    const priorityFilter = document.getElementById('priority-filter');
    const statusFilter = document.getElementById('status-filter');
    const sortBy = document.getElementById('sort-by');
    const ideasContainer = document.getElementById('ideas-container');
    
    // State
    let currentIdeas = [];
    
    // Initialize
    async function init() {
        await loadSkills();
        await loadIdeas();
        
        // Add event listeners
        skillFilter.addEventListener('change', loadIdeas);
        priorityFilter.addEventListener('change', loadIdeas);
        statusFilter.addEventListener('change', loadIdeas);
        sortBy.addEventListener('change', loadIdeas);
        
        // Auto-refresh every 30 seconds
        setInterval(loadIdeas, 30000);
    }
    
    // Load skills for filter
    async function loadSkills() {
        try {
            const skills = await utils.fetchJson('/api/skills');
            skillFilter.innerHTML = '<option value="">All Skills</option>';
            skills.forEach(skill => {
                const option = document.createElement('option');
                option.value = skill.id;
                option.textContent = skill.name;
                skillFilter.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading skills:', error);
        }
    }
    
    // Load and display ideas
    async function loadIdeas() {
        try {
            const params = new URLSearchParams({
                skill: skillFilter.value,
                priority: priorityFilter.value,
                status: statusFilter.value,
                sort: sortBy.value
            });
            
            ideasContainer.innerHTML = '<div class="loading">Loading ideas...</div>';
            
            const ideas = await utils.fetchJson(`/api/ideas?${params}`);
            currentIdeas = ideas;
            
            if (ideas.length === 0) {
                ideasContainer.innerHTML = `
                    <div class="empty-state">
                        <h3>No ideas found</h3>
                        <p>Try adjusting your filters or <a href="/submit">submit a new idea</a>.</p>
                    </div>
                `;
                return;
            }
            
            ideasContainer.innerHTML = ideas.map(idea => createIdeaCard(idea)).join('');
        } catch (error) {
            console.error('Error loading ideas:', error);
            ideasContainer.innerHTML = '<div class="error">Error loading ideas. Please try again.</div>';
        }
    }
    
    // Create idea card HTML
    function createIdeaCard(idea) {
        const statusClass = `status-${idea.status}`;
        const priorityClass = `priority-${idea.priority}`;
        
        const skillsHtml = idea.skills.map(skill => 
            `<span class="skill-tag">${utils.escapeHtml(skill.name)}</span>`
        ).join('');
        
        const claimInfo = idea.claims && idea.claims.length > 0 
            ? `<div class="claim-info">Claimed by ${utils.escapeHtml(idea.claims[0].name)}</div>`
            : '';
        
        return `
            <div class="idea-card" onclick="window.location.href='/idea/${idea.id}'">
                <div class="idea-header">
                    <h3 class="idea-title">${utils.escapeHtml(idea.title)}</h3>
                    <span class="status-badge ${statusClass}">${idea.status.toUpperCase()}</span>
                </div>
                
                <div class="idea-meta">
                    <span class="priority-badge ${priorityClass}">Priority: ${idea.priority}</span>
                    <span>Size: ${idea.size.replace('_', ' ')}</span>
                    <span>Team: ${utils.escapeHtml(idea.benefactor_team)}</span>
                </div>
                
                ${skillsHtml ? `<div class="skills-tags">${skillsHtml}</div>` : ''}
                
                <p class="idea-description">
                    ${utils.escapeHtml(idea.description.substring(0, 150))}${idea.description.length > 150 ? '...' : ''}
                </p>
                
                ${idea.reward ? `<div class="reward">Reward: ${utils.escapeHtml(idea.reward)}</div>` : ''}
                
                <div class="idea-footer">
                    <span>Submitted${idea.submitter_name ? ' by ' + utils.escapeHtml(idea.submitter_name) : ''}: ${utils.formatDate(idea.date_submitted)}</span>
                    ${idea.needed_by ? `<span>Needed by: ${utils.formatDate(idea.needed_by)}</span>` : ''}
                </div>
                
                ${claimInfo}
                
                <a href="/idea/${idea.id}" class="view-details-link" onclick="event.stopPropagation()">View Details →</a>
            </div>
        `;
    }
    
    // Initialize on page load
    init();
})();