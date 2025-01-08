from dash import html

def create_hamburger_menu_container():
    return html.Div([
            html.Div([
                html.Div(className="hamburger-line"),
                html.Div(className="hamburger-line"),
                html.Div(className="hamburger-line"),
            ], className="hamburger-menu")
        ], id='sidebar-toggle', className="menu-container")