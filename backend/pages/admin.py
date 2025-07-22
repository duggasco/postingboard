from dash import html, dcc, callback, Output, Input
from flask import session


layout = html.Div([
    dcc.Location(id='admin-redirect', refresh=True),
    html.Div(id='admin-redirect-trigger')
])

@callback(
    Output('admin-redirect', 'href'),
    Input('admin-redirect-trigger', 'children')
)
def redirect_admin(_):
    if session.get('is_admin'):
        return '/admin/dashboard'
    else:
        return '/admin/login'