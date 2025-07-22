from dash import html, dcc, callback, Input, Output, State, ALL, callback_context
from dash.exceptions import PreventUpdate
from flask import session
from database import get_session
from models import Skill


def layout():
    # Check authentication
    if not session.get('is_admin'):
        return dcc.Location(href='/admin/login', id='redirect-login')
    
    return html.Div([
        html.Div([
            html.H2('Manage Skills', style={'flex': '1'}),
            dcc.Link('← Back to Dashboard', href='/admin/dashboard', style={
                'color': '#007bff',
                'textDecoration': 'none'
            })
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '30px'}),
        
        # Add new skill
        html.Div([
            html.H3('Add New Skill'),
            html.Div([
                dcc.Input(
                    id='new-skill-input',
                    type='text',
                    placeholder='Enter skill name',
                    style={'padding': '8px', 'marginRight': '10px', 'width': '300px'}
                ),
                html.Button('Add Skill', id='add-skill-btn', n_clicks=0, style={
                    'padding': '8px 20px',
                    'backgroundColor': '#28a745',
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '4px',
                    'cursor': 'pointer'
                })
            ]),
            html.Div(id='add-skill-feedback', style={'marginTop': '10px'})
        ], style={
            'backgroundColor': '#f8f9fa',
            'padding': '20px',
            'borderRadius': '8px',
            'marginBottom': '30px'
        }),
        
        # Existing skills
        html.H3('Existing Skills'),
        html.Div(id='skills-list-container'),
        
        # General feedback
        html.Div(id='skills-feedback', style={'marginTop': '20px'}),
        
        # Refresh interval
        dcc.Interval(id='skills-refresh', interval=2000)
    ], style={'maxWidth': '800px', 'margin': '0 auto', 'padding': '20px'})

@callback(
    Output('skills-list-container', 'children'),
    Input('skills-refresh', 'n_intervals')
)
def refresh_skills_list(n):
    db = get_session()
    try:
        skills = db.query(Skill).order_by(Skill.name).all()
        
        skill_items = []
        for skill in skills:
            skill_items.append(
                html.Div([
                    dcc.Input(
                        id={'type': 'skill-name', 'index': skill.id},
                        value=skill.name,
                        style={'padding': '8px', 'marginRight': '10px', 'flex': '1'}
                    ),
                    html.Button('Save', id={'type': 'save-skill', 'index': skill.id}, 
                               n_clicks=0, style={
                        'padding': '8px 15px',
                        'backgroundColor': '#007bff',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '4px',
                        'cursor': 'pointer',
                        'marginRight': '5px'
                    }),
                    html.Button('Delete', id={'type': 'delete-skill', 'index': skill.id}, 
                               n_clicks=0, style={
                        'padding': '8px 15px',
                        'backgroundColor': '#dc3545',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '4px',
                        'cursor': 'pointer'
                    })
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginBottom': '10px',
                    'padding': '10px',
                    'backgroundColor': '#f8f9fa',
                    'borderRadius': '5px'
                })
            )
        
        return skill_items
    finally:
        db.close()

# Add new skill
@callback(
    [Output('add-skill-feedback', 'children'),
     Output('new-skill-input', 'value')],
    Input('add-skill-btn', 'n_clicks'),
    State('new-skill-input', 'value')
)
def add_new_skill(n_clicks, skill_name):
    if n_clicks == 0 or not skill_name:
        raise PreventUpdate
    
    db = get_session()
    try:
        # Check if skill already exists
        existing = db.query(Skill).filter_by(name=skill_name).first()
        if existing:
            return [html.Div('Skill already exists', style={'color': 'red'}), skill_name]
        
        # Add new skill
        skill = Skill(name=skill_name)
        db.add(skill)
        db.commit()
        
        return [html.Div('✓ Skill added successfully', style={'color': 'green'}), '']
        
    except Exception as e:
        db.rollback()
        return [html.Div(f'Error: {str(e)}', style={'color': 'red'}), skill_name]
    finally:
        db.close()

# Handle skill updates and deletions
@callback(
    Output('skills-feedback', 'children'),
    [Input({'type': 'save-skill', 'index': ALL}, 'n_clicks'),
     Input({'type': 'delete-skill', 'index': ALL}, 'n_clicks')],
    [State({'type': 'skill-name', 'index': ALL}, 'value')]
)
def handle_skill_actions(save_clicks, delete_clicks, skill_names):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    trigger = ctx.triggered[0]
    prop_id = trigger['prop_id']
    
    # Parse the action
    import json
    button_info = json.loads(prop_id.split('.')[0])
    skill_id = button_info['index']
    action_type = button_info['type']
    
    db = get_session()
    try:
        if action_type == 'save-skill':
            # Find which button was clicked
            for i, clicks in enumerate(save_clicks):
                if clicks and clicks > 0:
                    skill = db.query(Skill).filter_by(id=skill_id).first()
                    if skill and i < len(skill_names):
                        skill.name = skill_names[i]
                        db.commit()
                        return html.Div('✓ Skill updated successfully', style={'color': 'green'})
        
        elif action_type == 'delete-skill':
            skill = db.query(Skill).filter_by(id=skill_id).first()
            if skill:
                # Check if skill is in use
                if skill.ideas:
                    return html.Div('Cannot delete skill that is in use', style={'color': 'red'})
                
                db.delete(skill)
                db.commit()
                return html.Div('✓ Skill deleted successfully', style={'color': 'green'})
        
        raise PreventUpdate
        
    except Exception as e:
        db.rollback()
        return html.Div(f'Error: {str(e)}', style={'color': 'red'})
    finally:
        db.close()