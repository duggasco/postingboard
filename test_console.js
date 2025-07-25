// Console test script to verify SVG GANTT
// Run this in browser console on the idea detail page

console.log('=== SVG GANTT Test ===');

// Check if container exists
const container = document.getElementById('gantt-chart-container');
console.log('Container found:', !!container);

// Check if SVG exists
const svg = document.getElementById('gantt-svg');
console.log('SVG element found:', !!svg);

// If SVG exists, check its content
if (svg) {
    console.log('SVG dimensions:', svg.getAttribute('viewBox'));
    console.log('SVG groups:', svg.querySelectorAll('g').length);
    console.log('Phase elements:', svg.querySelectorAll('.phase').length);
    console.log('Phase bars:', svg.querySelectorAll('.phase-bar').length);
}

// Check if tooltip exists
const tooltip = document.getElementById('gantt-tooltip');
console.log('Tooltip found:', !!tooltip);

// Check if SVGGanttChart class is available
console.log('SVGGanttChart class available:', typeof SVGGanttChart !== 'undefined');

// Check for errors
if (window.ganttError) {
    console.error('GANTT Error:', window.ganttError);
}

// Try to manually render if not present
if (!svg && typeof SVGGanttChart !== 'undefined') {
    console.log('Attempting manual render...');
    try {
        renderGanttChart();
        console.log('Manual render complete');
    } catch (e) {
        console.error('Manual render failed:', e);
    }
}