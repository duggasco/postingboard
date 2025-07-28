#!/usr/bin/env python3
"""
Generate workflow diagrams with straight lines and perpendicular connections
All arrows use only horizontal and vertical segments with bisecting labels
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Polygon
import matplotlib.lines as mlines

class StraightLineWorkflowGenerator:
    def __init__(self):
        self.screenshots_dir = "/root/postingboard/documentation_screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
    def create_all_diagrams(self):
        """Create all workflow diagrams with straight line connections"""
        print("Creating straight-line workflow diagrams...")
        self.create_auth_workflow()
        self.create_claim_workflow()
        self.create_lifecycle_diagram()
        self.create_notification_diagram()
        print("Straight-line workflow diagrams created!")

    def create_auth_workflow(self):
        """Create authentication workflow with straight lines only"""
        fig, ax = plt.subplots(figsize=(10, 12))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 12)
        ax.axis('off')
        
        # Define positions
        main_x = 5
        error_x = 2
        
        # Draw shapes
        shapes = {
            'start': self._draw_shape(ax, main_x, 11, "User Accesses\nProtected Page", "start"),
            'redirect': self._draw_shape(ax, main_x, 10, "Redirect to\nEmail Verification", "process"),
            'email': self._draw_shape(ax, main_x, 9, "Enter Email\nAddress", "input"),
            'generate': self._draw_shape(ax, main_x, 8, "Generate 6-digit\nCode", "process"),
            'send': self._draw_shape(ax, main_x, 7, "Send Code\nvia Email", "process"),
            'enter': self._draw_shape(ax, main_x, 6, "User Enters\nCode", "input"),
            'valid': self._draw_shape(ax, main_x, 5, "Code Valid?", "decision"),
            'error': self._draw_shape(ax, error_x, 5, "Show Error\nRetry", "error"),
            'profile': self._draw_shape(ax, main_x, 3, "Create/Update\nProfile", "process"),
            'success': self._draw_shape(ax, main_x, 1, "Grant Access\n7-day Session", "success")
        }
        
        # Draw straight-line connections
        # Main flow
        self._draw_straight_arrow(ax, main_x, 11, main_x, 10)
        self._draw_straight_arrow(ax, main_x, 10, main_x, 9)
        self._draw_straight_arrow(ax, main_x, 9, main_x, 8)
        self._draw_straight_arrow(ax, main_x, 8, main_x, 7)
        self._draw_straight_arrow(ax, main_x, 7, main_x, 6)
        self._draw_straight_arrow(ax, main_x, 6, main_x, 5)
        
        # Decision branches with perpendicular connections
        # No path - uses perpendicular connector
        self._draw_perpendicular_arrow(ax, main_x, 5, error_x, 5, "No", direction='left')
        
        # Yes path - straight down
        self._draw_straight_arrow(ax, main_x, 5, main_x, 3, "Yes")
        
        # Error loop back - perpendicular path
        self._draw_perpendicular_arrow(ax, error_x, 5, main_x, 6, "", direction='up_right', dashed=True)
        
        # Profile to success
        self._draw_straight_arrow(ax, main_x, 3, main_x, 1)
        
        plt.title('Email-Based Authentication Workflow', fontsize=18, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(f'{self.screenshots_dir}/workflow_auth_straight.png', 
                    dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()

    def create_claim_workflow(self):
        """Create claim approval workflow with straight lines"""
        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_xlim(0, 14)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Positions
        center_x = 7
        left_x = 3
        right_x = 11
        
        # Draw shapes
        shapes = {
            'start': self._draw_shape(ax, center_x, 9, "User Claims\nIdea", "start"),
            'create': self._draw_shape(ax, center_x, 8, "Create Claim\nApproval Request", "process"),
            'notify_owner': self._draw_shape(ax, left_x, 6, "Notify Idea\nOwner", "notification"),
            'notify_manager': self._draw_shape(ax, right_x, 6, "Notify Claimer's\nManager", "notification"),
            'owner_approves': self._draw_shape(ax, left_x, 4, "Owner\nApproves?", "decision"),
            'manager_approves': self._draw_shape(ax, right_x, 4, "Manager\nApproves?", "decision"),
            'both_approved': self._draw_shape(ax, center_x, 2, "Both\nApproved?", "decision"),
            'deny': self._draw_shape(ax, 3, 0.5, "Deny Claim\nNotify User", "error"),
            'create_claim': self._draw_shape(ax, 11, 0.5, "Create Claim\nUpdate Status", "success")
        }
        
        # Main flow
        self._draw_straight_arrow(ax, center_x, 9, center_x, 8)
        
        # Fork to notifications - using perpendicular paths
        self._draw_perpendicular_arrow(ax, center_x, 8, left_x, 6, "", direction='down_left')
        self._draw_perpendicular_arrow(ax, center_x, 8, right_x, 6, "", direction='down_right')
        
        # To decision points
        self._draw_straight_arrow(ax, left_x, 6, left_x, 4)
        self._draw_straight_arrow(ax, right_x, 6, right_x, 4)
        
        # Decision outcomes - perpendicular connections
        self._draw_perpendicular_arrow(ax, left_x, 4, center_x, 2, "Yes", direction='down_right')
        self._draw_straight_arrow(ax, left_x, 4, left_x, 0.5, "No")
        
        self._draw_perpendicular_arrow(ax, right_x, 4, center_x, 2, "Yes", direction='down_left')
        self._draw_straight_arrow(ax, right_x, 4, right_x, 0.5, "No")
        
        # Final decision
        self._draw_perpendicular_arrow(ax, center_x, 2, right_x, 0.5, "Yes", direction='down_right')
        self._draw_perpendicular_arrow(ax, center_x, 2, left_x, 0.5, "No", direction='down_left')
        
        plt.title('Claim Approval Workflow', fontsize=18, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(f'{self.screenshots_dir}/workflow_claim_straight.png', 
                    dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()

    def create_lifecycle_diagram(self):
        """Create idea lifecycle with straight connections"""
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.set_xlim(0, 14)
        ax.set_ylim(0, 8)
        ax.axis('off')
        
        # Main status positions
        status_y = 6
        status_positions = [
            (2, status_y, "Open", "status"),
            (7, status_y, "Claimed", "status"),
            (12, status_y, "Complete", "status")
        ]
        
        # Sub-status positions
        sub_y = 3.5
        sub_positions = [
            (1, sub_y, "Planning", "substatus"),
            (3, sub_y, "In Development", "substatus"),
            (5, sub_y, "Testing", "substatus"),
            (7, sub_y, "Deployment", "substatus"),
            (9, sub_y, "Verification", "substatus"),
            (11, sub_y, "Verified", "substatus")
        ]
        
        # Exception states
        exc_y = 1
        exc_positions = [
            (2, exc_y, "On Hold", "exception"),
            (5, exc_y, "Blocked", "exception"),
            (8, exc_y, "Cancelled", "exception")
        ]
        
        # Draw all shapes
        for x, y, text, stype in status_positions:
            self._draw_shape(ax, x, y, text, stype)
        for x, y, text, stype in sub_positions:
            self._draw_shape(ax, x, y, text, stype)
        for x, y, text, stype in exc_positions:
            self._draw_shape(ax, x, y, text, stype)
        
        # Main flow arrows
        self._draw_straight_arrow(ax, 2, status_y, 7, status_y, "Claim Approved")
        self._draw_straight_arrow(ax, 7, status_y, 12, status_y, "Work Finished")
        
        # To development - perpendicular
        self._draw_perpendicular_arrow(ax, 7, status_y, 1, sub_y, "Start Development", direction='down_left')
        
        # Sub-status flow
        for i in range(len(sub_positions)-1):
            x1, _, _, _ = sub_positions[i]
            x2, _, _, _ = sub_positions[i+1]
            self._draw_straight_arrow(ax, x1, sub_y, x2, sub_y)
        
        # To complete - perpendicular
        self._draw_perpendicular_arrow(ax, 11, sub_y, 12, status_y, "", direction='up_right')
        
        # Exception flows - perpendicular connections
        self._draw_perpendicular_arrow(ax, 1, sub_y, 2, exc_y, "Pause", direction='down', color='orange')
        self._draw_perpendicular_arrow(ax, 5, sub_y, 5, exc_y, "Issue", direction='down', color='red')
        self._draw_perpendicular_arrow(ax, 7, sub_y, 8, exc_y, "Cancel", direction='down_right', color='red')
        
        # Return path
        self._draw_perpendicular_arrow(ax, 2, exc_y, 1, sub_y, "Resume", direction='up', dashed=True, color='green')
        
        plt.title('Idea Development Lifecycle', fontsize=18, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(f'{self.screenshots_dir}/workflow_lifecycle_straight.png', 
                    dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()

    def create_notification_diagram(self):
        """Create notification flow with straight connections"""
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Central event
        center = (6, 8)
        self._draw_shape(ax, center[0], center[1], "Status Change\nEvent", "event")
        
        # Notification targets
        targets = [
            (2, 5, "Idea Owner", "user"),
            (6, 5, "Claimer", "user"),
            (10, 5, "Manager", "user"),
            (2, 2, "Admin", "admin"),
            (10, 2, "Team Members", "team")
        ]
        
        for x, y, text, ttype in targets:
            self._draw_shape(ax, x, y, text, ttype)
        
        # Draw perpendicular connections from center
        # To direct targets
        self._draw_straight_arrow(ax, center[0], center[1], 2, 5, "Notify")
        self._draw_straight_arrow(ax, center[0], center[1], 6, 5, "Notify")
        self._draw_straight_arrow(ax, center[0], center[1], 10, 5, "Notify")
        
        # To lower targets - perpendicular paths
        self._draw_perpendicular_arrow(ax, center[0], center[1], 2, 2, "If Required", direction='down_left')
        self._draw_perpendicular_arrow(ax, center[0], center[1], 10, 2, "If Team Impact", direction='down_right')
        
        # Add notification types
        types_text = "Notification Types:\n• Claim Request\n• Status Change\n• Assignment\n• Approval Required"
        ax.text(6, 0.5, types_text, ha='center', va='bottom', fontsize=10,
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", edgecolor="gray"))
        
        plt.title('Notification System Flow', fontsize=18, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(f'{self.screenshots_dir}/workflow_notifications_straight.png', 
                    dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()

    def _draw_shape(self, ax, x, y, text, shape_type):
        """Draw different shape types"""
        colors = {
            'start': '#90EE90',
            'process': '#87CEEB',
            'decision': '#FFD700',
            'input': '#DDA0DD',
            'error': '#FFB6C1',
            'success': '#98FB98',
            'notification': '#FFA07A',
            'status': '#4682B4',
            'substatus': '#87CEEB',
            'exception': '#FFB6C1',
            'event': '#FFD700',
            'user': '#DDA0DD',
            'admin': '#FF6347',
            'team': '#20B2AA'
        }
        
        color = colors.get(shape_type, '#DDDDDD')
        
        if shape_type == 'start':
            circle = Circle((x, y), 0.5, facecolor=color, edgecolor='black', linewidth=2)
            ax.add_patch(circle)
        elif shape_type == 'decision':
            diamond = Polygon([(x, y+0.4), (x+0.6, y), (x, y-0.4), (x-0.6, y)],
                            facecolor=color, edgecolor='black', linewidth=2)
            ax.add_patch(diamond)
        else:
            if shape_type in ['notification', 'event']:
                box = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6,
                                   boxstyle="round,pad=0.1",
                                   facecolor=color, edgecolor='black', linewidth=2)
            else:
                box = Rectangle((x-0.8, y-0.3), 1.6, 0.6,
                              facecolor=color, edgecolor='black', linewidth=2)
            ax.add_patch(box)
        
        # Add text
        fontsize = 9 if len(text) > 15 else 10
        ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
               fontweight='normal' if shape_type != 'start' else 'bold')
        
        return (x, y)

    def _draw_straight_arrow(self, ax, x1, y1, x2, y2, label="", color='black', dashed=False):
        """Draw a straight arrow between two points"""
        if dashed:
            line_style = '--'
        else:
            line_style = '-'
        
        # Draw line
        ax.plot([x1, x2], [y1, y2], line_style, color=color, linewidth=2)
        
        # Add arrowhead
        dx = x2 - x1
        dy = y2 - y1
        if dx != 0 or dy != 0:
            ax.arrow(x2 - 0.1*(dx/abs(dx) if dx != 0 else 0), 
                    y2 - 0.1*(dy/abs(dy) if dy != 0 else 0),
                    0.05*(dx/abs(dx) if dx != 0 else 0), 
                    0.05*(dy/abs(dy) if dy != 0 else 0),
                    head_width=0.15, head_length=0.1, fc=color, ec=color)
        
        # Add label at midpoint
        if label:
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            
            # Offset label slightly
            offset_x = 0.1 if dx == 0 else 0
            offset_y = 0.1 if dy == 0 else 0
            
            ax.text(mid_x + offset_x, mid_y + offset_y, label,
                   ha='center', va='center', fontsize=9,
                   bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.8))

    def _draw_perpendicular_arrow(self, ax, x1, y1, x2, y2, label="", direction='auto', color='black', dashed=False):
        """Draw a perpendicular (L-shaped) arrow between two points"""
        if dashed:
            line_style = '--'
        else:
            line_style = '-'
        
        # Determine the bend point based on direction
        if direction == 'left':
            # Go left then vertical
            bend_x = x2
            bend_y = y1
        elif direction == 'right':
            # Go right then vertical
            bend_x = x2
            bend_y = y1
        elif direction == 'up':
            # Go up then horizontal
            bend_x = x1
            bend_y = y2
        elif direction == 'down':
            # Go down then horizontal
            bend_x = x1
            bend_y = y2
        elif direction == 'down_left':
            # Go down then left
            bend_x = x1
            bend_y = y2
        elif direction == 'down_right':
            # Go down then right
            bend_x = x1
            bend_y = y2
        elif direction == 'up_right':
            # Go up then right
            bend_x = x1
            bend_y = y2
        elif direction == 'up_left':
            # Go up then left
            bend_x = x1
            bend_y = y2
        else:
            # Auto determine best path
            if abs(x2 - x1) > abs(y2 - y1):
                bend_x = x1
                bend_y = y2
            else:
                bend_x = x2
                bend_y = y1
        
        # Draw the two segments
        ax.plot([x1, bend_x], [y1, bend_y], line_style, color=color, linewidth=2)
        ax.plot([bend_x, x2], [bend_y, y2], line_style, color=color, linewidth=2)
        
        # Add arrowhead at the end
        if bend_x == x2:
            # Vertical ending
            dy = y2 - bend_y
            if dy != 0:
                ax.arrow(x2, y2 - 0.1*(dy/abs(dy)), 0, 0.05*(dy/abs(dy)),
                        head_width=0.15, head_length=0.1, fc=color, ec=color)
        else:
            # Horizontal ending
            dx = x2 - bend_x
            if dx != 0:
                ax.arrow(x2 - 0.1*(dx/abs(dx)), y2, 0.05*(dx/abs(dx)), 0,
                        head_width=0.15, head_length=0.1, fc=color, ec=color)
        
        # Add label at the bend point
        if label:
            ax.text(bend_x, bend_y, label,
                   ha='center', va='center', fontsize=9,
                   bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="none", alpha=0.8))

if __name__ == "__main__":
    generator = StraightLineWorkflowGenerator()
    generator.create_all_diagrams()