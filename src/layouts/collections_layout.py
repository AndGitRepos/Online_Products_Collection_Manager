from dash import html, dcc
from src.layouts.common import create_hamburger_menu_container

# Creates the layout of HTML data for the collections page
def create_collections_layout():
    return html.Div([
        # Hamburger menu
        create_hamburger_menu_container(),

        # Page title and refresh button
        html.Div([
            html.H1("Collections", className="page-title"),
            html.Button("Refresh", id="refresh-button", className="button")
        ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "20px"}),

        # Collections container
        html.Div([
            html.Div(id='collections-grid', className="collections-grid")
        ], className="collections-container"),

        # Main content
        html.Div([
            # Products grid or product details
            html.Div([
                html.Div([
                    html.H3("Products", style={"display": "inline-block"}),
                    html.Button("Add Product", id="add-product-button", className="button")
                ], style={"display": "flex", "justify-content": "space-between", "align-items": "center"}),
                html.Div(id='products-grid', className="products-grid"),
                html.Div(id='product-details', style={'display': 'none'})
            ], className="products-section"),

            # Graph container
            html.Div([
                dcc.Graph(id='product-graph'),
                html.Div(id='wordcloud-container'),
                
                # Graph controls
                html.Div([
                    dcc.Dropdown(
                        id='graph-type',
                        options=[
                            {'label': 'Bar Chart', 'value': 'bar'},
                            {'label': 'Line Plot', 'value': 'line'},
                            {'label': 'Word Cloud', 'value': 'wordcloud'},
                            {'label': 'Spreadsheet View', 'value': 'spreadsheet'}
                        ],
                        value='bar',
                        clearable=False
                    ),
                    dcc.Dropdown(
                        id="filter-product-data", 
                        options=[
                            {'label': 'Price', 'value': 'Price'},
                            {'label': 'Rating', 'value': 'Rating'},
                            {'label': 'Reviews count', 'value': 'Reviews-Count'}
                        ],
                        value='Price',
                        clearable=False),
                    dcc.Dropdown(id='filter-product', multi=True),
                ], className="graph-controls")
            ], className="graph-container"),
        ], className="main-content"),
        
        # Notification container
        html.Div(id="notification-container", style={"position": "absolute", "top": "11px", "right": "20px", "zIndex": "1000"}),

        # Hidden Stores and Intervals
        create_hidden_stores_and_intervals(),
        # Hidden layout to prevent callback errors
        create_hidden_layout_to_stop_callback_errors(),
    ], className="collections-page")
    
"""
Hidden elements wrapped within a Div to allow for 
easy implementation of seperated logic in different methods
""" 
def create_hidden_stores_and_intervals():
    return html.Div([
            dcc.Store(id='selected-collection', data=None),
            dcc.Store(id='product-clicked', data=None),
            dcc.Store(id='view-state', data='grid'),
            dcc.Interval(id='notification-interval', interval=1000, n_intervals=0),
            dcc.Interval(id='initial-refresh', interval=1, max_intervals=1)
        ], style={'display': 'none'})
    
def create_hidden_layout_to_stop_callback_errors():
    return html.Div([
                # Hidden collection list to stop callback errors
                html.Div(id='collections-list', style={"display": "none"}),
                # Hidden elements to stop callback errors
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
            ], style={'display': 'none'})
