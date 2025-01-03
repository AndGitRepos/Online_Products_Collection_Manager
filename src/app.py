import os, sys
import subprocess
import pkg_resources
from pathlib import Path
# Get the path to the project root directory
# Allows importing of modules
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root.replace("/src", ""))

from src.callbacks.common_callbacks import register_common_callbacks
from src.callbacks.home_callbacks import register_home_callbacks
from src.callbacks.collections_callbacks import register_collections_callbacks

"""
Checks if any dependencies are missing and installs them
"""
def install_dependencies(requirements_file='requirements.txt'):
    required = set()
    with open(requirements_file, 'r') as f:
        for line in f:
            package = line.strip()
            if package and not package.startswith('#'):
                required.add(package)

    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

    if missing:
        python = sys.executable
        subprocess.check_call([python, '-m', 'pip', 'install', '-r', requirements_file], stdout=subprocess.DEVNULL)
        print(f"Installed missing dependencies: {', '.join(missing)}")
    else:
        print("All dependencies are already installed.")

def create_app():
    app = dash.Dash(__name__, 
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

""" - MAIN - """
if __name__ == "__main__":
    requirements_file = Path('requirements.txt')
    if requirements_file.exists():
        install_dependencies(str(requirements_file))
    else:
        print(f"Requirements file not found: {requirements_file}")
        
    from dash import dash, html, dcc
    
    app = create_app()
    app.run_server(debug=True)