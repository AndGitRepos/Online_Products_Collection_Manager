from dash import Input, Output, State, ALL, callback_context, no_update, html, dcc
from dash.exceptions import PreventUpdate
import time
from src.layouts.home_layout import create_home_layout
from src.layouts.collections_layout import create_collections_layout

"""
This method allows the main app file (app.py) to only need 
to call one method to register all callbacks that are used globally
"""
def register_common_callbacks(app) -> None:
    """
    Handles changes in pathname, changing webpage content depending on the value
    """
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
            return create_home_layout(), sidebar
    
    @app.callback(
        Output('url', 'pathname'),
        Input('url', 'pathname')
    )
    def update_url(pathname : str):
        return pathname

    """
    Handles inputs to the menu/hamburger 
    button to show or hide the side panel
    """
    @app.callback(
        Output("sidebar", "style"),
        [Input("sidebar-toggle", "n_clicks")],
        [State("sidebar", "style")]
    )
    def toggle_sidebar(n, style):
        if n:
            if style is None or "left" not in style or style["left"] == "-250px":
                return {"left": "0px", "transition": "left 0.3s"}
            else:
                return {"left": "-250px", "transition": "left 0.3s"}
        return {"left": "-250px"}
    
    """
    Handles notification system to ensure that 
    it stays for a fixed amount of time (5 seconds)
    """
    @app.callback(
        Output('notification-container', 'children', allow_duplicate=True),
        Input('url', 'pathname'),
        Input('notification-interval', 'n_intervals'),
        State('notification-container', 'children'),
        prevent_initial_call=True
    )
    def handle_notifications(pathname, notification_interval, current_notifications):
        ctx = callback_context
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'no_trigger'

        # Initialize outputs
        output = no_update

        # Handle notifications
        if trigger_id == 'notification-interval' and current_notifications:
            current_time = time.time()
            if current_time - current_notifications.get('props', {}).get('id', {}).get('index', 0) > 5:
                output = {}

        return output