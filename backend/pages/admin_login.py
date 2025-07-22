from dash import html, dcc, callback, Input, Output, State
from dash.exceptions import PreventUpdate
from flask import session


ADMIN_PASSWORD = '2929arch'

layout = html.Div([
    html.Div([
        html.H2('Admin Login', style={'textAlign': 'center', 'marginBottom': '30px'}),
        
        html.Div([
            html.Label('Password'),
            dcc.Input(
                id='admin-password',
                type='password',
                placeholder='Enter admin password',
                style={'width': '100%', 'padding': '10px', 'marginBottom': '20px'}
            )
        ]),
        
        html.Button('Login', id='admin-login-btn', n_clicks=0, style={
            'width': '100%',
            'padding': '10px',
            'backgroundColor': '#007bff',
            'color': 'white',
            'border': 'none',
            'borderRadius': '4px',
            'cursor': 'pointer',
            'fontSize': '16px'
        }),
        
        html.Div(id='login-feedback', style={'marginTop': '20px', 'textAlign': 'center'})
        
    ], style={
        'maxWidth': '400px',
        'margin': '100px auto',
        'padding': '30px',
        'border': '1px solid #dee2e6',
        'borderRadius': '8px',
        'backgroundColor': 'white'
    })
])

@callback(
    [Output('login-feedback', 'children'),
     Output('admin-auth-store', 'data', allow_duplicate=True)],
    Input('admin-login-btn', 'n_clicks'),
    State('admin-password', 'value'),
    prevent_initial_call=True
)
def handle_login(n_clicks, password):
    if n_clicks == 0:
        raise PreventUpdate
    
    if password == ADMIN_PASSWORD:
        session['is_admin'] = True
        return [
            html.Div([
                html.Div('✓ Login successful!', style={'color': 'green', 'fontWeight': 'bold'}),
                html.Div([
                    'Redirecting to ',
                    dcc.Link('admin dashboard', href='/admin/dashboard', style={'color': '#007bff'})
                ], style={'marginTop': '10px'})
            ]),
            {'authenticated': True}
        ]
    else:
        return [
            html.Div('Invalid password', style={'color': 'red'}),
            {'authenticated': False}
        ]