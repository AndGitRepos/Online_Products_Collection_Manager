from dash import dash, html, dcc, Output, Input
from .callbacks import register_callbacks
from .main_layout import create_main_layout
from .collections_layout import create_collections_layout
import os

def create_app():
    app = dash.Dash(__name__, 
                external_stylesheets=[
                    '/assets/styling/common.css',
                    '/assets/styling/main.css',
                    '/assets/styling/collections.css'
                ],
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
