#!/usr/bin/env python3
"""Clean up Canvas code from idea_detail.html"""

# Read the file
with open('/root/postingboard/backend/templates/idea_detail.html', 'r') as f:
    content = f.read()

# Find the end of renderGanttChart function
render_end = content.find('}\n    \n    let currentDate')
if render_end == -1:
    render_end = content.find('}\n    \n    // Draw month labels')
    if render_end == -1:
        print("Could not find end of renderGanttChart")
        exit(1)

# Find the start of Export function
export_start = content.find('// Export GANTT chart as PNG')
if export_start == -1:
    print("Could not find export function")
    exit(1)

# Extract parts
before = content[:render_end + 1]  # Include the closing brace
after = content[export_start:]

# Write back
new_content = before + '\n\n' + after
with open('/root/postingboard/backend/templates/idea_detail.html', 'w') as f:
    f.write(new_content)

print(f"Removed {export_start - render_end - 1} characters of Canvas code")
print("File updated successfully")