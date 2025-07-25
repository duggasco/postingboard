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
                option.value = utils.getUuid(skill);
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
    
    // Render bounty information
    function renderBounty(idea) {
        if (!idea.bounty && !idea.bounty_details) return '';
        
        let bountyHtml = '<div class="bounty">';
        bountyHtml += '<span style="font-weight: 600;">Bounty: </span>';
        
        const parts = [];
        
        if (idea.bounty) {
            parts.push(utils.escapeHtml(idea.bounty));
        }
        
        if (idea.bounty_details && idea.bounty_details.is_monetary) {
            let monetaryPart = '';
            if (idea.bounty_details.is_expensed) {
                monetaryPart = `<span style="color: #28a745; font-weight: 600;">$${idea.bounty_details.amount.toFixed(2)}</span>`;
                if (idea.bounty_details.requires_approval) {
                    monetaryPart += ' <span style="color: #856404; font-size: 11px;">(pending approval)</span>';
                }
            } else {
                monetaryPart = '<span style="color: #28a745;">Monetary bounty available</span>';
            }
            parts.push(monetaryPart);
        }
        
        if (parts.length === 0) {
            bountyHtml += '<span style="color: #6c757d;">None specified</span>';
        } else {
            bountyHtml += parts.join(' + ');
        }
        
        bountyHtml += '</div>';
        return bountyHtml;
    }
    
    // Create idea card HTML
    function createIdeaCard(idea) {
        const statusClass = `status-${idea.status}`;
        const priorityClass = `priority-${idea.priority}`;
        const sizeClass = `size-${idea.size}`;
        
        const skillsHtml = idea.skills.map(skill => 
            `<span class="skill-tag">${utils.escapeHtml(skill.name)}</span>`
        ).join('');
        
        const claimInfo = idea.claims && idea.claims.length > 0 
            ? `<div class="claim-info">Claimed by ${utils.escapeHtml(idea.claims[0].name)}</div>`
            : '';
        
        // Add sub-status display for claimed ideas
        const subStatusHtml = idea.status === 'claimed' && idea.sub_status
            ? `<div class="sub-status-info" style="margin-top: 8px; font-size: 12px; color: #6c757d;">
                   <span class="sub-status-badge sub-status-${idea.sub_status}">
                       ${idea.sub_status.replace(/_/g, ' ').toUpperCase()}
                   </span>
                   ${idea.progress_percentage !== undefined ? ` • ${idea.progress_percentage}% complete` : ''}
               </div>`
            : '';
        
        // Create full description for tooltip
        const fullDescription = utils.escapeHtml(idea.description);
        const truncatedDescription = idea.description.length > 150 
            ? utils.escapeHtml(idea.description.substring(0, 150)) + '...'
            : fullDescription;
        
        return `
            <div class="idea-card" onclick="window.location.href='/idea/${utils.getUuid(idea)}'">
                <div class="idea-header">
                    <h3 class="idea-title">${utils.escapeHtml(idea.title)}</h3>
                    <span class="status-badge ${statusClass}">${idea.status.toUpperCase()}</span>
                </div>
                
                <div class="idea-meta">
                    <div class="priority-badge ${priorityClass}">Priority: ${idea.priority}</div>
                    <div class="size-badge ${sizeClass}">Size: ${idea.size.replace('_', ' ')}</div>
                </div>
                
                ${skillsHtml ? `<div class="skills-tags">${skillsHtml}</div>` : ''}
                
                <p class="idea-description" ${idea.description.length > 150 ? `title="${fullDescription}"` : ''}>
                    ${truncatedDescription}
                </p>
                
                ${renderBounty(idea)}
                
                ${subStatusHtml}
                ${claimInfo}
                
                <div class="idea-footer">
                    <div>Submitted${idea.submitter_name ? ' by ' + utils.escapeHtml(idea.submitter_name) : ''}: ${utils.formatDate(idea.date_submitted)}</div>
                    <div>Team: ${utils.escapeHtml(idea.benefactor_team)}</div>
                    ${idea.needed_by ? `<div>Needed by: ${utils.formatDate(idea.needed_by)}</div>` : ''}
                </div>
                
                <a href="/idea/${utils.getUuid(idea)}" class="view-details-link" onclick="event.stopPropagation()">View Details →</a>
            </div>
        `;
    }
    
    // Initialize on page load
    init();
})();