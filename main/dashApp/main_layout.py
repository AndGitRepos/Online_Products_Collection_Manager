from dash import html, dcc

def create_main_layout():
    return html.Div([
        # Background
        html.Div(style={"width": "1000px", "height": "650px", "position": "absolute", "background": "#222831"}),

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
        ], style={"width": "256px", "height": "auto", "left": "28px", "top": "102px", "position": "absolute"}),

        # Divider
        html.Div(style={"width": "950px", "height": "0px", "left": "25px", "top": "307px", "position": "absolute", "border": "1px white solid"}),

        # Collections section
        html.Div([
            html.Div(style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "20px"}),
            html.Div("Collections", style={"color": "white", "fontSize": "15px", "fontWeight": "700"}),
            html.Button("Refresh", id="refresh-button", className="refresh-button"),
            html.Div(id='collection-display', style={"overflowY": "auto", "maxHeight": "280px"})
        ], style={"width": "951px", "height": "330px", "left": "24px", "top": "319px", "position": "absolute"}),

        # Notification container
        html.Div(id="notification-container", style={"position": "absolute", "top": "11px", "right": "20px", "zIndex": "1000"}),

        # Hidden elements
        dcc.Store(id='selected-collection', data=None),
        dcc.Store(id='notifications', data=[]),
        dcc.Download(id="download-json"),
        dcc.Interval(id='search-progress', interval=1000, n_intervals=0, disabled=True),
        dcc.Interval(id='notification-interval', interval=1000, n_intervals=0),
        dcc.Interval(id='initial-refresh', interval=1, max_intervals=1),
        # Hidden elements for collections page
        html.Div(id='collections-grid', style={'display': 'none'}),
    ], className="main-page")
