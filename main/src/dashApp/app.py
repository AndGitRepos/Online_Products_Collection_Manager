from dash import dash, html, dcc
from src.dashApp.callbacks.common_callbacks import register_common_callbacks
from src.dashApp.callbacks.home_callbacks import register_home_callbacks
from src.dashApp.callbacks.collections_callbacks import register_collections_callbacks

def create_app():
    app = dash.Dash(__name__, 
                external_stylesheets=[
                    '/src/dashApp/assets/styling/common.css',
                    '/src/dashApp/assets/styling/home.css',
                    '/src/dashApp/assets/styling/collections.css'
                ],
                suppress_callback_exceptions=True)
    
    # Setting a global layout that every page will have
    # Trigger for change in url and adding sidebar/sidepanel
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='sidebar-container'),
        html.Div(id='page-content')
    ])

    register_common_callbacks(app)
    register_home_callbacks(app)
    register_collections_callbacks(app)
    
    return app
