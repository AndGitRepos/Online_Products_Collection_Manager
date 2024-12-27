import dash_bootstrap_components as dbc
from dash import dcc, html

def create_layout():
    return dbc.Container([
        dbc.Navbar(
            dbc.Container([
                html.A(
                    dbc.Row([
                        dbc.Col(dbc.NavbarBrand("SCRAPER", className="ms-2")),
                    ], align="center", className="g-0"),
                    href="/",
                    style={"textDecoration": "none"},
                ),
                dbc.NavbarToggler(id="navbar-toggler"),
                dbc.Collapse(
                    dbc.Nav([
                        dbc.NavItem(dbc.NavLink("Home", href="#")),
                        dbc.NavItem(dbc.NavLink("Collections", href="#")),
                        dbc.NavItem(dbc.NavLink("About", href="#")),
                    ]),
                    id="navbar-collapse",
                    navbar=True,
                ),
            ]),
            color="dark",
            dark=True,
            className="mb-5",
        ),
        
        dbc.Row([
            dbc.Col([
                html.H1("ONLINE PRODUCTS MANAGER", className="display-3 text-center mb-4", style={"color": "#66FCF1"}),
                html.P("Welcome to the Online Products Collection Manager. Search, manage, and export your product collections with ease.", className="lead text-center mb-5"),
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Input(id="product-input", placeholder="Enter product name", type="text", className="mb-3"),
                dbc.Button("Search", id="search-button", color="primary", className="me-2"),
                dbc.Button("Refresh Collections", id="refresh-button", color="secondary", className="me-2"),
                dcc.Upload(
                    id='upload-json',
                    children=dbc.Button('Import JSON', color="secondary", className="me-2"),
                    multiple=False
                ),
                dbc.Button("Export JSON", id="export-button", color="primary"),
            ], width={"size": 8, "offset": 2}, className="mb-5")
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Loading(
                    id="loading",
                    type="default",
                    children=[html.Div(id="collection-display")]
                ),
            ])
        ]),
        
        html.Div(id="notification-container", className="notification-container"),

        dcc.Interval(id='search-progress', interval=1000, n_intervals=0, disabled=True),
        dcc.Interval(id='periodic-refresh', interval=300000, n_intervals=0),  # 5 minutes = 300000 ms
        dcc.Interval(id='notification-interval', interval=100, n_intervals=0),
        dcc.Store(id='selected-collection', data=None),
        dcc.Store(id='notifications', data=[]),
        dcc.Download(id="download-json")
    ], fluid=True, className="px-4")
