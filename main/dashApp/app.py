import dash
from dash import html, dcc, Output, Input
import dash_bootstrap_components as dbc
from .callbacks import register_callbacks
from .main_layout import create_main_layout
from .collections_layout import create_collections_layout
import os

def create_app():
    assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
    app = dash.Dash(__name__, 
                external_stylesheets=[
                    '/assets/common.css',
                    '/assets/main.css',
                    '/assets/collections.css'
                ],
                assets_folder=assets_path,
                suppress_callback_exceptions=True)
    
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='sidebar-container'),
        html.Div(id='page-content')
    ])
    
    @app.callback(
        [Output('page-content', 'children'),
         Output('sidebar-container', 'children')],
        [Input('url', 'pathname')]
    )
    def display_page(pathname):
        sidebar = html.Div([
            html.H2("Menu"),
            dcc.Link("Home", href="/", className="menu-item"),
            dcc.Link("Collections", href="/collections", className="menu-item"),
        ], id='sidebar', className='sidebar')

        if pathname == '/collections':
            return create_collections_layout(), sidebar
        else:
            return create_main_layout(), sidebar

    register_callbacks(app)
    return app
