import os, sys
from dash import dash, html, dcc

# Get the path to the project root directory
# Allows importing of modules
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root.replace("/src", ""))

from src.callbacks.common_callbacks import register_common_callbacks
from src.callbacks.home_callbacks import register_home_callbacks
from src.callbacks.collections_callbacks import register_collections_callbacks

def create_app():
    app = dash.Dash(__name__, title='Online-Products-Collection-Manager',
                external_stylesheets=[
                    '/src/assets/styling/common.css',
                    '/src/assets/styling/home.css',
                    '/src/assets/styling/collections.css'
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

# Create the app instance
app = create_app()

# Get the Flask server
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
