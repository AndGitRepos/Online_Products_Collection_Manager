from dash import html, dcc

def create_home_layout():
    return html.Div([
        # Hamburger menu
        html.Div([
            html.Div([
                html.Div(className="hamburger-line"),
                html.Div(className="hamburger-line"),
                html.Div(className="hamburger-line"),
            ], className="hamburger-menu")
        ], id='sidebar-toggle', className="menu-container"),

        # Search container
        html.Div([
            # Search bar
            dcc.Input(
                id="product-input",
                type="text",
                placeholder="Search for a collection",
                className="search-bar"
            ),
            # Search button
            html.Button("Search", id="search-button", className="search-button"),
        ], className="search-container"),

        # Analytics section
        html.Div([
            html.Div("Analytics", style={"color": "white", "fontSize": "15px", "fontWeight": "700", "marginBottom": "20px"}),
            html.Div(id="current-scrape-time", style={"color": "white", "fontSize": "13px", "fontWeight": "400", "marginBottom": "10px"}),
            html.Div(id="last-scrape-duration", style={"color": "white", "fontSize": "13px", "fontWeight": "400", "marginBottom": "10px"}),
            html.Div(id="total-collections", style={"color": "white", "fontSize": "13px", "fontWeight": "400", "marginBottom": "10px"}),
            html.Div(id="current-scrape-products", style={"color": "white", "fontSize": "13px", "fontWeight": "400"}),
        ], className="analytics-section"),

        # Divider
        html.Div(className="divider"),

        # Collections section
        html.Div([
            html.Div("Collections", style={"color": "white", "fontSize": "15px", "fontWeight": "700"}),
            html.Button("Refresh", id="refresh-button", className="refresh-button"),
            html.Div(id='collections-list')
        ], className="collections-container"),

        # Notification container
        html.Div(id="notification-container", style={"position": "absolute", "top": "11px", "right": "20px", "zIndex": "1000"}),

        # Hidden elements
        dcc.Store(id='selected-collection', data=None),
        dcc.Store(id='notifications', data=[]),
        dcc.Download(id="download-json"),
        dcc.Download(id="download-csv"),
        dcc.Interval(id='search-progress', interval=500, n_intervals=0, disabled=True),
        dcc.Interval(id='notification-interval', interval=500, n_intervals=0),
        dcc.Interval(id='initial-refresh', interval=1, max_intervals=1),
        # Hidden elements to stop callback errors
        html.Div(id='collections-grid', style={'display': 'none'}),
        html.Div(id='products-grid', style={'display': 'none'}),
        html.Div(id='product-details', style={'display': 'none'})
    ], className="main-page")
