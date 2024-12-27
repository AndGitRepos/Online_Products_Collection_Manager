import dash
import dash_bootstrap_components as dbc
from .layout import create_layout
from .callbacks import register_callbacks
import os

def create_app():
    assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
    app = dash.Dash(__name__, 
                    external_stylesheets=[dbc.themes.BOOTSTRAP],
                    assets_folder=assets_path)

    app.layout = create_layout()
    register_callbacks(app)
    return app
