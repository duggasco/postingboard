# SVG GANTT Implementation Plan

## Architecture Overview

### 1. Component Structure
```
SVGGanttChart
├── SVG Container (responsive)
├── Grid Layer (background lines, dates)
├── Phases Layer (interactive bars)
├── Markers Layer (today line, milestones)
├── Tooltip Layer (dynamic tooltips)
└── Controls Layer (zoom, export)
```

### 2. Data Flow
```
Idea Data (from backend)
    ↓
Phase Calculator (size, dates, progress)
    ↓
SVG Renderer (phases, grid, markers)
    ↓
Event Handlers (hover, click)
    ↓
UI Updates (tooltips, modals)
```

### 3. Core Functions

#### `renderSvgGanttChart()`
Main function to replace `renderGanttChart()`:
- Create SVG element with proper dimensions
- Calculate timeline based on idea size/dates
- Generate phase data with positions
- Render grid and date labels
- Draw phase bars with proper styling
- Add today marker
- Attach event handlers

#### `calculatePhaseData(ideaData)`
Transform idea data into phase rendering data:
- Start/end dates for each phase
- X/Y positions and dimensions
- Color based on progress/status
- Linked items counts
- Stage-specific data references

#### `createPhaseElement(phaseData)`
Create individual phase SVG group:
- Rectangle for phase bar
- Text labels (name, duration)
- Progress overlay
- Linked items badges
- Event data attributes

#### `showPhaseTooltip(event, phaseData)`
Display rich tooltip on hover:
- Phase name and status
- Start/end dates
- Actual vs planned duration
- Progress percentage
- Linked items summary
- Key stage data

#### `handlePhaseClick(event, phaseData)`
Handle phase interactions:
- Show stage-specific data modal
- Filter activity feed by phase
- Navigate to related items
- Open update status modal

### 4. Visual Design Matching Canvas

#### Colors
- Planning: #e9ecef (not started) → #28a745 (complete)
- Development: Progress-based coloring
- Testing: #ffc107 (in progress)
- Deployment: #4a90e2 (planned)
- Verification: #28a745 (complete)
- Blocked/On Hold: #dc3545 (red)

#### Layout
- Left margin: 100px for phase labels
- Row height: 25px
- Row spacing: 35px
- Start Y: 60px
- Font: 12px sans-serif

### 5. Enhanced Features

#### Tooltip Content Structure
```javascript
{
  phase: "Planning",
  status: "completed",
  dates: {
    start: "2025-01-01",
    end: "2025-01-05",
    duration: 5
  },
  progress: {
    percentage: 100,
    status: "Complete"
  },
  linkedItems: {
    comments: 3,
    links: 2,
    activities: 5
  },
  stageData: {
    requirements_doc: "URL",
    design_spec: "URL"
  },
  assignee: "John Developer"
}
```

#### Interactive Elements
1. **Hover Effects**
   - Slight opacity change (0.8)
   - Cursor change to pointer
   - Tooltip appears after 200ms

2. **Click Actions**
   - Single click: Show phase details
   - Double click: Open stage edit modal
   - Right click: Context menu (optional)

3. **Visual Feedback**
   - Highlight current phase
   - Dim other phases on hover
   - Smooth transitions (0.2s)

### 6. Implementation Steps

#### Step 1: Create SVG Structure
- Replace canvas element with SVG
- Set up viewBox for responsiveness
- Create layer groups

#### Step 2: Port Rendering Logic
- Convert Canvas drawing to SVG elements
- Maintain exact positioning/sizing
- Preserve color logic

#### Step 3: Add Interactivity
- Implement mouse event handlers
- Create tooltip system
- Add click handlers

#### Step 4: Enhance with Data
- Connect to stage-specific data
- Show linked items counts
- Display real dates/durations

#### Step 5: Polish and Test
- Ensure mobile compatibility
- Test with various data states
- Verify export functionality

### 7. Code Structure

```javascript
class SVGGanttChart {
  constructor(containerId, ideaData) {
    this.container = document.getElementById(containerId);
    this.ideaData = ideaData;
    this.phases = this.calculatePhases();
    this.tooltip = null;
  }
  
  render() {
    this.createSVG();
    this.drawGrid();
    this.drawPhases();
    this.drawMarkers();
    this.attachEventHandlers();
  }
  
  calculatePhases() {
    // Convert idea data to phase rendering data
  }
  
  createSVG() {
    // Create SVG element with proper setup
  }
  
  drawPhases() {
    // Render each phase as SVG group
  }
  
  showTooltip(phaseData, x, y) {
    // Display rich tooltip
  }
  
  handlePhaseClick(phaseData) {
    // Handle phase interactions
  }
  
  export() {
    // Export as PNG
  }
}
```

### 8. Integration Points

#### With Existing Code
- Replace `renderGanttChart()` calls with `renderSvgGanttChart()`
- Maintain sessionStorage for custom settings
- Keep export functionality working
- Preserve progress calculation logic

#### With SDLC Features
- Link to comments count
- Show external links count
- Display recent activities
- Connect to stage-specific modals

### 9. Testing Checklist

- [ ] Renders correctly for all idea sizes
- [ ] Tooltips show accurate data
- [ ] Click opens correct modals
- [ ] Export produces valid PNG
- [ ] Responsive on different screens
- [ ] Touch events work on mobile
- [ ] Keyboard navigation supported
- [ ] Progress overlays display correctly
- [ ] Today marker positioned accurately
- [ ] Custom settings applied properly

### 10. Performance Considerations

- Use CSS transforms for animations
- Debounce mouse move events
- Lazy load tooltip content
- Minimize DOM manipulations
- Cache calculated positions
- Use requestAnimationFrame for smooth updates