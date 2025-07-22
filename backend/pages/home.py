from dash import html, dcc, callback, Input, Output, State, dash_table
import pandas as pd
from datetime import datetime
from database import get_session
from models import Idea, Skill, Claim, IdeaStatus, PriorityLevel, IdeaSize

# Priority colors
PRIORITY_COLORS = {
    'low': '#28a745',
    'medium': '#ffc107', 
    'high': '#dc3545'
}

# Size labels
SIZE_LABELS = {
    'small': 'Small (1-2 days)',
    'medium': 'Medium (3-5 days)',
    'large': 'Large (1-2 weeks)',
    'extra_large': 'Extra Large (2+ weeks)'
}

layout = html.Div([
    html.H2('Browse Ideas', style={'textAlign': 'center', 'marginBottom': '30px'}),
    
    # Filters
    html.Div([
        html.Div([
            html.Label('Filter by Skill:'),
            dcc.Dropdown(
                id='skill-filter',
                options=[],
                placeholder='All Skills',
                clearable=True
            )
        ], style={'width': '200px'}),
        
        html.Div([
            html.Label('Filter by Priority:'),
            dcc.Dropdown(
                id='priority-filter',
                options=[
                    {'label': 'All', 'value': ''},
                    {'label': 'Low', 'value': 'low'},
                    {'label': 'Medium', 'value': 'medium'},
                    {'label': 'High', 'value': 'high'}
                ],
                value='',
                clearable=False
            )
        ], style={'width': '150px'}),
        
        html.Div([
            html.Label('Filter by Status:'),
            dcc.Dropdown(
                id='status-filter',
                options=[
                    {'label': 'All', 'value': ''},
                    {'label': 'Open', 'value': 'open'},
                    {'label': 'Claimed', 'value': 'claimed'},
                    {'label': 'Complete', 'value': 'complete'}
                ],
                value='open',
                clearable=False
            )
        ], style={'width': '150px'}),
        
        html.Div([
            html.Label('Sort by:'),
            dcc.Dropdown(
                id='sort-by',
                options=[
                    {'label': 'Date (Newest)', 'value': 'date_desc'},
                    {'label': 'Date (Oldest)', 'value': 'date_asc'},
                    {'label': 'Priority', 'value': 'priority'},
                    {'label': 'Size', 'value': 'size'}
                ],
                value='date_desc',
                clearable=False
            )
        ], style={'width': '150px'})
    ], style={
        'display': 'flex',
        'gap': '20px',
        'marginBottom': '30px',
        'flexWrap': 'wrap'
    }),
    
    # Ideas container
    html.Div(id='ideas-container'),
    
    # Refresh interval
    dcc.Interval(id='refresh-interval', interval=30000)  # Refresh every 30 seconds
])

@callback(
    Output('skill-filter', 'options'),
    Input('refresh-interval', 'n_intervals')
)
def update_skill_options(n):
    db = get_session()
    try:
        skills = db.query(Skill).order_by(Skill.name).all()
        return [{'label': skill.name, 'value': skill.name} for skill in skills]
    finally:
        db.close()

@callback(
    Output('ideas-container', 'children'),
    [Input('skill-filter', 'value'),
     Input('priority-filter', 'value'),
     Input('status-filter', 'value'),
     Input('sort-by', 'value'),
     Input('refresh-interval', 'n_intervals')]
)
def update_ideas_list(skill_filter, priority_filter, status_filter, sort_by, n):
    # Handle None/empty values from dropdowns on initial load
    if status_filter == '' or status_filter is None:
        status_filter = 'open'
    if sort_by is None:
        sort_by = 'date_desc'
    
    print(f"DEBUG: Filters - skill: {skill_filter}, priority: {repr(priority_filter)}, status: {repr(status_filter)}")
    db = get_session()
    try:
        # Build query
        query = db.query(Idea)
        
        # Apply filters
        if skill_filter:
            query = query.join(Idea.skills).filter(Skill.name == skill_filter)
        
        if priority_filter:
            query = query.filter(Idea.priority == PriorityLevel(priority_filter))
            
        if status_filter:
            query = query.filter(Idea.status == IdeaStatus(status_filter))
        
        # Apply sorting
        if sort_by == 'date_desc':
            query = query.order_by(Idea.date_submitted.desc())
        elif sort_by == 'date_asc':
            query = query.order_by(Idea.date_submitted.asc())
        elif sort_by == 'priority':
            # Custom ordering for priority
            priority_order = {'high': 1, 'medium': 2, 'low': 3}
            ideas = query.all()
            ideas.sort(key=lambda x: priority_order.get(x.priority.value, 999))
        elif sort_by == 'size':
            # Custom ordering for size
            size_order = {'small': 1, 'medium': 2, 'large': 3, 'extra_large': 4}
            ideas = query.all()
            ideas.sort(key=lambda x: size_order.get(x.size.value, 999))
        else:
            ideas = query.all()
            
        if sort_by not in ['priority', 'size']:
            ideas = query.all()
        
        print(f"DEBUG: Found {len(ideas)} ideas after filtering")
        
        # Create idea cards
        idea_cards = []
        for idea in ideas:
            # Get claim info
            claim = db.query(Claim).filter_by(idea_id=idea.id).order_by(Claim.claim_date.desc()).first()
            
            card = html.Div([
                # Status badge
                html.Div(
                    idea.status.value.upper(),
                    style={
                        'position': 'absolute',
                        'top': '10px',
                        'right': '10px',
                        'padding': '5px 10px',
                        'borderRadius': '5px',
                        'fontSize': '12px',
                        'fontWeight': 'bold',
                        'backgroundColor': '#28a745' if idea.status.value == 'open' else '#6c757d',
                        'color': 'white'
                    }
                ),
                
                # Title
                html.H3(idea.title, style={'marginBottom': '10px'}),
                
                # Metadata
                html.Div([
                    html.Span(f"Priority: {idea.priority.value.capitalize()}", style={
                        'color': PRIORITY_COLORS.get(idea.priority.value, '#000'),
                        'fontWeight': 'bold',
                        'marginRight': '20px'
                    }),
                    html.Span(f"Size: {SIZE_LABELS.get(idea.size.value, idea.size.value)}", style={'marginRight': '20px'}),
                    html.Span(f"Team: {idea.benefactor_team}")
                ], style={'marginBottom': '10px'}),
                
                # Skills
                html.Div([
                    html.Span(skill.name, style={
                        'backgroundColor': '#e9ecef',
                        'padding': '3px 8px',
                        'borderRadius': '3px',
                        'marginRight': '5px',
                        'fontSize': '14px'
                    }) for skill in idea.skills
                ], style={'marginBottom': '10px'}),
                
                # Description preview
                html.P(
                    idea.description[:150] + '...' if len(idea.description) > 150 else idea.description,
                    style={'marginBottom': '10px', 'color': '#6c757d'}
                ),
                
                # Reward if exists
                html.Div([
                    html.Strong("🎁 Reward: "),
                    html.Span(idea.reward)
                ], style={'marginBottom': '10px'}) if idea.reward else None,
                
                # Dates
                html.Div([
                    html.Span(f"Submitted: {idea.date_submitted.strftime('%b %d, %Y')}", style={'fontSize': '14px', 'color': '#6c757d'}),
                    html.Span(f" | Needed by: {idea.needed_by.strftime('%b %d, %Y')}" if idea.needed_by else "", style={'fontSize': '14px', 'color': '#6c757d'})
                ], style={'marginBottom': '10px'}),
                
                # Claim info if claimed
                html.Div([
                    html.Hr(),
                    html.Div([
                        html.Strong("Claimed by: "),
                        html.Span(f"{claim.claimer_name} ({claim.claimer_team})"),
                        html.Span(f" on {claim.claim_date.strftime('%b %d, %Y')}", style={'color': '#6c757d'})
                    ])
                ]) if claim else None,
                
                # View details link
                dcc.Link('View Details →', href=f'/idea/{idea.id}', style={
                    'color': '#007bff',
                    'textDecoration': 'none',
                    'fontWeight': 'bold'
                })
            ], style={
                'border': '1px solid #dee2e6',
                'borderRadius': '8px',
                'padding': '20px',
                'marginBottom': '20px',
                'position': 'relative',
                'backgroundColor': '#f8f9fa' if idea.status.value != 'open' else 'white',
                'cursor': 'pointer',
                'transition': 'all 0.3s ease'
            }, className='idea-card')
            
            idea_cards.append(card)
        
        if not idea_cards:
            return html.Div(
                'No ideas found matching your filters.',
                style={'textAlign': 'center', 'padding': '40px', 'color': '#6c757d'}
            )
        
        return idea_cards
        
    finally:
        db.close()