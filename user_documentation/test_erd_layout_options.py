#!/usr/bin/env python3
"""
Test different ERD layout options to avoid relationship ambiguity
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

for ax, title, layout_type in [(ax1, 'Current Layout (Ambiguous)', 'horizontal'), 
                                (ax2, 'Improved Layout (Clear)', 'offset')]:
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Entity positions
    if layout_type == 'horizontal':
        # Current problematic layout - all on same line
        entities = {
            'Idea': {'pos': (2, 8), 'width': 3.5, 'height': 2.5},
            'Skill': {'pos': (7, 8), 'width': 2.5, 'height': 0.8},
            'Team': {'pos': (12, 8), 'width': 3.0, 'height': 1.0},
            'Claim': {'pos': (2, 4), 'width': 3.0, 'height': 1.2},
            'UserProfile': {'pos': (12, 4), 'width': 3.5, 'height': 1.5}
        }
    else:
        # Improved layout - offset to show relationships clearly
        entities = {
            'Idea': {'pos': (7, 8), 'width': 3.5, 'height': 2.5},  # Center top
            'Skill': {'pos': (3, 6), 'width': 2.5, 'height': 0.8},  # Left middle
            'Team': {'pos': (11, 6), 'width': 3.0, 'height': 1.0},  # Right middle
            'Claim': {'pos': (3, 3), 'width': 3.0, 'height': 1.2},  # Left bottom
            'UserProfile': {'pos': (11, 3), 'width': 3.5, 'height': 1.5}  # Right bottom
        }
    
    # Draw entities
    for name, info in entities.items():
        x, y = info['pos']
        w, h = info['width'], info['height']
        
        # Draw entity box
        box = FancyBboxPatch(
            (x - w/2, y - h/2), w, h,
            boxstyle="round,pad=0.05",
            facecolor='white',
            edgecolor='#4a90e2',
            linewidth=2
        )
        ax.add_patch(box)
        
        # Draw entity name
        ax.text(x, y, name, ha='center', va='center', 
                fontsize=11, fontweight='bold')
    
    # Draw relationships
    relationships = [
        ('Idea', 'Skill', 'M:N', 'has'),
        ('Idea', 'Team', 'M:1', 'belongs to'),
        ('Idea', 'Claim', '1:M', 'has'),
        ('UserProfile', 'Team', 'M:1', 'belongs to')
    ]
    
    for start_name, end_name, cardinality, label in relationships:
        if start_name in entities and end_name in entities:
            start = entities[start_name]['pos']
            end = entities[end_name]['pos']
            
            # Draw line
            ax.plot([start[0], end[0]], [start[1], end[1]], 
                    'k-', linewidth=1.5, zorder=1)
            
            # Calculate midpoint
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            
            # Add labels
            ax.text(mid_x, mid_y, f"{cardinality}",
                    ha='center', va='center', fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='white', 
                             edgecolor='none', alpha=0.9))
    
    # Highlight issues/benefits
    if layout_type == 'horizontal':
        # Show ambiguity
        ax.plot([4.5, 9.5], [8, 8], 'r--', linewidth=2, alpha=0.5)
        ax.text(7, 8.7, '? Unclear if Skill ↔ Team related ?', 
                ha='center', color='red', fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
        
        # Show label collision area
        ax.add_patch(Rectangle((6, 7.6), 2, 0.8, 
                              fill=True, facecolor='red', alpha=0.2))
        ax.text(7, 7.2, 'Label collision zone', ha='center', 
                color='red', fontsize=9, style='italic')
    else:
        # Show clarity
        ax.text(7, 5, '✓ Clear hub-and-spoke pattern\n✓ No ambiguous relationships\n✓ Labels have space',
                ha='center', color='green', fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7))
        
        # Highlight the hub
        circle = plt.Circle(entities['Idea']['pos'], 3.5, 
                           fill=False, edgecolor='green', 
                           linewidth=2, linestyle='--', alpha=0.5)
        ax.add_patch(circle)

plt.tight_layout()
plt.savefig('/root/postingboard/documentation_screenshots/test_erd_layout_options.png', 
            dpi=150, bbox_inches='tight')
plt.close()

print("Test image saved to: documentation_screenshots/test_erd_layout_options.png")
print("\nLayout comparison:")
print("1. Current Layout Problems:")
print("   - Skill and Team appear connected when they're not")
print("   - Horizontal alignment creates label collision zone")
print("   - Ambiguous relationship paths")
print("\n2. Improved Layout Benefits:")
print("   - Hub-and-spoke pattern with Idea at center")
print("   - Clear relationship paths")
print("   - No visual ambiguity")
print("   - More space for labels")