// GANTT Chart Rendering
function renderGanttChart() {
    console.log('renderGanttChart called');
    const container = document.getElementById('gantt-chart-container');
    if (!container) {
        console.error('GANTT container not found');
        return;
    }
    
    // Get idea data with linked items count
    const ideaData = {
        id: {{ idea.id }},
        size: '{{ idea.size.value }}',
        status: '{{ idea.status.value }}',
        subStatus: '{{ idea.sub_status.value if idea.sub_status else "" }}',
        progress: {{ idea.progress_percentage or 0 }},
        dateSubmitted: new Date('{{ idea.date_submitted.isoformat() }}'),
        neededBy: {% if idea.needed_by %}new Date('{{ idea.needed_by.isoformat() }}'){% else %}null{% endif %},
        claimDate: {% if idea.claims %}new Date('{{ idea.claims[0].claim_date.isoformat() }}'){% else %}null{% endif %},
        linkedItems: {
            comments: {{ idea.comments | length if idea.comments else 0 }},
            links: {{ idea.external_links | length if idea.external_links else 0 }},
            activities: {{ idea.activities | length if idea.activities else 0 }}
        }
    };
    
    // Check for custom settings
    const customSettings = sessionStorage.getItem(`gantt-settings-{{ idea.id }}`);
    if (customSettings) {
        const settings = JSON.parse(customSettings);
        ideaData.customSettings = settings;
    }
    
    // Create and render the SVG GANTT chart
    try {
        const ganttChart = new SVGGanttChart('gantt-chart-container', ideaData);
        ganttChart.render();
        
        // Store instance for export functionality
        window.currentGanttChart = ganttChart;
    } catch (error) {
        console.error('Error rendering SVG GANTT chart:', error);
        container.innerHTML = '<p style="color: #dc3545;">Error loading GANTT chart</p>';
    }
}