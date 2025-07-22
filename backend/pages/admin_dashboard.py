from dash import html, dcc, callback, Input, Output
from dash.exceptions import PreventUpdate
from flask import session, redirect
from database import get_session
from models import Idea, Skill, IdeaStatus
import plotly.graph_objs as go


def layout():
    # Check authentication
    if not session.get('is_admin'):
        return dcc.Location(href='/admin/login', id='redirect-login')
    
    db = get_session()
    try:
        # Get statistics
        total_ideas = db.query(Idea).count()
        open_ideas = db.query(Idea).filter_by(status=IdeaStatus.OPEN).count()
        claimed_ideas = db.query(Idea).filter_by(status=IdeaStatus.CLAIMED).count()
        completed_ideas = db.query(Idea).filter_by(status=IdeaStatus.COMPLETE).count()
        total_skills = db.query(Skill).count()
        
        # Create pie chart for idea status
        status_fig = go.Figure(data=[go.Pie(
            labels=['Open', 'Claimed', 'Complete'],
            values=[open_ideas, claimed_ideas, completed_ideas],
            hole=.3
        )])
        status_fig.update_layout(
            title='Idea Status Distribution',
            height=300
        )
        
        return html.Div([
            html.H2('Admin Dashboard', style={'marginBottom': '30px'}),
            
            # Navigation
            html.Div([
                dcc.Link('Manage Ideas', href='/admin/ideas', className='admin-nav-link'),
                dcc.Link('Manage Skills', href='/admin/skills', className='admin-nav-link'),
                html.A('Logout', href='#', id='admin-logout', className='admin-nav-link', 
                       style={'float': 'right', 'color': '#dc3545'})
            ], style={'marginBottom': '30px'}),
            
            # Statistics cards
            html.Div([
                html.Div([
                    html.H3(str(total_ideas)),
                    html.P('Total Ideas')
                ], className='stat-card'),
                
                html.Div([
                    html.H3(str(open_ideas)),
                    html.P('Open Ideas')
                ], className='stat-card', style={'backgroundColor': '#d4edda'}),
                
                html.Div([
                    html.H3(str(claimed_ideas)),
                    html.P('Claimed Ideas')
                ], className='stat-card', style={'backgroundColor': '#fff3cd'}),
                
                html.Div([
                    html.H3(str(completed_ideas)),
                    html.P('Completed Ideas')
                ], className='stat-card', style={'backgroundColor': '#d1ecf1'}),
                
                html.Div([
                    html.H3(str(total_skills)),
                    html.P('Total Skills')
                ], className='stat-card'),
            ], style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(auto-fit, minmax(200px, 1fr))',
                'gap': '20px',
                'marginBottom': '30px'
            }),
            
            # Chart
            dcc.Graph(figure=status_fig)
            
        ], style={'maxWidth': '1200px', 'margin': '0 auto', 'padding': '20px'})
        
    finally:
        db.close()

# Logout callback
@callback(
    Output('url', 'pathname', allow_duplicate=True),
    Input('admin-logout', 'n_clicks'),
    prevent_initial_call=True
)
def handle_logout(n_clicks):
    if n_clicks:
        session.pop('is_admin', None)
        return '/admin/login'
    raise PreventUpdate