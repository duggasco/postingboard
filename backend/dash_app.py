import dash
from dash import Dash, html, dcc, Input, Output, State, callback, dash_table, ALL, MATCH
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd
from flask import Flask, session, request
from flask_session import Session
import os
from functools import wraps

from database import init_db, get_session
from models import Idea, Skill, Claim, IdeaStatus, PriorityLevel, IdeaSize
from config import Config

# Initialize Flask server
server = Flask(__name__)
server.config['SECRET_KEY'] = Config.SECRET_KEY or 'dev-secret-key'
server.config['SESSION_TYPE'] = 'filesystem'
Session(server)

# Initialize Dash app with Flask server
app = Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True
)

# Initialize database
init_db()

# Import pages to register their callbacks
from pages import home, submit, idea_detail, my_ideas, admin, admin_login, admin_dashboard, admin_ideas, admin_skills

# App layout with navigation
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='session-store', storage_type='session'),
    dcc.Store(id='admin-auth-store', storage_type='session'),
    
    # Navigation bar
    html.Div([
        html.Div([
            html.H1('Citizen Developer Posting Board', style={'margin': '0', 'color': 'white'}),
            html.Div([
                dcc.Link('All Ideas', href='/', className='nav-link'),
                dcc.Link('My Ideas', href='/my-ideas', className='nav-link'),
                dcc.Link('Submit Idea', href='/submit', className='nav-link'),
                dcc.Link('Admin', href='/admin', className='nav-link'),
            ], style={'display': 'flex', 'gap': '20px'})
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'padding': '20px',
            'backgroundColor': '#2c3e50',
            'marginBottom': '20px'
        })
    ]),
    
    # Page content
    html.Div(id='page-content')
])

# Page routing callback
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    print(f"DEBUG: Routing to {pathname}, is_admin: {session.get('is_admin')}")
    if pathname == '/':
        return home.layout
    elif pathname == '/submit':
        return submit.layout()
    elif pathname == '/my-ideas':
        return my_ideas.layout()
    elif pathname and pathname.startswith('/idea/'):
        idea_id = pathname.split('/')[-1]
        return idea_detail.layout(idea_id=idea_id)
    elif pathname == '/admin':
        return admin.layout
    elif pathname == '/admin/login':
        return admin_login.layout
    elif pathname == '/admin/dashboard':
        return admin_dashboard.layout()
    elif pathname == '/admin/ideas':
        return admin_ideas.layout()
    elif pathname == '/admin/skills':
        return admin_skills.layout()
    else:
        return html.Div('404 - Page not found')

# Admin authentication callback
@app.callback(
    Output('admin-auth-store', 'data'),
    Input('url', 'pathname'),
    State('admin-auth-store', 'data')
)
def check_admin_auth(pathname, auth_data):
    if pathname and pathname.startswith('/admin'):
        # Check if user is authenticated
        if not session.get('is_admin'):
            return {'authenticated': False, 'redirect': '/admin/login'}
    return auth_data or {}

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=5000)