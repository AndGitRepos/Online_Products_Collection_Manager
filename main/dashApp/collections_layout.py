from dash import html, dcc

def create_collections_layout():
    return html.Div([
        # Hamburger menu
        html.Div([
            html.Div([
                html.Div(className="hamburger-line"),
                html.Div(className="hamburger-line"),
                html.Div(className="hamburger-line"),
            ], className="hamburger-menu")
        ], id='sidebar-toggle', className="menu-container"),

        # Page title and refresh button
        html.Div([
            html.H1("Collections", className="page-title"),
            html.Button("Refresh", id="refresh-button", className="refresh-button")
        ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "20px"}),

        # Collections container
        html.Div([
            html.Div(id='collections-grid', className="collections-grid")
        ], className="collections-container"),

        # Main content
        html.Div([
            # Products grid
            html.Div([
                html.Div(id='products-grid', className="products-grid")
            ], className="products-section"),

            # Graph container
            html.Div([
                dcc.Graph(id='product-graph')
            ], className="graph-container"),
        ], className="main-content"),
        
        # Notification container
        html.Div(id="notification-container", style={"position": "absolute", "top": "11px", "right": "20px", "zIndex": "1000"}),

        dcc.Interval(id='notification-interval', interval=1000, n_intervals=0),
        dcc.Interval(id='initial-refresh', interval=1, max_intervals=1),
        # Hidden collection display for consistency
        html.Div(id='collection-display', style={"display": "none"}),
        # Hidden elements for main page
        html.Div(id='search-progress', style={'display': 'none'}),
        html.Div(id='current-scrape-time', style={'display': 'none'}),
        html.Div(id='last-scrape-duration', style={'display': 'none'}),
        html.Div(id='total-collections', style={'display': 'none'}),
        html.Div(id='current-scrape-products', style={'display': 'none'}),
        html.Button(id='search-button', style={'display': 'none'}),
        dcc.Input(id='product-input', style={'display': 'none'}),
        # Hidden elements for toggle collection callbacks
        html.Div([
            html.Div(id={'type': 'collection-collapse', 'index': i}, style={'display': 'none'})
            for i in range(10)  # Assuming a maximum of 10 collections, adjust as needed
        ]),
        html.Div([
            html.Div(id={'type': 'collection-products', 'index': i}, style={'display': 'none'})
            for i in range(10)
        ]),
        html.Div([
            html.Div(id={'type': 'collection-item', 'index': i}, style={'display': 'none'})
            for i in range(10)
        ]),
    ], className="collections-page")
