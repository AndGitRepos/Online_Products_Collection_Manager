from dash import Input, Output, State, ALL, MATCH, callback_context, no_update, html
from dash.exceptions import PreventUpdate
import dash
import time
import threading
import json
import asyncio
import pandas as pd
import plotly.express as px
from src.WebScraper import WebScraper
from src.DataManager import DataManager
from src.Collection import Collection

# Global variables
collections = []
search_result = None
is_searching = False
search_start_time = None
last_scrape_duration = None

def load_collections():
    global collections
    try:
        collections = DataManager.loadCollectionsFromCsvFolder("CsvFolder")
        print(f"Loaded {len(collections)} collections from CsvFolder")
    except FileNotFoundError:
        print("CsvFolder not found. Starting with empty collections.")
        collections = []
    except Exception as e:
        print(f"Error loading collections: {str(e)}")
        collections = []

def background_search(product_name):
    global search_result, is_searching, search_start_time, last_scrape_duration
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    search_start_time = time.time()
    search_result = loop.run_until_complete(WebScraper.searchForProducts(product_name))
    last_scrape_duration = time.time() - search_start_time
    is_searching = False
    if search_result:
        DataManager.saveCollectionsToCsvFolder("CsvFolder", [search_result])

def create_notification(message, color):
    return html.Div([
        html.Div(style={"width": "9px", "height": "56px", "left": "0px", "top": "0px", "position": "absolute", "background": color, "borderRadius": "5px"}),
        html.Div("Notification", style={"left": "19px", "top": "5px", "position": "absolute", "color": "white", "fontSize": "13px", "fontWeight": "700"}),
        html.Div(message, style={"left": "22px", "top": "28px", "position": "absolute", "color": "white", "fontSize": "12px", "fontWeight": "400"}),
    ], style={"width": "177px", "height": "56px", "position": "relative", "background": "#393E46", "borderRadius": "5px", "border": "1px #00ADB5 solid", "marginBottom": "10px"}, id={"type": "notification", "index": time.time()})

def display_collections():
    return [create_collection_item(collection.name, len(collection.products), i) for i, collection in enumerate(collections)]

def format_time(seconds):
    return f"{seconds:.2f}" if seconds is not None else "0.00"

def truncate_name(name, max_length=25):
    return (name[:max_length] + '...') if len(name) > max_length else name

def create_collection_item(name, total_products, index):
    return html.Div([
        html.Div([
            html.Div([
                html.Div(name, style={"color": "#EEEEEE", "fontSize": "15px", "fontWeight": "700"}),
                html.Div(f"Total products: {total_products}", style={"color": "#EEEEEE", "fontSize": "12px", "fontWeight": "400"}),
            ], style={"flex": "1"}),
            html.Div("▼", className="chevron", style={"cursor": "pointer", "transition": "transform 0.3s ease"}),
        ], className="collection-header", style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}),
        html.Div([
            html.H5("Products:"),
            html.Div(id={"type": "collection-products", "index": index}),
            html.Button("Export Collection", className="export-button", id={"type": "export-collection", "index": index})
        ], id={"type": "collection-collapse", "index": index}, style={"display": "none"}),
    ], className="collection-item", id={"type": "collection-item", "index": index}, style={
        "background": "#393E46",
        "borderRadius": "15px",
        "padding": "12px 17px",
        "marginBottom": "10px",
        "cursor": "pointer"
    })

def register_callbacks(app):
    @app.callback(
        Output('collection-display', 'children'),
        Output('search-progress', 'disabled'),
        Output('notification-container', 'children'),
        Output('current-scrape-time', 'children'),
        Output('last-scrape-duration', 'children'),
        Output('total-collections', 'children'),
        Output('current-scrape-products', 'children'),
        Input('url', 'pathname'),
        Input('refresh-button', 'n_clicks'),
        Input('search-button', 'n_clicks'),
        Input('search-progress', 'n_intervals'),
        Input('initial-refresh', 'n_intervals'),
        Input('notification-interval', 'n_intervals'),
        State('product-input', 'value'),
        State('notification-container', 'children'),
        prevent_initial_call=True
    )
    def handle_main_page_updates(pathname, refresh_clicks, search_clicks, search_intervals, 
                                initial_refresh, notification_interval, product_name, current_notifications):
        if pathname != '/':
            raise PreventUpdate
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Initialize outputs
        outputs = [no_update] * 7

        if trigger_id in ['initial-refresh', 'refresh-button']:
            load_collections()
            outputs = [
                display_collections(),
                True,
                create_notification("Collections refreshed", "#00ADB5"),
                f"Current scrape time elapsed: 0 seconds",
                f"Last scrape duration: {format_time(last_scrape_duration)} seconds",
                f"Total Collections: {len(collections)}",
                f"Current scrape products collected: {sum(len(c.products) for c in collections)} products"
            ]

        elif trigger_id == 'search-button' and product_name:
            global is_searching, search_result
            is_searching = True
            search_result = None
            threading.Thread(target=lambda: background_search(product_name)).start()
            outputs[1:3] = [False, create_notification("Searching...", "#FFB507")]

        elif trigger_id == 'search-progress':
            if is_searching:
                elapsed_time = time.time() - search_start_time if search_start_time else 0
                outputs[1:] = [
                    False,
                    no_update,
                    f"Current scrape time elapsed: {format_time(elapsed_time)} seconds",
                    f"Last scrape duration: {format_time(last_scrape_duration)} seconds",
                    f"Total Collections: {len(collections)}",
                    f"Current scrape products collected: {sum(len(c.products) for c in collections)} products"
                ]
            elif search_result:
                collections.append(search_result)
                outputs = [
                    display_collections(),
                    True,
                    create_notification("Search completed. New collection added.", "#00ADB5"),
                    f"Current scrape time elapsed: {format_time(last_scrape_duration)} seconds",
                    f"Last scrape duration: {format_time(last_scrape_duration)} seconds",
                    f"Total Collections: {len(collections)}",
                    f"Current scrape products collected: {sum(len(c.products) for c in collections)} products"
                ]

        # Handle notifications
        if trigger_id == 'notification-interval' and current_notifications:
            current_time = time.time()
            updated_notifications = [
                notif for notif in current_notifications
                if isinstance(notif, dict) and isinstance(notif.get('props', {}).get('id', {}), dict) and
                current_time - notif['props']['id'].get('index', 0) < 5
            ]
            outputs[2] = updated_notifications

        return tuple(outputs)

    @app.callback(
        Output('collections-grid', 'children'),
        Output('notification-container', 'children', allow_duplicate=True),
        Input('url', 'pathname'),
        Input('refresh-button', 'n_clicks'),
        Input('initial-refresh', 'n_intervals'),
        Input('notification-interval', 'n_intervals'),
        State('notification-container', 'children'),
        prevent_initial_call=True
    )
    def handle_collections_page_updates(pathname, refresh_clicks, initial_refresh, notification_interval, current_notifications):
        if pathname != '/collections':
            raise PreventUpdate
        
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id in ['initial-refresh', 'refresh-button']:
            load_collections()
            collections_grid = [
                html.Div(collection.name, 
                         className="collection-item",
                         id={'type': 'collection-item', 'index': i})
                for i, collection in enumerate(collections)
            ]
            return collections_grid, create_notification("Collections refreshed", "#00ADB5")

        # Handle notifications
        if trigger_id == 'notification-interval' and current_notifications:
            current_time = time.time()
            updated_notifications = [
                notif for notif in current_notifications
                if isinstance(notif, dict) and isinstance(notif.get('props', {}).get('id', {}), dict) and
                current_time - notif['props']['id'].get('index', 0) < 5
            ]
            return no_update, updated_notifications

        return no_update, no_update

    @app.callback(
        Output({"type": "collection-collapse", "index": MATCH}, "style"),
        Output({"type": "collection-products", "index": MATCH}, "children"),
        Output({"type": "collection-item", "index": MATCH}, "style"),
        Input({"type": "collection-item", "index": MATCH}, "n_clicks"),
        State({"type": "collection-collapse", "index": MATCH}, "style"),
        State({"type": "collection-item", "index": MATCH}, "style"),
        State({"type": "collection-item", "index": MATCH}, "id"),
        State('url', 'pathname')
    )
    def toggle_collection(n_clicks, collapse_style, item_style, item_id, pathname):
        if pathname == '/collections':
            # For collections page, we don't need to toggle anything
            raise PreventUpdate
        if n_clicks:
            try:
                collection_index = item_id['index']
                if collection_index < len(collections):
                    collection = collections[collection_index]
                    products = [
                        html.Div([
                            html.Div(f"{product.name} - £{product.price}", className="product-name"),
                            html.Div(product.url, className="product-url"),
                        ], className="product-item")
                        for product in collection.products[:5]  # Limiting to 5 products for performance
                    ]
                    new_collapse_style = {"display": "block"} if collapse_style.get("display") == "none" else {"display": "none"}
                    new_item_style = {**item_style, "background": "#00ADB5" if new_collapse_style["display"] == "block" else "#393E46"}
                    return new_collapse_style, products, new_item_style
            except (KeyError, ValueError, IndexError) as e:
                print(f"Error in toggle_collection: {str(e)}")
        return collapse_style, no_update, item_style

    @app.callback(
        Output("download-json", "data"),
        Input({"type": "export-collection", "index": ALL}, "n_clicks"),
        State({"type": "export-collection", "index": ALL}, "id"),
        prevent_initial_call=True
    )
    def export_collection(n_clicks, ids):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        button_index = json.loads(button_id)['index']
        
        # Check if the button was actually clicked
        if n_clicks[button_index] is None or n_clicks[button_index] == 0:
            raise PreventUpdate
        
        if button_index < len(collections):
            collection = collections[button_index]
            collection_dict = DataManager.convertCollectionToDictionary(collection)
            return dict(content=json.dumps(collection_dict, indent=2), filename=f"{collection.name}.json")
        
        raise PreventUpdate

    @app.callback(
        Output('products-grid', 'children'),
        Input({"type": "collection-item", "index": ALL}, "n_clicks"),
        State({"type": "collection-item", "index": ALL}, "id"),
        State('url', 'pathname')
    )
    def update_products_grid(n_clicks, ids, pathname):
        if pathname != '/collections':
            raise PreventUpdate
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        clicked_id = ctx.triggered[0]['prop_id'].split('.')[0]
        clicked_index = json.loads(clicked_id)['index']
        
        if clicked_index < len(collections):
            selected_collection = collections[clicked_index]
            products = selected_collection.products
            return [
                html.Div(truncate_name(product.name), 
                         style={"color": "white", "fontSize": "15px", "fontWeight": "700",
                                "display": "flex", "alignItems": "center", "justifyContent": "center",
                                "background": "#393E46", "borderRadius": "10px", "height": "70px"},
                         className="product-item",
                         title=product.name)
                for product in products
            ]
        return []

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
    
    @app.callback(
        Output('product-graph', 'figure'),
        Input({'type': 'collection-item', 'index': ALL}, 'n_clicks'),
        State({'type': 'collection-item', 'index': ALL}, 'id'),
        State('url', 'pathname')
    )
    def update_graph(n_clicks, ids, pathname):
        if pathname != '/collections':
            raise PreventUpdate
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        try:
            clicked_id = ctx.triggered[0]['prop_id'].split('.')[0]
            clicked_index = json.loads(clicked_id)['index']
            
            if clicked_index < len(collections):
                selected_collection = collections[clicked_index]
                products = selected_collection.products

                # Create a DataFrame from the products
                df = pd.DataFrame([
                    {'name': truncate_name(product.name), 'price': product.price}
                    for product in products
                ])

                # Create a bar chart
                fig = px.bar(df, x='name', y='price', title=f'Product Prices in {selected_collection.name}')
                fig.update_layout(
                    xaxis_title="Product Name",
                    yaxis_title="Price (£)",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                return fig
        except Exception as e:
            print(f"Error in update_graph: {str(e)}")
        
        # If no collection is selected or an error occurred, return an empty figure
        return px.bar(title="Select a collection to view product prices")