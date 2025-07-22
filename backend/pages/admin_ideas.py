from dash import html, dcc, callback, Input, Output, State, dash_table, ALL
from dash.exceptions import PreventUpdate
from flask import session
from database import get_session
from models import Idea, IdeaStatus, PriorityLevel, IdeaSize
import pandas as pd


def layout():
    # Check authentication
    if not session.get('is_admin'):
        return dcc.Location(href='/admin/login', id='redirect-login')
    
    return html.Div([
        html.Div([
            html.H2('Manage Ideas', style={'flex': '1'}),
            dcc.Link('← Back to Dashboard', href='/admin/dashboard', style={
                'color': '#007bff',
                'textDecoration': 'none'
            })
        ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '30px'}),
        
        # Ideas table container
        html.Div(id='ideas-table-container'),
        
        # Refresh interval
        dcc.Interval(id='ideas-refresh', interval=5000),
        
        # Feedback message
        html.Div(id='admin-feedback', style={'marginTop': '20px'})
    ], style={'maxWidth': '1400px', 'margin': '0 auto', 'padding': '20px'})

@callback(
    Output('ideas-table-container', 'children'),
    Input('ideas-refresh', 'n_intervals')
)
def refresh_ideas_table(n):
    db = get_session()
    try:
        ideas = db.query(Idea).order_by(Idea.date_submitted.desc()).all()
        
        # Convert to dataframe for easier display
        data = []
        for idea in ideas:
            data.append({
                'id': idea.id,
                'title': idea.title,
                'team': idea.benefactor_team,
                'priority': idea.priority.value,
                'size': idea.size.value,
                'status': idea.status.value,
                'skills': ', '.join([s.name for s in idea.skills]),
                'submitted': idea.date_submitted.strftime('%Y-%m-%d'),
                'email': idea.email
            })
        
        df = pd.DataFrame(data)
        
        return dash_table.DataTable(
            id='ideas-table',
            columns=[
                {'name': 'ID', 'id': 'id', 'editable': False},
                {'name': 'Title', 'id': 'title', 'editable': True},
                {'name': 'Team', 'id': 'team', 'editable': True},
                {'name': 'Priority', 'id': 'priority', 'editable': True, 'presentation': 'dropdown'},
                {'name': 'Size', 'id': 'size', 'editable': True, 'presentation': 'dropdown'},
                {'name': 'Status', 'id': 'status', 'editable': True, 'presentation': 'dropdown'},
                {'name': 'Skills', 'id': 'skills', 'editable': True},
                {'name': 'Submitted', 'id': 'submitted', 'editable': False},
                {'name': 'Email', 'id': 'email', 'editable': True}
            ],
            data=df.to_dict('records'),
            editable=True,
            row_deletable=True,
            dropdown={
                'priority': {
                    'options': [
                        {'label': 'Low', 'value': 'low'},
                        {'label': 'Medium', 'value': 'medium'},
                        {'label': 'High', 'value': 'high'}
                    ]
                },
                'size': {
                    'options': [
                        {'label': 'Small', 'value': 'small'},
                        {'label': 'Medium', 'value': 'medium'},
                        {'label': 'Large', 'value': 'large'},
                        {'label': 'Extra Large', 'value': 'extra_large'}
                    ]
                },
                'status': {
                    'options': [
                        {'label': 'Open', 'value': 'open'},
                        {'label': 'Claimed', 'value': 'claimed'},
                        {'label': 'Complete', 'value': 'complete'}
                    ]
                }
            },
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            style_data_conditional=[
                {
                    'if': {'column_id': 'status', 'filter_query': '{status} = "open"'},
                    'backgroundColor': '#d4edda',
                    'color': 'black',
                },
                {
                    'if': {'column_id': 'status', 'filter_query': '{status} = "claimed"'},
                    'backgroundColor': '#fff3cd',
                    'color': 'black',
                },
                {
                    'if': {'column_id': 'status', 'filter_query': '{status} = "complete"'},
                    'backgroundColor': '#d1ecf1',
                    'color': 'black',
                }
            ],
            page_size=20,
            style_table={'overflowX': 'auto'}
        )
    finally:
        db.close()

# Handle edits and deletions
@callback(
    Output('admin-feedback', 'children'),
    [Input('ideas-table', 'data_timestamp'),
     Input('ideas-table', 'data_previous')],
    [State('ideas-table', 'data')]
)
def handle_table_changes(timestamp, previous_data, current_data):
    if not timestamp:
        raise PreventUpdate
    
    if not previous_data:
        raise PreventUpdate
    
    db = get_session()
    try:
        # Check for deletions
        if len(current_data) < len(previous_data):
            # Find deleted row
            deleted_ids = set(row['id'] for row in previous_data) - set(row['id'] for row in current_data)
            for idea_id in deleted_ids:
                idea = db.query(Idea).filter_by(id=idea_id).first()
                if idea:
                    db.delete(idea)
            db.commit()
            return html.Div('✓ Idea deleted successfully', style={'color': 'green'})
        
        # Check for edits
        for i, row in enumerate(current_data):
            if i < len(previous_data) and row != previous_data[i]:
                # Row was edited
                idea = db.query(Idea).filter_by(id=row['id']).first()
                if idea:
                    idea.title = row['title']
                    idea.benefactor_team = row['team']
                    idea.priority = PriorityLevel(row['priority'])
                    idea.size = IdeaSize(row['size'])
                    idea.status = IdeaStatus(row['status'])
                    idea.email = row['email']
                    # Note: Skills editing would need special handling
                    
        db.commit()
        return html.Div('✓ Changes saved successfully', style={'color': 'green'})
        
    except Exception as e:
        db.rollback()
        return html.Div(f'Error: {str(e)}', style={'color': 'red'})
    finally:
        db.close()