// SVG GANTT Chart Implementation
class SVGGanttChart {
    constructor(containerId, ideaData) {
        this.container = document.getElementById(containerId);
        this.ideaData = ideaData;
        this.svg = null;
        this.tooltip = document.getElementById('gantt-tooltip');
        this.phaseDataMap = new Map();
    }

    render() {
        console.log('SVGGanttChart render called', this.ideaData);
        
        // Clear existing content
        this.container.innerHTML = '';
        
        // Create SVG element
        this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        this.svg.setAttribute('id', 'gantt-svg');
        this.svg.setAttribute('style', 'width: 100%; height: 250px;');
        this.svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
        
        // Get dimensions
        const rect = this.container.getBoundingClientRect();
        const width = rect.width - 40; // Account for padding
        const height = 250;
        
        // Set viewBox
        this.svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
        
        // Calculate timeline
        const timeline = this.calculateTimeline();
        
        // Create layer groups
        const layers = this.createLayers();
        
        // Draw components
        this.drawGrid(layers.grid, timeline, width, height);
        this.drawPhases(layers.phases, timeline, width, height);
        this.drawMarkers(layers.markers, timeline, width, height);
        
        // Append layers to SVG
        this.svg.appendChild(layers.grid);
        this.svg.appendChild(layers.phases);
        this.svg.appendChild(layers.markers);
        
        // Append SVG to container
        this.container.appendChild(this.svg);
        
        // Create tooltip container if it doesn't exist
        if (!this.tooltip) {
            this.tooltip = document.createElement('div');
            this.tooltip.id = 'gantt-tooltip';
            this.tooltip.style.cssText = 'position: absolute; display: none; background: white; border: 1px solid #dee2e6; border-radius: 4px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); font-size: 12px; pointer-events: none; z-index: 1000;';
            document.body.appendChild(this.tooltip); // Append to body instead of container
        }
    }

    createLayers() {
        return {
            grid: this.createGroup('gantt-grid'),
            phases: this.createGroup('gantt-phases'),
            markers: this.createGroup('gantt-markers')
        };
    }

    createGroup(className) {
        const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        group.setAttribute('class', className);
        return group;
    }

    calculateTimeline() {
        const sizeDurations = {
            'small': 5,
            'medium': 10,
            'large': 20,
            'extra_large': 30
        };
        
        const estimatedDays = sizeDurations[this.ideaData.size] || 10;
        const startDate = this.ideaData.claimDate || new Date();
        const endDate = this.ideaData.neededBy || new Date(startDate.getTime() + (estimatedDays * 24 * 60 * 60 * 1000));
        
        const phases = [
            { name: 'Planning', startOffset: 0, duration: 0.15, status: 'planning' },
            { name: 'Development', startOffset: 0.10, duration: 0.45, status: 'in_development' },
            { name: 'Testing', startOffset: 0.40, duration: 0.30, status: 'testing' },
            { name: 'Deployment', startOffset: 0.65, duration: 0.15, status: 'awaiting_deployment' },
            { name: 'Verification', startOffset: 0.75, duration: 0.15, status: 'deployed,verified' }
        ];
        
        return {
            startDate,
            endDate,
            phases,
            totalDuration: endDate - startDate
        };
    }

    drawGrid(gridGroup, timeline, width, height) {
        // Header background
        const headerBg = this.createRect(0, 0, width, 40, '#f8f9fa');
        gridGroup.appendChild(headerBg);
        
        // Calculate pixels per day
        const pixelsPerDay = (width - 150) / (timeline.totalDuration / (1000 * 60 * 60 * 24));
        
        // Draw date labels
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        let currentDate = new Date(timeline.startDate);
        let x = 100;
        
        while (currentDate <= timeline.endDate) {
            const monthLabel = months[currentDate.getMonth()] + ' ' + currentDate.getDate();
            const text = this.createText(x, 25, monthLabel, {
                fill: '#495057',
                fontSize: '12px'
            });
            gridGroup.appendChild(text);
            
            x += pixelsPerDay * 7;
            currentDate.setDate(currentDate.getDate() + 7);
        }
        
        // Draw vertical grid lines
        let gridDate = new Date(timeline.startDate);
        while (gridDate <= timeline.endDate) {
            const gridX = 100 + ((gridDate - timeline.startDate) / (1000 * 60 * 60 * 24)) * pixelsPerDay;
            const line = this.createLine(gridX, 40, gridX, 235, {
                stroke: '#f0f0f0',
                strokeWidth: 1
            });
            gridGroup.appendChild(line);
            
            gridDate.setDate(gridDate.getDate() + 7);
        }
    }

    drawPhases(phasesGroup, timeline, width, height) {
        const barHeight = 25;
        const rowSpacing = 35;
        const startY = 60;
        const pixelsPerDay = (width - 150) / (timeline.totalDuration / (1000 * 60 * 60 * 24));
        
        timeline.phases.forEach((phase, index) => {
            const phaseGroup = this.createGroup(`phase phase-${index}`);
            phaseGroup.setAttribute('data-phase', phase.status);
            phaseGroup.style.cursor = 'pointer';
            
            // Calculate positions
            const phaseStart = new Date(timeline.startDate.getTime() + (phase.startOffset * timeline.totalDuration));
            const phaseDuration = phase.duration * timeline.totalDuration;
            const phaseEnd = new Date(phaseStart.getTime() + phaseDuration);
            
            const x1 = 100 + (phase.startOffset * timeline.totalDuration / (1000 * 60 * 60 * 24)) * pixelsPerDay;
            const x2 = x1 + (phaseDuration / (1000 * 60 * 60 * 24)) * pixelsPerDay;
            const barY = startY + (index * rowSpacing);
            
            // Draw phase label
            const label = this.createText(90, barY + barHeight/2 + 4, phase.name, {
                textAnchor: 'end',
                fill: '#212529',
                fontSize: '12px'
            });
            phaseGroup.appendChild(label);
            
            // Determine color
            const color = this.getPhaseColor(phase, timeline);
            
            // Draw phase bar
            const bar = this.createRect(x1, barY, x2 - x1, barHeight, color, {
                stroke: '#dee2e6',
                strokeWidth: 1,
                rx: 3,
                ry: 3
            });
            bar.setAttribute('class', 'phase-bar');
            phaseGroup.appendChild(bar);
            
            // Draw duration text
            const durationDays = Math.round(phaseDuration / (1000 * 60 * 60 * 24));
            const durationText = this.createText(x2 + 10, barY + barHeight/2 + 4, 
                `${durationDays} days (${Math.round(phase.duration * 100)}%)`, {
                fill: '#6c757d',
                fontSize: '11px'
            });
            phaseGroup.appendChild(durationText);
            
            // Draw progress overlay if needed
            this.drawPhaseProgress(phaseGroup, phase, timeline, x1, barY, x2 - x1, barHeight);
            
            // Store phase data for tooltips
            const phaseData = {
                name: phase.name,
                status: phase.status,
                startDate: phaseStart.toLocaleDateString(),
                endDate: phaseEnd.toLocaleDateString(),
                duration: durationDays,
                progress: this.calculatePhaseProgress(phase, timeline),
                x1: x1,
                x2: x2,
                y: barY
            };
            this.phaseDataMap.set(phaseGroup, phaseData);
            
            // Add event listeners
            this.addPhaseEventListeners(phaseGroup, phaseData);
            
            phasesGroup.appendChild(phaseGroup);
        });
        
        // Draw dependency lines
        this.drawDependencyLines(phasesGroup, timeline, width, pixelsPerDay, startY, rowSpacing);
    }

    drawDependencyLines(phasesGroup, timeline, width, pixelsPerDay, startY, rowSpacing) {
        const depGroup = this.createGroup('dependencies');
        
        const dependencies = [
            { from: 0.15, to: 0.10, fromRow: 0, toRow: 1 },
            { from: 0.55, to: 0.40, fromRow: 1, toRow: 2 },
            { from: 0.70, to: 0.65, fromRow: 2, toRow: 3 },
            { from: 0.80, to: 0.75, fromRow: 3, toRow: 4 }
        ];
        
        dependencies.forEach(dep => {
            const x1 = 100 + (dep.from * timeline.totalDuration / (1000 * 60 * 60 * 24)) * pixelsPerDay;
            const y1 = startY + (dep.fromRow * rowSpacing) + 12;
            const x2 = 100 + (dep.to * timeline.totalDuration / (1000 * 60 * 60 * 24)) * pixelsPerDay;
            const y2 = startY + (dep.toRow * rowSpacing) + 12;
            
            const line = this.createLine(x1, y1, x2, y2, {
                stroke: '#999',
                strokeWidth: 1,
                strokeDasharray: '2,2'
            });
            depGroup.appendChild(line);
        });
        
        phasesGroup.appendChild(depGroup);
    }

    drawMarkers(markersGroup, timeline, width, height) {
        const pixelsPerDay = (width - 150) / (timeline.totalDuration / (1000 * 60 * 60 * 24));
        
        // Draw progress indicator
        if (this.ideaData.progress > 0 && this.ideaData.progress < 100) {
            const totalDays = timeline.totalDuration / (1000 * 60 * 60 * 24);
            const progressDays = (this.ideaData.progress / 100) * totalDays;
            const progressX = 100 + (progressDays * pixelsPerDay);
            
            const progressLine = this.createLine(progressX, 50, progressX, 225, {
                stroke: '#007bff',
                strokeWidth: 2
            });
            markersGroup.appendChild(progressLine);
            
            const progressText = this.createText(progressX - 30, 45, 
                `Progress: ${this.ideaData.progress}%`, {
                fill: '#007bff',
                fontSize: '10px'
            });
            markersGroup.appendChild(progressText);
        }
        
        // Draw today marker
        const today = new Date();
        if (today >= timeline.startDate && today <= timeline.endDate) {
            const daysFromStart = (today - timeline.startDate) / (1000 * 60 * 60 * 24);
            const todayX = 100 + (daysFromStart * pixelsPerDay);
            
            const todayLine = this.createLine(todayX, 40, todayX, 235, {
                stroke: '#dc3545',
                strokeWidth: 1,
                strokeDasharray: '5,5'
            });
            markersGroup.appendChild(todayLine);
            
            const todayText = this.createText(todayX - 15, 250, 'Today', {
                fill: '#dc3545',
                fontSize: '11px'
            });
            markersGroup.appendChild(todayText);
        }
    }

    getPhaseColor(phase, timeline) {
        const phaseStartProgress = phase.startOffset * 100;
        const phaseEndProgress = phaseStartProgress + (phase.duration * 100);
        
        if (this.ideaData.progress >= phaseEndProgress) {
            return '#28a745'; // Completed
        } else if (this.ideaData.progress > phaseStartProgress && this.ideaData.progress < phaseEndProgress) {
            return '#ffc107'; // In progress
        }
        
        // Override if blocked or on hold
        if (this.ideaData.subStatus === 'blocked' || this.ideaData.subStatus === 'on_hold') {
            if (this.ideaData.progress > phaseStartProgress && this.ideaData.progress <= phaseEndProgress) {
                return '#dc3545'; // Blocked/on hold
            }
        }
        
        return '#e9ecef'; // Not started
    }

    drawPhaseProgress(phaseGroup, phase, timeline, x, y, width, height) {
        const phaseStartProgress = phase.startOffset * 100;
        const phaseEndProgress = phaseStartProgress + (phase.duration * 100);
        
        if (this.ideaData.progress > phaseStartProgress && this.ideaData.progress < phaseEndProgress) {
            const phaseProgress = (this.ideaData.progress - phaseStartProgress) / (phase.duration * 100);
            if (phaseProgress > 0 && phaseProgress <= 1) {
                const fillColor = (this.ideaData.subStatus === 'blocked' || this.ideaData.subStatus === 'on_hold') 
                    ? 'rgba(220, 53, 69, 0.3)' 
                    : 'rgba(40, 167, 69, 0.3)';
                
                const progressRect = this.createRect(x, y, width * phaseProgress, height, fillColor, {
                    rx: 3,
                    ry: 3,
                    pointerEvents: 'none'
                });
                phaseGroup.appendChild(progressRect);
            }
        }
    }

    calculatePhaseProgress(phase, timeline) {
        const phaseStartProgress = phase.startOffset * 100;
        const phaseEndProgress = phaseStartProgress + (phase.duration * 100);
        
        if (this.ideaData.progress >= phaseEndProgress) return 100;
        if (this.ideaData.progress <= phaseStartProgress) return 0;
        
        return Math.round(((this.ideaData.progress - phaseStartProgress) / (phase.duration * 100)) * 100);
    }

    addPhaseEventListeners(phaseGroup, phaseData) {
        phaseGroup.addEventListener('mouseenter', (e) => {
            this.showTooltip(e, phaseData);
        });
        
        phaseGroup.addEventListener('mouseleave', () => {
            this.hideTooltip();
        });
        
        phaseGroup.addEventListener('click', () => {
            this.handlePhaseClick(phaseData);
        });
    }

    showTooltip(event, phaseData) {
        const containerRect = this.container.getBoundingClientRect();
        
        let tooltipContent = `
            <div style="font-weight: bold; margin-bottom: 5px;">${phaseData.name}</div>
            <div style="margin-bottom: 3px;">Status: ${this.formatStatus(phaseData.status)}</div>
            <div style="margin-bottom: 3px;">Start: ${phaseData.startDate}</div>
            <div style="margin-bottom: 3px;">End: ${phaseData.endDate}</div>
            <div style="margin-bottom: 3px;">Duration: ${phaseData.duration} days</div>
            <div style="margin-bottom: 3px;">Progress: ${phaseData.progress}%</div>
        `;
        
        // Add linked items if available
        if (this.ideaData.linkedItems) {
            const { comments, links } = this.ideaData.linkedItems;
            if (comments > 0 || links > 0) {
                tooltipContent += '<div style="margin-top: 5px; padding-top: 5px; border-top: 1px solid #dee2e6;">';
                if (comments > 0) {
                    tooltipContent += `<div style="margin-bottom: 2px;">💬 ${comments} comment${comments > 1 ? 's' : ''}</div>`;
                }
                if (links > 0) {
                    tooltipContent += `<div style="margin-bottom: 2px;">🔗 ${links} link${links > 1 ? 's' : ''}</div>`;
                }
                tooltipContent += '</div>';
            }
        }
        
        this.tooltip.innerHTML = tooltipContent;
        
        // Position tooltip
        const mouseX = event.clientX;
        const mouseY = event.clientY;
        
        let left = mouseX - containerRect.left + 10;
        let top = mouseY - containerRect.top + 10;
        
        // Adjust if tooltip would go off screen
        if (left + 200 > containerRect.width) {
            left = mouseX - containerRect.left - 210;
        }
        if (top + 150 > containerRect.height) {
            top = mouseY - containerRect.top - 160;
        }
        
        this.tooltip.style.left = left + 'px';
        this.tooltip.style.top = top + 'px';
        this.tooltip.style.display = 'block';
    }

    hideTooltip() {
        if (this.tooltip) {
            this.tooltip.style.display = 'none';
        }
    }

    handlePhaseClick(phaseData) {
        console.log('Phase clicked:', phaseData);
        // This will be implemented to show stage-specific data
        if (window.showUpdateSubStatusModal) {
            window.showUpdateSubStatusModal();
        }
    }

    formatStatus(status) {
        const statusMap = {
            'planning': 'Planning',
            'in_development': 'In Development',
            'testing': 'Testing',
            'awaiting_deployment': 'Awaiting Deployment',
            'deployed': 'Deployed',
            'verified': 'Verified',
            'deployed,verified': 'Deployed/Verified'
        };
        return statusMap[status] || status;
    }

    // Helper methods for creating SVG elements
    createRect(x, y, width, height, fill, attrs = {}) {
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', x);
        rect.setAttribute('y', y);
        rect.setAttribute('width', width);
        rect.setAttribute('height', height);
        rect.setAttribute('fill', fill);
        
        Object.entries(attrs).forEach(([key, value]) => {
            rect.setAttribute(this.camelToKebab(key), value);
        });
        
        return rect;
    }

    createLine(x1, y1, x2, y2, attrs = {}) {
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', x1);
        line.setAttribute('y1', y1);
        line.setAttribute('x2', x2);
        line.setAttribute('y2', y2);
        
        Object.entries(attrs).forEach(([key, value]) => {
            line.setAttribute(this.camelToKebab(key), value);
        });
        
        return line;
    }

    createText(x, y, text, attrs = {}) {
        const textEl = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        textEl.setAttribute('x', x);
        textEl.setAttribute('y', y);
        textEl.textContent = text;
        textEl.setAttribute('font-family', 'sans-serif');
        
        Object.entries(attrs).forEach(([key, value]) => {
            textEl.setAttribute(this.camelToKebab(key), value);
        });
        
        return textEl;
    }

    camelToKebab(str) {
        return str.replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').toLowerCase();
    }

    // Export as PNG
    exportAsPNG() {
        const svgData = new XMLSerializer().serializeToString(this.svg);
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        canvas.width = this.svg.viewBox.baseVal.width;
        canvas.height = this.svg.viewBox.baseVal.height;
        
        img.onload = function() {
            ctx.fillStyle = 'white';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0);
            
            const link = document.createElement('a');
            link.download = `gantt-chart-idea-${new Date().toISOString().split('T')[0]}.png`;
            link.href = canvas.toDataURL();
            link.click();
        };
        
        const svgBlob = new Blob([svgData], {type: 'image/svg+xml;charset=utf-8'});
        const url = URL.createObjectURL(svgBlob);
        img.src = url;
    }
}

// Make it globally available
window.SVGGanttChart = SVGGanttChart;