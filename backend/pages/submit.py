from dash import html, dcc, callback, Input, Output, State, ALL, callback_context
from dash.exceptions import PreventUpdate
from datetime import datetime, date
import json
from flask import session
from database import get_session
from models import Idea, Skill, IdeaStatus, PriorityLevel, IdeaSize


def layout():
    # Get user's email from session if available
    user_email = session.get('user_email', '')
    
    return html.Div([
    html.H2('Submit a New Idea', style={'textAlign': 'center', 'marginBottom': '30px'}),
    
    html.Div([
        # Title
        html.Div([
            html.Label('Title *', style={'fontWeight': 'bold'}),
            dcc.Input(
                id='title-input',
                type='text',
                placeholder='Enter idea title',
                style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}
            )
        ]),
        
        # Description
        html.Div([
            html.Label('Description *', style={'fontWeight': 'bold'}),
            dcc.Textarea(
                id='description-input',
                placeholder='Describe your idea in detail',
                style={'width': '100%', 'minHeight': '100px', 'padding': '8px', 'marginBottom': '15px'}
            )
        ]),
        
        # Skills section
        html.Div([
            html.Label('Required Skills *', style={'fontWeight': 'bold'}),
            html.Div([
                # Predefined skills dropdown
                html.Div([
                    dcc.Dropdown(
                        id='skill-dropdown',
                        options=[],
                        placeholder='Select from existing skills',
                        value='',
                        clearable=True
                    )
                ], style={'flex': '1', 'marginRight': '10px'}),
                
                # Custom skill input
                html.Div([
                    dcc.Input(
                        id='custom-skill-input',
                        type='text',
                        placeholder='Or type a custom skill',
                        style={'width': '100%', 'padding': '8px'}
                    )
                ], style={'flex': '1', 'marginRight': '10px'}),
                
                # Add button
                html.Button('Add', id='add-skill-btn', n_clicks=0, style={
                    'padding': '8px 16px',
                    'backgroundColor': '#007bff',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '4px',
                    'cursor': 'pointer'
                })
            ], style={'display': 'flex', 'marginBottom': '10px'}),
            
            # Selected skills display
            html.Div(id='selected-skills-container', children=[], style={'marginBottom': '15px'})
        ]),
        
        # Priority and Size
        html.Div([
            html.Div([
                html.Label('Priority *', style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='priority-input',
                    options=[
                        {'label': 'Low', 'value': 'low'},
                        {'label': 'Medium', 'value': 'medium'},
                        {'label': 'High', 'value': 'high'}
                    ],
                    placeholder='Select priority',
                    style={'marginBottom': '15px'}
                )
            ], style={'flex': '1', 'marginRight': '20px'}),
            
            html.Div([
                html.Label('Size *', style={'fontWeight': 'bold'}),
                dcc.Dropdown(
                    id='size-input',
                    options=[
                        {'label': 'Small (1-2 days)', 'value': 'small'},
                        {'label': 'Medium (3-5 days)', 'value': 'medium'},
                        {'label': 'Large (1-2 weeks)', 'value': 'large'},
                        {'label': 'Extra Large (2+ weeks)', 'value': 'extra_large'}
                    ],
                    placeholder='Select size',
                    style={'marginBottom': '15px'}
                )
            ], style={'flex': '1'})
        ], style={'display': 'flex'}),
        
        # Benefactor Team and Email
        html.Div([
            html.Div([
                html.Label('Your Team *', style={'fontWeight': 'bold'}),
                dcc.Input(
                    id='team-input',
                    type='text',
                    placeholder='Your team name',
                    style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}
                )
            ], style={'flex': '1', 'marginRight': '20px'}),
            
            html.Div([
                html.Label('Your Email *', style={'fontWeight': 'bold'}),
                dcc.Input(
                    id='email-input',
                    type='email',
                    placeholder='your.email@example.com',
                    value=user_email,
                    style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}
                )
            ], style={'flex': '1'})
        ], style={'display': 'flex'}),
        
        # Needed By and Reward
        html.Div([
            html.Div([
                html.Label('Needed By', style={'fontWeight': 'bold'}),
                dcc.DatePickerSingle(
                    id='needed-by-input',
                    min_date_allowed=date.today(),
                    placeholder='Select date',
                    style={'marginBottom': '15px'}
                )
            ], style={'flex': '1', 'marginRight': '20px'}),
            
            html.Div([
                html.Label('Reward', style={'fontWeight': 'bold'}),
                dcc.Input(
                    id='reward-input',
                    type='text',
                    placeholder='BLK swag, lunch, etc.',
                    style={'width': '100%', 'padding': '8px', 'marginBottom': '15px'}
                )
            ], style={'flex': '1'})
        ], style={'display': 'flex'}),
        
        # Submit button
        html.Div([
            html.Button('Submit Idea', id='submit-btn', n_clicks=0, style={
                'padding': '10px 30px',
                'backgroundColor': '#28a745',
                'color': 'white',
                'border': 'none',
                'borderRadius': '4px',
                'cursor': 'pointer',
                'fontSize': '16px',
                'fontWeight': 'bold'
            })
        ], style={'textAlign': 'center', 'marginTop': '20px'}),
        
        # Feedback message
        html.Div(id='submit-feedback', style={'marginTop': '20px', 'textAlign': 'center'})
        
        ], style={'maxWidth': '800px', 'margin': '0 auto', 'padding': '20px'}),
        
        # Hidden store for selected skills
        dcc.Store(id='skills-store', data=[])
    ])

# Update skill dropdown options
@callback(
    Output('skill-dropdown', 'options'),
    Input('skill-dropdown', 'id'),
    State('skills-store', 'data')
)
def update_skill_options(_, selected_skills):
    db = get_session()
    try:
        skills = db.query(Skill).order_by(Skill.name).all()
        # Filter out already selected skills
        options = [
            {'label': skill.name, 'value': skill.name} 
            for skill in skills 
            if skill.name not in selected_skills
        ]
        return options
    finally:
        db.close()

# Handle skill addition
@callback(
    [Output('skills-store', 'data'),
     Output('selected-skills-container', 'children'),
     Output('skill-dropdown', 'value'),
     Output('custom-skill-input', 'value')],
    [Input('add-skill-btn', 'n_clicks'),
     Input({'type': 'remove-skill', 'index': ALL}, 'n_clicks')],
    [State('skill-dropdown', 'value'),
     State('custom-skill-input', 'value'),
     State('skills-store', 'data')]
)
def manage_skills(add_clicks, remove_clicks, dropdown_skill, custom_skill, current_skills):
    ctx = callback_context
    
    if not ctx.triggered:
        return current_skills, [], '', ''
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    # Handle skill addition
    if 'add-skill-btn' in trigger_id and (dropdown_skill or custom_skill):
        skill_to_add = dropdown_skill or custom_skill
        if skill_to_add and skill_to_add not in current_skills:
            current_skills.append(skill_to_add)
    
    # Handle skill removal
    elif 'remove-skill' in trigger_id:
        # Extract the skill index from the trigger
        import json
        for i, click in enumerate(remove_clicks):
            if click:
                # Find which button was clicked
                triggered_id = json.loads(trigger_id.split('.')[0])
                if triggered_id['index'] < len(current_skills):
                    current_skills.pop(triggered_id['index'])
                break
    
    # Create skill tags display
    skill_tags = []
    for i, skill in enumerate(current_skills):
        skill_tags.append(
            html.Span([
                skill,
                html.Button('×', id={'type': 'remove-skill', 'index': i}, 
                           style={
                               'marginLeft': '5px',
                               'border': 'none',
                               'background': 'none',
                               'cursor': 'pointer',
                               'fontWeight': 'bold'
                           })
            ], style={
                'backgroundColor': '#007bff',
                'color': 'white',
                'padding': '5px 10px',
                'borderRadius': '3px',
                'marginRight': '5px',
                'marginBottom': '5px',
                'display': 'inline-block'
            })
        )
    
    return current_skills, skill_tags, '', ''

# Handle form submission
@callback(
    Output('submit-feedback', 'children'),
    Input('submit-btn', 'n_clicks'),
    [State('title-input', 'value'),
     State('description-input', 'value'),
     State('skills-store', 'data'),
     State('priority-input', 'value'),
     State('size-input', 'value'),
     State('team-input', 'value'),
     State('email-input', 'value'),
     State('needed-by-input', 'date'),
     State('reward-input', 'value')]
)
def submit_idea(n_clicks, title, description, skills, priority, size, team, email, needed_by, reward):
    if n_clicks == 0:
        raise PreventUpdate
    
    # Validate required fields
    if not all([title, description, skills, priority, size, team, email]):
        return html.Div('Please fill in all required fields.', style={'color': 'red'})
    
    db = get_session()
    try:
        # Create new idea
        idea = Idea(
            title=title,
            description=description,
            priority=PriorityLevel(priority),
            size=IdeaSize(size),
            status=IdeaStatus.OPEN,
            email=email,
            benefactor_team=team,
            needed_by=datetime.strptime(needed_by, '%Y-%m-%d').date() if needed_by else None,
            reward=reward or None
        )
        
        # Add skills
        for skill_name in skills:
            # Check if skill exists
            skill = db.query(Skill).filter_by(name=skill_name).first()
            if not skill:
                # Create new skill
                skill = Skill(name=skill_name)
                db.add(skill)
            idea.skills.append(skill)
        
        db.add(idea)
        db.commit()
        
        # Track submitted idea in session
        if 'submitted_ideas' not in session:
            session['submitted_ideas'] = []
        session['submitted_ideas'].append(idea.id)
        
        # Store user's email for consistency
        session['user_email'] = email
        
        # Ensure session is saved
        session.modified = True
        
        return html.Div([
            html.Div('✓ Idea submitted successfully!', style={
                'color': 'green',
                'fontWeight': 'bold',
                'marginBottom': '10px'
            }),
            dcc.Link('View your idea', href=f'/idea/{idea.id}', style={'color': '#007bff'}),
            ' or ',
            dcc.Link('submit another', href='/submit', refresh=True, style={'color': '#007bff'})
        ])
        
    except Exception as e:
        db.rollback()
        return html.Div(f'Error submitting idea: {str(e)}', style={'color': 'red'})
    finally:
        db.close()