#!/usr/bin/env python3
"""
Professional Workflow Diagrams with Clean Layouts
Uses graphviz for better arrow routing and professional appearance
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyBboxPatch, Circle, Polygon
import matplotlib.lines as mlines

class ProfessionalWorkflowGenerator:
    def __init__(self):
        self.screenshots_dir = "/root/postingboard/documentation_screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
    def create_all_diagrams(self):
        """Create all workflow diagrams with professional layouts"""
        print("Creating professional workflow diagrams...")
        self.create_auth_workflow()
        self.create_claim_workflow()
        self.create_lifecycle_diagram()
        self.create_notification_diagram()
        print("Professional workflow diagrams created!")

    def create_auth_workflow(self):
        """Create authentication workflow with clean vertical layout"""
        fig, ax = plt.subplots(figsize=(8, 11))
        ax.set_xlim(0, 8)
        ax.set_ylim(0, 11)
        ax.axis('off')
        
        # Define positions - single column for main flow
        main_x = 4
        error_x = 1.5
        success_x = 6.5
        
        # Step positions
        steps = [
            (main_x, 10, "User Accesses\nProtected Page", "start"),
            (main_x, 9, "Redirect to\nEmail Verification", "process"),
            (main_x, 8, "Enter Email\nAddress", "input"),
            (main_x, 7, "Generate 6-digit\nCode", "process"),
            (main_x, 6, "Send Code\nvia Email", "process"),
            (main_x, 5, "User Enters\nCode", "input"),
            (main_x, 4, "Code Valid?", "decision"),
            (error_x, 3, "Show Error\nRetry", "error"),
            (main_x, 2, "Create/Update\nProfile", "process"),
            (success_x, 1, "Grant Access\n7-day Session", "success")
        ]
        
        # Draw all steps
        shapes = []
        for x, y, text, stype in steps:
            shape = self._draw_shape(ax, x, y, text, stype)
            shapes.append((x, y))
        
        # Draw arrows - main flow
        for i in range(6):
            self._draw_arrow(ax, shapes[i], shapes[i+1])
        
        # Decision branches
        # No path
        self._draw_arrow(ax, (main_x, 4), (error_x, 3), label="No", curved=True)
        # Yes path
        self._draw_arrow(ax, (main_x, 4), (main_x, 2), label="Yes")
        # Error loop back
        self._draw_arrow(ax, (error_x, 3), (main_x, 5), curved=True, dashed=True)
        # Profile to success
        self._draw_arrow(ax, (main_x, 2), (success_x, 1), curved=True)
        
        plt.title('Email-Based Authentication Workflow', fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(f'{self.screenshots_dir}/workflow_auth_professional.png', 
                    dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()

    def create_claim_workflow(self):
        """Create claim approval workflow with clear dual paths"""
        fig, ax = plt.subplots(figsize=(12, 9))
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 9)
        ax.axis('off')
        
        # Positions
        center_x = 6
        left_x = 2.5
        right_x = 9.5
        
        elements = [
            (center_x, 8, "User Claims\nIdea", "start"),
            (center_x, 7, "Create Claim\nApproval Request", "process"),
            (left_x, 5.5, "Notify Idea\nOwner", "notification"),
            (right_x, 5.5, "Notify Claimer's\nManager", "notification"),
            (left_x, 4, "Owner\nApproves?", "decision"),
            (right_x, 4, "Manager\nApproves?", "decision"),
            (center_x, 2.5, "Both\nApproved?", "decision"),
            (left_x, 1, "Deny Claim\nNotify User", "error"),
            (right_x, 1, "Create Claim", "success"),
            (center_x, 0.5, "Idea Status:\nClaimed", "success")
        ]
        
        # Draw elements
        for x, y, text, etype in elements:
            self._draw_shape(ax, x, y, text, etype)
        
        # Draw connections
        self._draw_arrow(ax, (center_x, 8), (center_x, 7))
        
        # Fork to notifications
        self._draw_arrow(ax, (center_x, 7), (left_x, 5.5), curved=True)
        self._draw_arrow(ax, (center_x, 7), (right_x, 5.5), curved=True)
        
        # To decisions
        self._draw_arrow(ax, (left_x, 5.5), (left_x, 4))
        self._draw_arrow(ax, (right_x, 5.5), (right_x, 4))
        
        # Decision outcomes
        self._draw_arrow(ax, (left_x, 4), (center_x, 2.5), label="Yes", curved=True)
        self._draw_arrow(ax, (left_x, 4), (left_x, 1), label="No")
        
        self._draw_arrow(ax, (right_x, 4), (center_x, 2.5), label="Yes", curved=True)
        self._draw_arrow(ax, (right_x, 4), (right_x, 1), label="No")
        
        # Final decision
        self._draw_arrow(ax, (center_x, 2.5), (center_x, 0.5), label="Yes")
        self._draw_arrow(ax, (center_x, 2.5), (left_x, 1), label="No", curved=True)
        
        # Success to final
        self._draw_arrow(ax, (right_x, 1), (center_x, 0.5), curved=True)
        
        # Add central label
        ax.text(center_x, 6, 'Dual Approval Required', ha='center', va='center',
                style='italic', fontsize=10, color='#666',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#fffacd', 
                         edgecolor='#daa520', linewidth=1))
        
        plt.title('Claim Approval Workflow (Dual Approval)', fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(f'{self.screenshots_dir}/workflow_claim_professional.png', 
                    dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()

    def create_lifecycle_diagram(self):
        """Create idea lifecycle state diagram"""
        fig, ax = plt.subplots(figsize=(14, 10))
        ax.set_xlim(0, 14)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Main states
        main_states = [
            (2, 8, "Open", "#e7f5ed"),
            (7, 8, "Claimed", "#fff3cd"),
            (12, 8, "Complete", "#e9ecef")
        ]
        
        # Sub-states
        sub_states = [
            (2, 5.5, "Planning", "#e3f2fd"),
            (4.5, 5.5, "In Development", "#e3f2fd"),
            (7, 5.5, "Testing", "#e3f2fd"),
            (9.5, 5.5, "Awaiting\nDeployment", "#e3f2fd"),
            (12, 5.5, "Deployed", "#e3f2fd"),
            (12, 3.5, "Verified", "#e8f5e8")
        ]
        
        # Exception states
        exception_states = [
            (2, 2, "On Hold", "#ffe0b2"),
            (5, 2, "Blocked", "#ffcdd2"),
            (8, 2, "Cancelled", "#ffcdd2")
        ]
        
        # Draw all states
        for x, y, text, color in main_states:
            self._draw_state_box(ax, x, y, text, color, bold=True)
            
        for x, y, text, color in sub_states:
            self._draw_state_box(ax, x, y, text, color)
            
        for x, y, text, color in exception_states:
            self._draw_state_box(ax, x, y, text, color)
        
        # Main flow arrows
        self._draw_arrow(ax, (2, 8), (7, 8), label="Claim Approved")
        self._draw_arrow(ax, (7, 8), (12, 8), label="Work Finished")
        
        # To development
        self._draw_arrow(ax, (7, 8), (2, 5.5), label="Start Development", curved=True)
        
        # Development flow
        dev_flow = [(2, 5.5), (4.5, 5.5), (7, 5.5), (9.5, 5.5), (12, 5.5)]
        for i in range(len(dev_flow)-1):
            self._draw_arrow(ax, dev_flow[i], dev_flow[i+1])
        
        # To verified
        self._draw_arrow(ax, (12, 5.5), (12, 3.5))
        
        # Exception flows
        self._draw_arrow(ax, (2, 5.5), (2, 2), label="Pause", color='orange')
        self._draw_arrow(ax, (4.5, 5.5), (5, 2), label="Issue", color='red')
        self._draw_arrow(ax, (7, 5.5), (8, 2), label="Cancel", color='red')
        
        # Return arrow
        self._draw_arrow(ax, (2, 2), (2, 5.5), label="Resume", 
                        curved=True, dashed=True, color='green')
        
        # Title and subtitle
        ax.text(7, 9.5, 'Idea Lifecycle States', ha='center', va='center',
                fontsize=18, fontweight='bold')
        ax.text(7, 9, 'Main States: Open → Claimed → Complete', ha='center', va='center',
                fontsize=10, style='italic', color='#666')
        ax.text(7, 6.5, 'Development Sub-states (available during Claimed status)', 
                ha='center', va='center', fontsize=10, style='italic', color='#666')
        
        plt.tight_layout()
        plt.savefig(f'{self.screenshots_dir}/workflow_lifecycle_professional.png', 
                    dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()

    def create_notification_diagram(self):
        """Create notification system flow diagram"""
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Central system
        center = (6, 5)
        self._draw_central_system(ax, center)
        
        # Event sources in circular arrangement
        import numpy as np
        n_events = 8
        radius = 3
        events = [
            "Claim\nRequests",
            "Status\nChanges", 
            "Team\nUpdates",
            "Approvals",
            "Assignments",
            "Manager\nRequests",
            "Bounty\nApprovals",
            "Comments"
        ]
        
        # Calculate positions
        angles = np.linspace(0, 2*np.pi, n_events, endpoint=False)
        for i, (event, angle) in enumerate(zip(events, angles)):
            x = center[0] + radius * np.cos(angle)
            y = center[1] + radius * np.sin(angle)
            
            # Draw event box
            self._draw_event_box(ax, x, y, event)
            
            # Draw arrow to center
            # Calculate edge points
            dx = center[0] - x
            dy = center[1] - y
            norm = np.sqrt(dx**2 + dy**2)
            dx, dy = dx/norm, dy/norm
            
            start_x = x + 0.8 * dx
            start_y = y + 0.4 * dy
            end_x = center[0] - 1.2 * dx
            end_y = center[1] - 0.6 * dy
            
            ax.arrow(start_x, start_y, end_x - start_x, end_y - start_y,
                    head_width=0.15, head_length=0.1, fc='#666', ec='#666',
                    length_includes_head=True)
        
        # Add recipients
        recipients = [
            (6, 8.5, "Users", "#4caf50"),
            (1, 2, "Managers", "#ff9800"),
            (11, 2, "Admins", "#f44336")
        ]
        
        for x, y, text, color in recipients:
            circle = Circle((x, y), 0.5, facecolor=color, edgecolor='black', 
                          alpha=0.8, linewidth=2)
            ax.add_patch(circle)
            ax.text(x, y, text, ha='center', va='center', color='white', 
                   fontweight='bold', fontsize=10)
        
        plt.title('Notification System Event Flow', fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(f'{self.screenshots_dir}/workflow_notifications_professional.png', 
                    dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
        plt.close()

    # Helper methods
    def _draw_shape(self, ax, x, y, text, shape_type):
        """Draw a workflow shape"""
        if shape_type == "start":
            circle = Circle((x, y), 0.4, facecolor='#e8f5e8', 
                          edgecolor='#2e7d32', linewidth=2)
            ax.add_patch(circle)
        elif shape_type == "process":
            rect = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6,
                                boxstyle="round,pad=0.05",
                                facecolor='#e3f2fd', edgecolor='#1976d2', 
                                linewidth=1.5)
            ax.add_patch(rect)
        elif shape_type == "decision":
            diamond = Polygon([(x, y+0.4), (x+0.5, y), (x, y-0.4), (x-0.5, y)],
                            facecolor='#fff3cd', edgecolor='#f57c00', linewidth=1.5)
            ax.add_patch(diamond)
        elif shape_type == "input":
            rect = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6,
                                boxstyle="round,pad=0.05",
                                facecolor='#ede7f6', edgecolor='#7b1fa2', 
                                linewidth=1.5)
            ax.add_patch(rect)
        elif shape_type == "notification":
            rect = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6,
                                boxstyle="round,pad=0.05",
                                facecolor='#fce4ec', edgecolor='#c2185b', 
                                linewidth=1.5)
            ax.add_patch(rect)
        elif shape_type == "error":
            rect = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6,
                                boxstyle="round,pad=0.05",
                                facecolor='#ffcdd2', edgecolor='#d32f2f', 
                                linewidth=1.5)
            ax.add_patch(rect)
        elif shape_type == "success":
            rect = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6,
                                boxstyle="round,pad=0.05",
                                facecolor='#c8e6c9', edgecolor='#388e3c', 
                                linewidth=1.5)
            ax.add_patch(rect)
        
        # Add text
        ax.text(x, y, text, ha='center', va='center', fontsize=9, 
               fontweight='normal' if shape_type != 'start' else 'bold')

    def _draw_arrow(self, ax, start, end, label="", curved=False, dashed=False, color='black'):
        """Draw an arrow between two points"""
        x1, y1 = start
        x2, y2 = end
        
        if curved:
            # Create a curved path
            mid_x = (x1 + x2) / 2
            if x1 < x2:
                mid_x -= 0.5
            else:
                mid_x += 0.5
            mid_y = (y1 + y2) / 2
            
            # Use quadratic bezier curve
            from matplotlib.patches import FancyArrowPatch
            from matplotlib.path import Path
            import matplotlib.patches as mpatches
            
            if dashed:
                style = 'dashed'
            else:
                style = 'solid'
                
            arrow = FancyArrowPatch(start, end,
                                  connectionstyle="arc3,rad=.3",
                                  arrowstyle='->', mutation_scale=15,
                                  linewidth=1.5, color=color, linestyle=style)
            ax.add_patch(arrow)
        else:
            # Straight arrow
            dx = x2 - x1
            dy = y2 - y1
            
            if dashed:
                ax.plot([x1, x2], [y1, y2], '--', color=color, linewidth=1.5)
                # Add arrowhead manually
                ax.arrow(x2 - 0.1*dx/abs(dx) if dx != 0 else x2, 
                        y2 - 0.1*dy/abs(dy) if dy != 0 else y2,
                        0.1*dx/abs(dx) if dx != 0 else 0, 
                        0.1*dy/abs(dy) if dy != 0 else 0,
                        head_width=0.15, head_length=0.1, fc=color, ec=color)
            else:
                ax.arrow(x1, y1, dx*0.85, dy*0.85,
                        head_width=0.15, head_length=0.1, fc=color, ec=color,
                        linewidth=1.5, length_includes_head=True)
        
        # Add label if provided
        if label:
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            if curved:
                if x1 < x2:
                    mid_x -= 0.3
                else:
                    mid_x += 0.3
            ax.text(mid_x, mid_y, label, ha='center', va='center',
                   fontsize=8, bbox=dict(boxstyle="round,pad=0.2",
                   facecolor='white', edgecolor='none'))

    def _draw_state_box(self, ax, x, y, text, color, bold=False):
        """Draw a state box"""
        rect = FancyBboxPatch((x-0.9, y-0.35), 1.8, 0.7,
                            boxstyle="round,pad=0.05",
                            facecolor=color, edgecolor='black', 
                            linewidth=2 if bold else 1.5)
        ax.add_patch(rect)
        ax.text(x, y, text, ha='center', va='center', 
               fontsize=10, fontweight='bold' if bold else 'normal')

    def _draw_central_system(self, ax, center):
        """Draw the central notification system"""
        rect = FancyBboxPatch((center[0]-1.5, center[1]-0.7), 3, 1.4,
                            boxstyle="round,pad=0.05",
                            facecolor='#4a90e2', edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(center[0], center[1], 'Notification\nSystem', 
               ha='center', va='center', color='white', 
               fontweight='bold', fontsize=12)

    def _draw_event_box(self, ax, x, y, text):
        """Draw an event source box"""
        rect = FancyBboxPatch((x-0.7, y-0.3), 1.4, 0.6,
                            boxstyle="round,pad=0.05",
                            facecolor='#e3f2fd', edgecolor='#1976d2', 
                            linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x, y, text, ha='center', va='center', fontsize=8)

if __name__ == "__main__":
    generator = ProfessionalWorkflowGenerator()
    generator.create_all_diagrams()