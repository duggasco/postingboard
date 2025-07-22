from dash import html, dcc, callback, Input, Output
from datetime import datetime
from flask import session
from database import get_session
from models import Idea, IdeaStatus, PriorityLevel

def layout():
    db = get_session()
    try:
        # Get user's email and submitted ideas from session
        user_email = session.get('user_email', '')
        submitted_idea_ids = session.get('submitted_ideas', [])
        
        # Query ideas by session IDs or email
        ideas_query = db.query(Idea).filter(
            (Idea.id.in_(submitted_idea_ids) if submitted_idea_ids else False) |
            (Idea.email == user_email if user_email else False)
        ).order_by(Idea.date_submitted.desc())
        
        my_ideas = ideas_query.all()
        
        # If no ideas found
        if not my_ideas:
            return html.Div([
                html.H2('My Ideas', style={'textAlign': 'center', 'marginBottom': '30px'}),
                html.Div([
                    html.P("You haven't submitted any ideas yet.", style={'textAlign': 'center', 'fontSize': '18px'}),
                    html.Div([
                        dcc.Link('Submit your first idea', href='/submit', style={
                            'backgroundColor': '#28a745',
                            'color': 'white',
                            'padding': '10px 20px',
                            'borderRadius': '4px',
                            'textDecoration': 'none',
                            'display': 'inline-block'
                        })
                    ], style={'textAlign': 'center', 'marginTop': '20px'})
                ])
            ])
        
        # Build idea cards
        idea_cards = []
        for idea in my_ideas:
            # Status color mapping
            status_color = {
                IdeaStatus.OPEN: '#28a745',
                IdeaStatus.CLAIMED: '#ffc107',
                IdeaStatus.COMPLETE: '#6c757d'
            }.get(idea.status, '#6c757d')
            
            # Priority color mapping
            priority_color = {
                PriorityLevel.high: '#dc3545',
                PriorityLevel.medium: '#ffc107',
                PriorityLevel.low: '#28a745'
            }.get(idea.priority, '#6c757d')
            
            # Calculate days until needed
            days_until = None
            if idea.needed_by:
                days_until = (idea.needed_by - datetime.utcnow().date()).days
            
            card = html.Div([
                # Header with title and status
                html.Div([
                    html.H3([
                        dcc.Link(idea.title, href=f'/idea/{idea.id}', style={
                            'color': '#2c3e50',
                            'textDecoration': 'none'
                        })
                    ], style={'margin': '0', 'flex': '1'}),
                    html.Span(idea.status.value.upper(), style={
                        'backgroundColor': status_color,
                        'color': 'white',
                        'padding': '4px 12px',
                        'borderRadius': '4px',
                        'fontSize': '12px',
                        'fontWeight': 'bold'
                    })
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
                
                # Metadata
                html.Div([
                    html.Span([
                        html.Strong('Priority: '),
                        html.Span(idea.priority.value, style={'color': priority_color, 'fontWeight': 'bold'})
                    ], style={'marginRight': '20px'}),
                    html.Span([
                        html.Strong('Size: '),
                        idea.size.value.replace('_', ' ')
                    ], style={'marginRight': '20px'}),
                    html.Span([
                        html.Strong('Team: '),
                        idea.benefactor_team
                    ])
                ], style={'marginBottom': '10px', 'color': '#666'}),
                
                # Description preview
                html.P(
                    idea.description[:200] + '...' if len(idea.description) > 200 else idea.description,
                    style={'marginBottom': '10px', 'color': '#444'}
                ),
                
                # Skills
                html.Div([
                    html.Span(skill.name, style={
                        'backgroundColor': '#e9ecef',
                        'padding': '4px 8px',
                        'borderRadius': '3px',
                        'marginRight': '5px',
                        'fontSize': '12px',
                        'display': 'inline-block',
                        'marginBottom': '5px'
                    }) for skill in idea.skills
                ], style={'marginBottom': '10px'}),
                
                # Footer with dates and claims
                html.Div([
                    html.Span([
                        html.Strong('Submitted: '),
                        idea.date_submitted.strftime('%B %d, %Y')
                    ], style={'marginRight': '20px', 'fontSize': '12px', 'color': '#666'}),
                    html.Span([
                        html.Strong('Claims: '),
                        str(len(idea.claims))
                    ], style={'marginRight': '20px', 'fontSize': '12px', 'color': '#666'}),
                    html.Span([
                        html.Strong('Needed by: '),
                        f"{idea.needed_by.strftime('%B %d')} ({days_until} days)" if idea.needed_by and days_until >= 0 else 'No deadline'
                    ], style={'fontSize': '12px', 'color': '#dc3545' if days_until and days_until < 7 else '#666'})
                ], style={'display': 'flex', 'flexWrap': 'wrap'})
            ], style={
                'border': '1px solid #ddd',
                'borderRadius': '8px',
                'padding': '20px',
                'marginBottom': '20px',
                'backgroundColor': 'white',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'transition': 'box-shadow 0.3s',
                'cursor': 'pointer'
            }, className='idea-card')
            
            idea_cards.append(card)
        
        return html.Div([
            html.H2(f'My Ideas ({len(my_ideas)})', style={'textAlign': 'center', 'marginBottom': '30px'}),
            
            # Summary stats
            html.Div([
                html.Div([
                    html.H4(str(len([i for i in my_ideas if i.status == IdeaStatus.OPEN])), 
                            style={'margin': '0', 'color': '#28a745'}),
                    html.P('Open', style={'margin': '0', 'color': '#666'})
                ], style={'textAlign': 'center', 'flex': '1'}),
                html.Div([
                    html.H4(str(len([i for i in my_ideas if i.status == IdeaStatus.CLAIMED])), 
                            style={'margin': '0', 'color': '#ffc107'}),
                    html.P('Claimed', style={'margin': '0', 'color': '#666'})
                ], style={'textAlign': 'center', 'flex': '1'}),
                html.Div([
                    html.H4(str(len([i for i in my_ideas if i.status == IdeaStatus.COMPLETE])), 
                            style={'margin': '0', 'color': '#6c757d'}),
                    html.P('Complete', style={'margin': '0', 'color': '#666'})
                ], style={'textAlign': 'center', 'flex': '1'})
            ], style={
                'display': 'flex',
                'justifyContent': 'space-around',
                'marginBottom': '30px',
                'padding': '20px',
                'backgroundColor': '#f8f9fa',
                'borderRadius': '8px'
            }),
            
            # Ideas list
            html.Div(idea_cards, style={'maxWidth': '800px', 'margin': '0 auto'})
        ])
        
    finally:
        db.close()

# Auto-refresh every 30 seconds to update status
layout_with_refresh = html.Div([
    dcc.Interval(id='my-ideas-refresh', interval=30000),
    html.Div(id='my-ideas-content')
])

@callback(
    Output('my-ideas-content', 'children'),
    Input('my-ideas-refresh', 'n_intervals')
)
def refresh_my_ideas(_):
    return layout()