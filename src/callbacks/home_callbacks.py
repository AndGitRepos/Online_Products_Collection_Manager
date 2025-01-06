from dash import Input, Output, State, ALL, MATCH, callback_context, no_update, html
from dash.exceptions import PreventUpdate
import time
import threading
import asyncio
import json
from typing import List
from src.callbacks.common_funcs import load_collections, create_notification, verify_pathname_and_get_trigger
from src.backend.WebScraper import WebScraper
from src.backend.DataManager import DataManager
from src.backend.Collection import Collection

# Global variables
collections : List[Collection] = []
search_result : Collection = None
is_searching : bool = False
search_start_time : float = 0.0
last_scrape_duration : float = 0.0

"""
This method should be called by a seperate thread.
It will ensure that execution does not continue until the webscraper 
has finished scraping all of the products for the collection.
After scraping is finished it will save the collection as a CSV
"""
def background_search(product_name) -> None:
    global search_result, is_searching, search_start_time, last_scrape_duration
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    search_start_time = time.time()
    search_result = loop.run_until_complete(WebScraper.search_for_products(product_name))
    last_scrape_duration = time.time() - search_start_time
    is_searching = False
    if search_result:
        DataManager.save_collections_to_csv_folder("CsvFolder", [search_result])

"""
This method returns the HTML data of a collection 
to be stored within the collection-list
"""
def create_collection_item(name : str, total_products : int, index : int):
    return html.Div([
        html.Div([
            html.Div([
                html.Div(name, className="collection-name"),
                html.Div(f"Total products: {total_products}", className="collection-total"),
            ], style={"flex": "1"}),
            html.Div("▼", className="chevron", style={"cursor": "pointer", "transition": "transform 0.3s ease"}),
        ], className="collection-header"),
        html.Div([
            html.H5("Products:"),
            html.Div(id={"type": "collection-products", "index": index}),
            html.Div([
                html.Div([
                    html.Button("Export Collection", className="export-button", id={"type": "export-collection", "index": index}),
                    html.Button("Download CSV", className="download-csv-button", id={"type": "download-csv", "index": index}),
                ]),
                html.Button("Delete Collection", className="delete-collection-button", id={"type": "delete-collection", "index": index})
            ], className="collection-actions"),
        ], id={"type": "collection-collapse", "index": index}, style={"display": "none"}),
    ], className="collection-item", id={"type": "collection-item", "index": index})

"""
Iterates through all of the collections and creates a list 
of collection items to be stored within the collection-list
"""
def display_collections(collections: List[Collection]):
    return [create_collection_item(collection.name, len(collection.products), i) for i, collection in enumerate(collections)]

"""
Formats a float value to 2dp as a string
"""
def format_time(seconds : float) -> str:
    return f"{seconds:.2f}" if seconds is not None else "0.00"

"""
This method allows the main app file (app.py) to only need 
to call one method to register all callbacks for the home page
"""
def register_home_callbacks(app) -> None:
    """
    Handle input by user to being search/scrape for collection data
    """
    @app.callback(
        Output('search-progress', 'disabled', allow_duplicate=True),
        Output('notification-container', 'children', allow_duplicate=True),
        Input('url', 'pathname'),
        Input('search-button', 'n_clicks'),
        State('product-input', 'value'),
        prevent_initial_call=True
    )
    def handle_search(pathname, search_clicks, product_name):
        trigger = verify_pathname_and_get_trigger(callback_context, pathname, '/')
        if trigger == None:
            raise PreventUpdate
        
        # Initialize outputs
        outputs = [no_update] * 2
        
        if trigger == 'search-button' and product_name:
            global is_searching, search_result
            is_searching = True
            search_result = None
            # Calling background search in asynchronous thread to 
            # not block application process while its searching/scraping
            threading.Thread(target=lambda: background_search(product_name)).start()
            outputs = [False, create_notification("Searching...")]
                
        return tuple(outputs)
    
    """
    Handles all updates for the Analytics section within the home page
    """
    @app.callback(
        Output('search-progress', 'disabled', allow_duplicate=True),
        Output('notification-container', 'children', allow_duplicate=True),
        Output('current-scrape-time', 'children'),
        Output('last-scrape-duration', 'children'),
        Output('total-collections', 'children'),
        Output('current-scrape-products', 'children'),
        Input('url', 'pathname'),
        Input('initial-refresh', 'n_intervals'),
        Input('search-progress', 'n_intervals'),
        Input('collections-list', 'children'),
        prevent_initial_call=True
    )
    def handle_analytics_update(pathname, refresh_interval, search_interval, collections_children):
        global collections
        trigger = verify_pathname_and_get_trigger(callback_context, pathname, '/')
        if trigger is None:
            raise PreventUpdate
        
        # Initialize outputs
        outputs = [no_update] * 6
        
        # Updating the Analytics information with the progress and history of searches
        if trigger == 'search-progress':
            if is_searching:
                elapsed_time = time.time() - search_start_time if search_start_time else 0
                outputs = [
                    False,
                    no_update,
                    f"Current scrape time elapsed: {format_time(elapsed_time)} seconds",
                    f"Last scrape duration: {format_time(last_scrape_duration)} seconds",
                    f"Total Collections: {len(collections)}",
                    f"Current scrape products collected: {sum(len(c.products) for c in collections)} products"
                ]
            elif search_result:
                collections = load_collections()
                outputs = [
                    True,
                    create_notification("Search completed. New collection added."),
                    f"Current scrape time elapsed: {format_time(last_scrape_duration)} seconds",
                    f"Last scrape duration: {format_time(last_scrape_duration)} seconds",
                    f"Total Collections: {len(collections)}",
                    f"Current scrape products collected: {sum(len(c.products) for c in collections)} products"
                ]
        elif trigger == "initial-refresh" or trigger == 'collections-list':
            outputs = [
                True,
                create_notification("Collections refreshed"),
                f"Current scrape time elapsed: {format_time(last_scrape_duration)} seconds",
                f"Last scrape duration: {format_time(last_scrape_duration)} seconds",
                f"Total Collections: {len(collections)}",
                f"Current scrape products collected: {sum(len(c.products) for c in collections)} products"
            ]
            
        return tuple(outputs)
    
    """
    Handles all updates of the collections list,
    ensuring that the list is always up-to-date 
    with all the collected collections
    """
    @app.callback(
        Output('collections-list', 'children', allow_duplicate=True),
        Output('notification-container', 'children', allow_duplicate=True),
        Input('url', 'pathname'),
        Input('refresh-button', 'n_clicks'),
        Input('initial-refresh', 'n_intervals'),
        Input('search-progress', 'disabled'),
        prevent_initial_call=True
    )
    def update_collections_grid(pathname, refresh_clicks, refresh_interval, search_disabled):
        global collections
        trigger = verify_pathname_and_get_trigger(callback_context, pathname, '/')
        if trigger is None:
            raise PreventUpdate
        
        if trigger == 'search-progress' and is_searching:
            raise PreventUpdate
        elif trigger == 'search-progress' and not search_disabled:
            raise PreventUpdate

        collections = load_collections()
        return tuple([display_collections(collections), create_notification("Collections refreshed")])
    
    """
    Updates selected collection from collection-list to show product details 
    and to allow for exporting of collection
    """
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
        if pathname != '/':
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
                    return new_collapse_style, products, item_style
            except (KeyError, ValueError, IndexError) as e:
                print(f"Error in toggle_collection: {str(e)}")
        return collapse_style, no_update, item_style
    
    @app.callback(
        Output("download-json", "data"),
        Input({"type": "export-collection", "index": ALL}, "n_clicks"),
        State({"type": "export-collection", "index": ALL}, "id"),
        State('url', 'pathname'),
        prevent_initial_call=True
    )
    def export_collection(n_clicks, ids, pathname):
        trigger = verify_pathname_and_get_trigger(callback_context, pathname, '/')
        if trigger == None:
            raise PreventUpdate
        
        button_id = trigger
        button_index = json.loads(button_id)['index']
        
        # Check if the button was actually clicked
        if n_clicks[button_index] is None or n_clicks[button_index] == 0:
            raise PreventUpdate
        
        if button_index < len(collections):
            collection = collections[button_index]
            collection_dict = DataManager.convert_collection_to_dictionary(collection)
            return dict(content=json.dumps(collection_dict, indent=2), filename=f"{collection.name}.json")
        
        raise PreventUpdate
    
    @app.callback(
        Output("download-csv", "data"),
        Input({"type": "download-csv", "index": ALL}, "n_clicks"),
        State({"type": "download-csv", "index": ALL}, "id"),
        State('url', 'pathname'),
        prevent_initial_call=True
    )
    def download_csv(n_clicks, ids, pathname):
        trigger = verify_pathname_and_get_trigger(callback_context, pathname, '/')
        if trigger is None:
            raise PreventUpdate
        
        button_id = trigger
        button_index = json.loads(button_id)['index']
        
        # Check if the button was actually clicked
        if n_clicks[button_index] is None or n_clicks[button_index] == 0:
            raise PreventUpdate
        
        if button_index < len(collections):
            collection = collections[button_index]
            csv_string = DataManager.convert_collection_to_csv_string(collection)
            return dict(content=csv_string, filename=f"{collection.name}.csv")
        
        raise PreventUpdate
    
    @app.callback(
        Output('collections-list', 'children', allow_duplicate=True),
        Output('notification-container', 'children', allow_duplicate=True),
        Input({"type": "delete-collection", "index": ALL}, "n_clicks"),
        State({"type": "delete-collection", "index": ALL}, "id"),
        State('url', 'pathname'),
        prevent_initial_call=True
    )
    def delete_collection(n_clicks, ids, pathname):
        global collections
        trigger = verify_pathname_and_get_trigger(callback_context, pathname, '/')
        if trigger is None:
            raise PreventUpdate
        
        button_id = trigger
        button_index = json.loads(button_id)['index']
        
        # Check if the button was actually clicked
        if n_clicks[button_index] is None or n_clicks[button_index] == 0:
            raise PreventUpdate
        
        if button_index < len(collections):
            collection_name = collections[button_index].name
            DataManager.delete_collection(collection_name)
            collections = load_collections()
            return display_collections(collections), create_notification(f"Collection '{collection_name}' deleted.")
        
        raise PreventUpdate