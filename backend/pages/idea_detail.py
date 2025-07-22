from dash import html, dcc, callback, Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import datetime
from database import get_session
from models import Idea, Claim, IdeaStatus
from utils.email import send_claim_notification

def layout(idea_id=None):
    if not idea_id:
        return html.Div('Invalid idea ID')
    
    db = get_session()
    try:
        idea = db.query(Idea).filter_by(id=int(idea_id)).first()
        if not idea:
            return html.Div('Idea not found')
        
        # Get claims history
        claims = db.query(Claim).filter_by(idea_id=idea.id).order_by(Claim.claim_date.desc()).all()
        
        # Priority colors
        priority_colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#dc3545'
        }
        
        # Size labels
        size_labels = {
            'small': 'Small (1-2 days)',
            'medium': 'Medium (3-5 days)',
            'large': 'Large (1-2 weeks)',
            'extra_large': 'Extra Large (2+ weeks)'
        }
        
        return html.Div([
            # Back button
            dcc.Link('← Back to Ideas', href='/', style={
                'color': '#007bff',
                'textDecoration': 'none',
                'marginBottom': '20px',
                'display': 'inline-block'
            }),
            
            # Main content
            html.Div([
                # Header with status
                html.Div([
                    html.H1(idea.title, style={'flex': '1'}),
                    html.Div(
                        idea.status.value.upper(),
                        style={
                            'padding': '10px 20px',
                            'borderRadius': '5px',
                            'fontSize': '14px',
                            'fontWeight': 'bold',
                            'backgroundColor': '#28a745' if idea.status.value == 'open' else '#6c757d',
                            'color': 'white'
                        }
                    )
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '20px'}),
                
                # Metadata
                html.Div([
                    html.Div([
                        html.Strong('Priority: '),
                        html.Span(idea.priority.value.capitalize(), style={
                            'color': priority_colors.get(idea.priority.value, '#000'),
                            'fontWeight': 'bold'
                        })
                    ], style={'marginRight': '30px'}),
                    html.Div([
                        html.Strong('Size: '),
                        html.Span(size_labels.get(idea.size.value, idea.size.value))
                    ], style={'marginRight': '30px'}),
                    html.Div([
                        html.Strong('Team: '),
                        html.Span(idea.benefactor_team)
                    ])
                ], style={'display': 'flex', 'marginBottom': '20px'}),
                
                # Skills
                html.Div([
                    html.Strong('Required Skills: '),
                    html.Div([
                        html.Span(skill.name, style={
                            'backgroundColor': '#e9ecef',
                            'padding': '5px 10px',
                            'borderRadius': '3px',
                            'marginRight': '5px',
                            'display': 'inline-block',
                            'marginTop': '5px'
                        }) for skill in idea.skills
                    ])
                ], style={'marginBottom': '20px'}),
                
                # Dates
                html.Div([
                    html.Div([
                        html.Strong('Submitted: '),
                        html.Span(idea.date_submitted.strftime('%B %d, %Y'))
                    ], style={'marginRight': '30px'}),
                    html.Div([
                        html.Strong('Needed by: '),
                        html.Span(idea.needed_by.strftime('%B %d, %Y') if idea.needed_by else 'Not specified')
                    ])
                ], style={'display': 'flex', 'marginBottom': '20px'}),
                
                # Reward if exists
                html.Div([
                    html.H3('🎁 Reward'),
                    html.P(idea.reward, style={
                        'backgroundColor': '#fff3cd',
                        'padding': '15px',
                        'borderRadius': '5px',
                        'border': '1px solid #ffeaa7'
                    })
                ], style={'marginBottom': '20px'}) if idea.reward else None,
                
                # Description
                html.Div([
                    html.H3('Description'),
                    html.P(idea.description, style={
                        'whiteSpace': 'pre-wrap',
                        'backgroundColor': '#f8f9fa',
                        'padding': '15px',
                        'borderRadius': '5px'
                    })
                ], style={'marginBottom': '30px'}),
                
                # Claims history
                html.Div([
                    html.H3('Claim History'),
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Strong(f"{claim.claimer_name} ({claim.claimer_team})"),
                                html.Span(f" - {claim.claim_date.strftime('%B %d, %Y')}", 
                                         style={'color': '#6c757d'})
                            ]),
                            html.Div([
                                html.Strong('Skills: '),
                                html.Span(claim.claimer_skills)
                            ], style={'fontSize': '14px', 'marginTop': '5px'})
                        ], style={
                            'padding': '10px',
                            'backgroundColor': '#f8f9fa',
                            'marginBottom': '10px',
                            'borderRadius': '5px'
                        }) for claim in claims
                    ]) if claims else html.P('No claims yet', style={'color': '#6c757d'})
                ], style={'marginBottom': '30px'}),
                
                # Claim button for open ideas
                html.Div([
                    html.Button('Claim This Idea', id='open-claim-modal', n_clicks=0, style={
                        'padding': '10px 30px',
                        'backgroundColor': '#007bff',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '4px',
                        'cursor': 'pointer',
                        'fontSize': '16px',
                        'fontWeight': 'bold'
                    })
                ], style={'textAlign': 'center'}) if idea.status.value == 'open' else None
                
            ], style={'maxWidth': '800px', 'margin': '0 auto', 'padding': '20px'}),
            
            # Claim modal
            html.Div([
                html.Div([
                    html.Div([
                        html.H2('Claim This Idea', style={'marginBottom': '20px'}),
                        html.Button('×', id='close-claim-modal', n_clicks=0, style={
                            'position': 'absolute',
                            'top': '10px',
                            'right': '15px',
                            'border': 'none',
                            'background': 'none',
                            'fontSize': '30px',
                            'cursor': 'pointer'
                        })
                    ], style={'position': 'relative'}),
                    
                    html.Div([
                        html.Label('Your Name *'),
                        dcc.Input(id='claimer-name', type='text', style={
                            'width': '100%',
                            'padding': '8px',
                            'marginBottom': '15px'
                        })
                    ]),
                    
                    html.Div([
                        html.Label('Your Email *'),
                        dcc.Input(id='claimer-email', type='email', style={
                            'width': '100%',
                            'padding': '8px',
                            'marginBottom': '15px'
                        })
                    ]),
                    
                    html.Div([
                        html.Label('Your Team *'),
                        dcc.Input(id='claimer-team', type='text', style={
                            'width': '100%',
                            'padding': '8px',
                            'marginBottom': '15px'
                        })
                    ]),
                    
                    html.Div([
                        html.Label('Your Skills *'),
                        dcc.Textarea(id='claimer-skills', placeholder='List your relevant skills', style={
                            'width': '100%',
                            'padding': '8px',
                            'marginBottom': '15px',
                            'minHeight': '80px'
                        })
                    ]),
                    
                    html.Div([
                        html.Button('Submit Claim', id='submit-claim', n_clicks=0, style={
                            'padding': '10px 30px',
                            'backgroundColor': '#28a745',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '4px',
                            'cursor': 'pointer',
                            'marginRight': '10px'
                        }),
                        html.Button('Cancel', id='cancel-claim', n_clicks=0, style={
                            'padding': '10px 30px',
                            'backgroundColor': '#6c757d',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '4px',
                            'cursor': 'pointer'
                        })
                    ], style={'textAlign': 'center'}),
                    
                    html.Div(id='claim-feedback', style={'marginTop': '15px', 'textAlign': 'center'})
                    
                ], style={
                    'backgroundColor': 'white',
                    'padding': '30px',
                    'borderRadius': '8px',
                    'width': '500px',
                    'maxWidth': '90%',
                    'position': 'relative'
                })
            ], id='claim-modal', style={
                'display': 'none',
                'position': 'fixed',
                'top': '0',
                'left': '0',
                'width': '100%',
                'height': '100%',
                'backgroundColor': 'rgba(0,0,0,0.5)',
                'alignItems': 'center',
                'justifyContent': 'center',
                'zIndex': '1000'
            }),
            
            # Store idea ID
            dcc.Store(id='current-idea-id', data=idea_id)
        ])
        
    finally:
        db.close()

# Modal visibility callbacks
@callback(
    Output('claim-modal', 'style'),
    [Input('open-claim-modal', 'n_clicks'),
     Input('close-claim-modal', 'n_clicks'),
     Input('cancel-claim', 'n_clicks'),
     Input('submit-claim', 'n_clicks')],
    State('claim-modal', 'style')
)
def toggle_modal(open_clicks, close_clicks, cancel_clicks, submit_clicks, current_style):
    from dash import callback_context
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'open-claim-modal':
        return {**current_style, 'display': 'flex'}
    else:
        return {**current_style, 'display': 'none'}

# Handle claim submission
@callback(
    Output('claim-feedback', 'children'),
    Input('submit-claim', 'n_clicks'),
    [State('current-idea-id', 'data'),
     State('claimer-name', 'value'),
     State('claimer-email', 'value'),
     State('claimer-team', 'value'),
     State('claimer-skills', 'value')]
)
def submit_claim(n_clicks, idea_id, name, email, team, skills):
    if n_clicks == 0:
        raise PreventUpdate
    
    if not all([name, email, team, skills]):
        return html.Div('Please fill in all fields', style={'color': 'red'})
    
    db = get_session()
    try:
        idea = db.query(Idea).filter_by(id=int(idea_id)).first()
        if not idea:
            return html.Div('Idea not found', style={'color': 'red'})
        
        if idea.status != IdeaStatus.OPEN:
            return html.Div('This idea has already been claimed', style={'color': 'red'})
        
        # Create claim
        claim = Claim(
            idea_id=idea.id,
            claimer_name=name,
            claimer_email=email,
            claimer_skills=skills,
            claimer_team=team
        )
        db.add(claim)
        
        # Update idea status
        idea.status = IdeaStatus.CLAIMED
        
        db.commit()
        
        # Send email notification (don't let failures break the claim)
        try:
            send_claim_notification(idea, claim)
        except:
            pass
        
        return html.Div([
            html.Div('✓ Idea claimed successfully!', style={'color': 'green', 'fontWeight': 'bold'}),
            html.Div('Refreshing page...', style={'fontSize': '14px', 'marginTop': '5px'})
        ])
        
    except Exception as e:
        db.rollback()
        return html.Div(f'Error: {str(e)}', style={'color': 'red'})
    finally:
        db.close()