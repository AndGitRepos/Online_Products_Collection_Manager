from dash import html, dcc
from src.layouts.common import create_hamburger_menu_container

# Creates the layout of HTML data for the home page
def create_home_layout():
    return html.Div([
        # Hamburger menu
        create_hamburger_menu_container(),

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
            html.Button("Scrape", id="search-button", className="button"),
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
            html.Div([
            html.Div("Collections", style={"color": "white", "fontSize": "15px", "fontWeight": "700"}),
            html.Button("Refresh", id="refresh-button", className="button")
            ], className="collections-container-header"),
            html.Div(id='collections-list')
        ], className="collections-container"),

        # Notification container
        html.Div(id="notification-container", style={"position": "absolute", "top": "11px", "right": "20px", "zIndex": "1000"}),

        # Hidden callback triggers for user interactions
        create_callback_triggers(),
        # Hidden elements to stop callback errors
        create_hidden_layout_to_stop_callback_errors()
    ], className="main-page")
    
"""
Hidden elements wrapped within a Div to allow for 
easy implementation of seperated logic in different methods
""" 
def create_callback_triggers():
    return html.Div([
            dcc.Store(id='selected-collection', data=None),
            dcc.Store(id='notifications', data=[]),
            dcc.Download(id="download-json"),
            dcc.Download(id="download-csv"),
            dcc.Interval(id='search-progress', interval=500, n_intervals=0, disabled=True),
            dcc.Interval(id='notification-interval', interval=1000, n_intervals=0),
            dcc.Interval(id='initial-refresh', interval=1, max_intervals=1)
        ], style={'display': 'none'})
    
def create_hidden_layout_to_stop_callback_errors():
    return html.Div([
        html.Div(id='collections-grid', style={'display': 'none'}),
        html.Div(id='products-grid', style={'display': 'none'}),
        html.Div(id='product-details', style={'display': 'none'})
    ])