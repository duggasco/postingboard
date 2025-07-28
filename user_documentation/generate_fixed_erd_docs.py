#!/usr/bin/env python3
"""
Fixed ERD Generator - Straight arrows only with properly bisecting labels
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

class FixedERDGenerator:
    def __init__(self):
        self.screenshots_dir = "/root/postingboard/documentation_screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        # Track label positions to avoid overlaps
        self.label_positions = []
        
    def calculate_box_width(self, name, attributes):
        """Calculate appropriate box width based on content"""
        # Estimate character width for different font sizes
        # Using more generous multipliers to ensure text fits
        name_width = len(name) * 0.12  # font size 12
        max_attr_width = max(len(attr) * 0.085 for attr in attributes) if attributes else 0  # font size 8
        
        # Set minimum width and add padding
        min_width = 2.5
        padding = 0.8  # More padding for safety
        return max(min_width, max(name_width, max_attr_width) + padding)
        
    def create_all_erds(self):
        """Create all ERD diagrams with fixed arrow connections"""
        print("Creating fixed ERD diagrams with proper arrow connections...")
        self.create_main_erd()
        self.create_sdlc_erd()
        self.create_auth_erd()
        print("Fixed ERD diagrams created!")

    def create_main_erd(self):
        """Create main ERD showing core entities with improved layout"""
        fig, ax = plt.subplots(1, 1, figsize=(16, 12))
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 12)
        ax.axis('off')
        
        # Define entities with improved hub-and-spoke layout
        # Idea is the central entity, others arranged around it in a circle
        entities = {
            'Idea': {
                'pos': (8, 6),  # Center of diagram
                'attrs': ['uuid (PK)', 'title', 'description', 'email', 'benefactor_team_uuid', 
                         'priority', 'size', 'status', 'sub_status', 'progress_percentage',
                         'bounty', 'needed_by', 'created_at', 'updated_at']
            },
            'Skill': {
                'pos': (3, 9),  # Upper left
                'attrs': ['uuid (PK)', 'name']
            },
            'Team': {
                'pos': (13, 9),  # Upper right
                'attrs': ['uuid (PK)', 'name', 'is_approved']
            },
            'Claim': {
                'pos': (2, 6),  # Left
                'attrs': ['uuid (PK)', 'idea_uuid (FK)', 'claimer_email', 'claimed_at']
            },
            'ClaimApproval': {
                'pos': (3, 3),  # Lower left
                'attrs': ['uuid (PK)', 'idea_uuid (FK)', 'claimer_email', 'claimer_name',
                         'idea_owner_approved', 'manager_approved', 'status']
            },
            'UserProfile': {
                'pos': (14, 6),  # Right
                'attrs': ['email (PK)', 'name', 'role', 'team_uuid (FK)', 
                         'managed_team_uuid (FK)', 'is_verified']
            },
            'Bounty': {
                'pos': (8, 2),  # Bottom center
                'attrs': ['uuid (PK)', 'idea_uuid (FK)', 'is_monetary', 'is_expensed',
                         'amount', 'requires_approval', 'is_approved']
            },
            'Notification': {
                'pos': (13, 3),  # Lower right
                'attrs': ['uuid (PK)', 'user_email', 'type', 'title', 'message',
                         'idea_uuid (FK)', 'is_read', 'created_at']
            }
        }
        
        # FIRST: Draw all entities and store their actual shapes
        entity_shapes = {}
        for entity_name, entity_info in entities.items():
            shape = self.draw_entity(ax, entity_name, entity_info['pos'], entity_info['attrs'])
            entity_shapes[entity_name] = {'shape': shape, 'pos': entity_info['pos']}
        
        # SECOND: Draw relationships between the actual entity boxes
        relationships = [
            ('Idea', 'Skill', 'M:N', 'has'),
            ('Idea', 'Team', 'M:1', 'belongs to'),
            ('Idea', 'Claim', '1:M', 'has'),
            ('Idea', 'ClaimApproval', '1:M', 'has'),
            ('Idea', 'Bounty', '1:1', 'has'),
            ('Idea', 'Notification', '1:M', 'triggers'),
            ('UserProfile', 'Team', 'M:1', 'belongs to'),
        ]
        
        # Clear label positions for this diagram
        self.label_positions = []
        
        for start_entity, end_entity, cardinality, label in relationships:
            self.draw_relationship(ax, entity_shapes[start_entity], entity_shapes[end_entity], 
                                 cardinality, label)
        
        plt.title('Main Database Schema - Core Entities', fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig(f'{self.screenshots_dir}/erd_main_fixed.png', dpi=300, bbox_inches='tight')
        plt.close()

    def create_sdlc_erd(self):
        """Create ERD for SDLC tracking entities"""
        fig, ax = plt.subplots(1, 1, figsize=(14, 10))
        ax.set_xlim(0, 14)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Clear label positions for this diagram
        self.label_positions = []
        
        # Hub-and-spoke layout with Idea at center
        entities = {
            'Idea': {
                'pos': (7, 5),  # Center
                'attrs': ['uuid (PK)', 'title', 'sub_status', 'progress_percentage']
            },
            'StatusHistory': {
                'pos': (2, 7),  # Upper left
                'attrs': ['uuid (PK)', 'idea_uuid (FK)', 'from_status', 'to_status',
                         'from_sub_status', 'to_sub_status', 'changed_by', 'changed_at']
            },
            'IdeaComment': {
                'pos': (7, 8.5),  # Top
                'attrs': ['uuid (PK)', 'idea_uuid (FK)', 'author_email', 'content',
                         'is_internal', 'created_at']
            },
            'IdeaActivity': {
                'pos': (12, 7),  # Upper right
                'attrs': ['uuid (PK)', 'idea_uuid (FK)', 'activity_type', 'actor_email',
                         'description', 'created_at']
            },
            'IdeaExternalLink': {
                'pos': (2, 3),  # Lower left
                'attrs': ['uuid (PK)', 'idea_uuid (FK)', 'link_type', 'title',
                         'url', 'description']
            },
            'IdeaStageData': {
                'pos': (12, 3),  # Lower right
                'attrs': ['uuid (PK)', 'idea_uuid (FK)', 'stage', 'field_name',
                         'field_value', 'updated_at']
            }
        }
        
        # FIRST: Draw all entities
        entity_shapes = {}
        for entity_name, entity_info in entities.items():
            shape = self.draw_entity(ax, entity_name, entity_info['pos'], entity_info['attrs'])
            entity_shapes[entity_name] = {'shape': shape, 'pos': entity_info['pos']}
        
        # SECOND: Draw relationships - all connect to Idea
        for entity_name in entities:
            if entity_name != 'Idea':
                self.draw_relationship(ax, entity_shapes['Idea'], entity_shapes[entity_name], 
                                     '1:M', 'has')
        
        plt.title('SDLC Tracking Schema', fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig(f'{self.screenshots_dir}/erd_sdlc_fixed.png', dpi=300, bbox_inches='tight')
        plt.close()

    def create_auth_erd(self):
        """Create ERD for authentication and user management"""
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 8)
        ax.axis('off')
        
        # Clear label positions for this diagram
        self.label_positions = []
        
        # Hub-and-spoke layout with UserProfile at center
        entities = {
            'UserProfile': {
                'pos': (6, 4),  # Center
                'attrs': ['email (PK)', 'name', 'role', 'team_uuid (FK)',
                         'managed_team_uuid (FK)', 'is_verified', 'created_at']
            },
            'VerificationCode': {
                'pos': (2, 6),  # Upper left
                'attrs': ['uuid (PK)', 'email', 'code', 'created_at',
                         'expires_at', 'attempts', 'is_used']
            },
            'ManagerRequest': {
                'pos': (10, 6),  # Upper right
                'attrs': ['uuid (PK)', 'user_email (FK)', 'requested_team_uuid (FK)',
                         'status', 'requested_at', 'processed_at', 'processed_by']
            },
            'user_skills': {
                'pos': (6, 1),  # Bottom
                'attrs': ['user_email (FK)', 'skill_uuid (FK)']
            }
        }
        
        # First pass: Create entity shapes without drawing them
        entity_shapes = {}
        for entity_name, entity_info in entities.items():
            x, y = entity_info['pos']
            # Match the height calculation from draw_entity
            title_height = 0.3
            separator_space = 0.1
            attr_height = len(entity_info['attrs']) * 0.15
            padding = 0.2
            box_height = title_height + separator_space + attr_height + padding
            box_width = self.calculate_box_width(entity_name, entity_info['attrs'])
            rect = FancyBboxPatch(
                (x - box_width/2, y - box_height/2),
                box_width, box_height,
                boxstyle="round,pad=0.05"
            )
            entity_shapes[entity_name] = {'shape': rect, 'pos': entity_info['pos']}
        
        # Draw relationships FIRST
        relationships = [
            ('UserProfile', 'VerificationCode', '1:M', 'has'),
            ('UserProfile', 'ManagerRequest', '1:M', 'requests'),
            ('UserProfile', 'user_skills', '1:M', 'has'),
        ]
        
        for start_entity, end_entity, cardinality, label in relationships:
            self.draw_relationship(ax, entity_shapes[start_entity], entity_shapes[end_entity], 
                                 cardinality, label)
        
        # Now draw entities on top
        for entity_name, entity_info in entities.items():
            shape = self.draw_entity(ax, entity_name, entity_info['pos'], entity_info['attrs'])
            entity_shapes[entity_name]['shape'] = shape
        
        plt.title('Authentication & User Management Schema', fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig(f'{self.screenshots_dir}/erd_auth_fixed.png', dpi=300, bbox_inches='tight')
        plt.close()

    def draw_entity(self, ax, name, pos, attributes):
        """Draw an entity box with attributes and return the shape"""
        x, y = pos
        
        # Calculate box dimensions based on content
        # Height needs to accommodate: 
        # - Title area: 0.3
        # - Separator space: 0.1
        # - Each attribute: 0.15
        # - Bottom padding: 0.1
        title_height = 0.3
        separator_space = 0.1
        attr_height = len(attributes) * 0.15
        padding = 0.2  # top and bottom padding
        box_height = title_height + separator_space + attr_height + padding
        
        # Use consistent width calculation
        box_width = self.calculate_box_width(name, attributes)
        
        # First draw a slightly larger white background box to hide line overlaps
        bg_rect = FancyBboxPatch(
            (x - box_width/2 - 0.02, y - box_height/2 - 0.02),
            box_width + 0.04, box_height + 0.04,
            boxstyle="round,pad=0.05",
            facecolor='white',
            edgecolor='none',  # No border for background
            zorder=4  # Above lines but below main box
        )
        ax.add_patch(bg_rect)
        
        # Draw entity box with high z-order to appear on top
        rect = FancyBboxPatch(
            (x - box_width/2, y - box_height/2),
            box_width, box_height,
            boxstyle="round,pad=0.05",
            facecolor='white',
            edgecolor='#4a90e2',
            linewidth=2,
            zorder=5  # Higher than background
        )
        ax.add_patch(rect)
        
        # Draw entity name with high z-order
        # Split long names if needed
        if len(name) > 15:
            # Try to split at underscores or capitals
            if '_' in name:
                parts = name.split('_')
                display_name = '\n'.join(parts)
            else:
                # Split at capital letters for camelCase
                import re
                parts = re.findall('[A-Z][^A-Z]*', name)
                if parts:
                    display_name = '\n'.join(parts)
                else:
                    display_name = name
        else:
            display_name = name
            
        ax.text(x, y + box_height/2 - 0.15, display_name, 
                ha='center', va='center', fontsize=12, fontweight='bold',
                zorder=6)  # Higher than box
        
        # Draw separator line with high z-order
        ax.plot([x - box_width/2 + 0.1, x + box_width/2 - 0.1],
                [y + box_height/2 - 0.3, y + box_height/2 - 0.3],
                'k-', linewidth=1, zorder=6)
        
        # Draw attributes with high z-order
        # Start attributes just below the separator line
        attr_start_y = y + box_height/2 - 0.4
        for i, attr in enumerate(attributes):
            attr_y = attr_start_y - i*0.15
            ax.text(x, attr_y, attr,
                    ha='center', va='center', fontsize=8,
                    zorder=6)  # Higher than box
        
        return rect

    def draw_relationship(self, ax, start_entity, end_entity, cardinality, label):
        """Draw relationship lines between entities with properly bisecting labels"""
        start_pos = start_entity['pos']
        end_pos = end_entity['pos']
        start_shape = start_entity['shape']
        end_shape = end_entity['shape']
        
        # Use FancyArrowPatch which automatically calculates edge connections
        arrow = patches.FancyArrowPatch(
            start_pos, end_pos,
            patchA=start_shape, patchB=end_shape,
            arrowstyle='-',  # No arrowhead
            shrinkA=5, shrinkB=5,  # Small gap from box edge
            mutation_scale=16,
            linewidth=1.5,
            color='black',
            zorder=2  # Above background (1) but below boxes (5)
        )
        ax.add_patch(arrow)
        
        # Calculate label position at midpoint between entity CENTERS
        mid_x = (start_pos[0] + end_pos[0]) / 2
        mid_y = (start_pos[1] + end_pos[1]) / 2
        
        # Add this label position to the tracking list
        self.label_positions.append((mid_x, mid_y))
        
        # Draw cardinality label
        ax.text(mid_x, mid_y + 0.15, cardinality, 
                ha='center', va='center', fontsize=9, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                         edgecolor='none', alpha=1.0),
                zorder=10)
        
        # Draw relationship label if provided
        if label:
            ax.text(mid_x, mid_y - 0.15, label,
                    ha='center', va='center', fontsize=8, style='italic',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                             edgecolor='none', alpha=1.0),
                    zorder=10)

if __name__ == "__main__":
    generator = FixedERDGenerator()
    generator.create_all_erds()