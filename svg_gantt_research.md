# SVG GANTT Research

## SVG Interactive Patterns

### 1. SVG Structure for Interactive Elements
```svg
<svg width="800" height="300" xmlns="http://www.w3.org/2000/svg">
  <!-- Timeline grid -->
  <g class="gantt-grid">
    <!-- Grid lines -->
  </g>
  
  <!-- Phase rows -->
  <g class="gantt-phases">
    <g class="phase" data-phase="planning" data-status="completed">
      <rect class="phase-bar" x="100" y="60" width="120" height="25" fill="#28a745"/>
      <text class="phase-label" x="90" y="77" text-anchor="end">Planning</text>
      <text class="phase-duration" x="225" y="77">3 days</text>
    </g>
  </g>
  
  <!-- Today marker -->
  <line class="today-marker" x1="400" y1="40" x2="400" y2="250"/>
  
  <!-- Invisible overlay for tooltips -->
  <g class="tooltip-layer">
    <!-- Tooltip will be inserted here dynamically -->
  </g>
</svg>
```

### 2. Mouse Event Handling
```javascript
// Add event listeners to phase bars
document.querySelectorAll('.phase').forEach(phase => {
  phase.addEventListener('mouseenter', showTooltip);
  phase.addEventListener('mouseleave', hideTooltip);
  phase.addEventListener('click', showPhaseDetails);
});

// Mouse position tracking
svg.addEventListener('mousemove', (e) => {
  const rect = svg.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  updateTooltipPosition(x, y);
});
```

### 3. Tooltip Implementation
```javascript
function createTooltip(phaseData) {
  const tooltip = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  tooltip.setAttribute('class', 'gantt-tooltip');
  
  // Background
  const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
  bg.setAttribute('class', 'tooltip-bg');
  bg.setAttribute('rx', '4');
  bg.setAttribute('ry', '4');
  
  // Text content
  const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  text.setAttribute('class', 'tooltip-text');
  
  // Multiple lines
  const lines = [
    `Phase: ${phaseData.name}`,
    `Status: ${phaseData.status}`,
    `Start: ${phaseData.startDate}`,
    `End: ${phaseData.endDate}`,
    `Duration: ${phaseData.duration} days`,
    `Progress: ${phaseData.progress}%`
  ];
  
  lines.forEach((line, i) => {
    const tspan = document.createElementNS('http://www.w3.org/2000/svg', 'tspan');
    tspan.textContent = line;
    tspan.setAttribute('x', '10');
    tspan.setAttribute('dy', i === 0 ? '20' : '18');
    text.appendChild(tspan);
  });
  
  tooltip.appendChild(bg);
  tooltip.appendChild(text);
  
  return tooltip;
}
```

### 4. Data Structure for Phase Information
```javascript
const phaseData = {
  planning: {
    name: 'Planning',
    status: 'completed',
    startDate: '2025-01-01',
    endDate: '2025-01-05',
    duration: 5,
    progress: 100,
    stageData: {
      requirements_doc: 'https://docs.example.com/req-123',
      design_spec: 'https://docs.example.com/design-123'
    },
    linkedItems: {
      comments: 3,
      links: 2,
      activities: 5
    }
  }
};
```

### 5. CSS for SVG Styling
```css
.phase-bar {
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.phase-bar:hover {
  opacity: 0.8;
}

.gantt-tooltip {
  pointer-events: none;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}

.tooltip-bg {
  fill: white;
  stroke: #dee2e6;
  stroke-width: 1;
}

.tooltip-text {
  font-size: 12px;
  fill: #212529;
}
```

### 6. Advanced Features

#### Click Interactions
```javascript
function showPhaseDetails(event) {
  const phase = event.currentTarget;
  const phaseName = phase.dataset.phase;
  const phaseInfo = phaseData[phaseName];
  
  // Show modal with stage-specific data
  showStageDataModal(phaseInfo);
  
  // Or filter activity feed
  filterActivityByPhase(phaseName);
}
```

#### Linked Items Display
```javascript
function addLinkedItemsBadges(phase, linkedItems) {
  if (linkedItems.comments > 0) {
    const badge = createBadge('comments', linkedItems.comments);
    phase.appendChild(badge);
  }
  
  if (linkedItems.links > 0) {
    const badge = createBadge('links', linkedItems.links);
    phase.appendChild(badge);
  }
}
```

#### Progress Overlay
```javascript
function drawProgressOverlay(phase, progress) {
  const rect = phase.querySelector('.phase-bar');
  const width = parseFloat(rect.getAttribute('width'));
  const x = parseFloat(rect.getAttribute('x'));
  const y = parseFloat(rect.getAttribute('y'));
  const height = parseFloat(rect.getAttribute('height'));
  
  const overlay = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
  overlay.setAttribute('class', 'progress-overlay');
  overlay.setAttribute('x', x);
  overlay.setAttribute('y', y);
  overlay.setAttribute('width', width * (progress / 100));
  overlay.setAttribute('height', height);
  overlay.setAttribute('fill', 'rgba(40, 167, 69, 0.3)');
  
  phase.appendChild(overlay);
}
```

### 7. Touch Support
```javascript
// Add touch events for mobile
phase.addEventListener('touchstart', handleTouchStart);
phase.addEventListener('touchend', handleTouchEnd);

let touchTimer;
function handleTouchStart(e) {
  touchTimer = setTimeout(() => {
    showTooltip(e);
  }, 500); // Show after 500ms hold
}

function handleTouchEnd(e) {
  clearTimeout(touchTimer);
  hideTooltip();
}
```

### 8. Accessibility
```svg
<g class="phase" role="button" tabindex="0" aria-label="Planning phase: completed">
  <title>Planning phase from Jan 1 to Jan 5, completed</title>
  <desc>This phase includes requirements documentation and design specification</desc>
  <rect class="phase-bar" />
</g>
```

### 9. Dynamic Sizing
```javascript
function calculatePhasePositions(phases, containerWidth) {
  const startX = 100;
  const availableWidth = containerWidth - startX - 50;
  const pixelsPerDay = availableWidth / totalDays;
  
  return phases.map((phase, index) => {
    const x = startX + (phase.startOffset * totalDays * pixelsPerDay);
    const width = phase.duration * totalDays * pixelsPerDay;
    const y = 60 + (index * 35);
    
    return { x, y, width, height: 25 };
  });
}
```

### 10. Export Functionality
```javascript
function exportSvgToPng() {
  const svg = document.getElementById('gantt-svg');
  const svgData = new XMLSerializer().serializeToString(svg);
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  
  const img = new Image();
  img.onload = function() {
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);
    
    canvas.toBlob(function(blob) {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'gantt-chart.png';
      a.click();
    });
  };
  
  img.src = 'data:image/svg+xml;base64,' + btoa(svgData);
}
```

## Key Advantages of SVG over Canvas

1. **Native Event Handling**: Each element can have its own event listeners
2. **DOM Manipulation**: Easy to update individual elements
3. **CSS Styling**: Full CSS support including animations
4. **Accessibility**: Better screen reader support
5. **Scalability**: Vector graphics scale perfectly
6. **Debugging**: Elements visible in DOM inspector

## Implementation Plan

1. Create SVG container with proper viewport
2. Generate phase bars as SVG rectangles
3. Add text labels and duration info
4. Implement hover tooltips
5. Add click handlers for phase details
6. Show linked items counts
7. Implement progress overlays
8. Add today marker
9. Enable export functionality
10. Ensure mobile compatibility