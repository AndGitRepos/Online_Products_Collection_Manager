from dash import Input, Output, State, ALL, MATCH, html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import asyncio
import threading
import time
import base64
import json
from functools import wraps
from src.WebScraper import WebScraper
from src.DataManager import DataManager
from src.Collection import Collection

# Global variables
collections = []
search_result = None
is_searching = False

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

load_collections()

def background_search(product_name):
    global search_result, is_searching
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    search_result = loop.run_until_complete(WebScraper.searchForProducts(product_name))
    loop.close()
    is_searching = False
    if search_result:
        DataManager.saveCollectionsToCsvFolder("CsvFolder", [search_result])

def create_notification(message, color):
    return {
        "id": f"notification-{time.time()}",
        "message": message,
        "color": color,
        "is_open": True,
        "created_at": time.time() + 0.1  # Add a small delay
    }

def display_collections(selected_collection):
    if not collections:
        return html.Div("No collections to display.", className="text-center")
    
    return html.Div([
        html.H2("All Collections", className="mb-4 text-center", style={"color": "#66FCF1"}),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        dbc.RadioItems(
                            options=[{"label": "", "value": collection.name}],
                            value=collection.name if selected_collection == collection.name else None,
                            id={"type": "collection-radio", "index": i},
                            inline=True
                        ),
                        html.Span(collection.name, className="ms-2 fw-bold")
                    ]),
                    dbc.CardBody([
                        html.Ul([html.Li(f"{product.name} - £{product.price}", className="mb-2") for product in collection.products[:5]])
                    ])
                ], className="h-100 mb-4")
            ], width=12, md=6, lg=4) for i, collection in enumerate(collections)
        ])
    ])

def register_callbacks(app):
    def callback_with_error_handling(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Error in callback: {str(e)}")
                return create_notification(f"An error occurred: {str(e)}", "danger")
        return wrapper

    @app.callback(
        Output("collection-display", "children"),
        Output("search-progress", "disabled"),
        Output("notifications", "data"),
        Output("selected-collection", "data"),
        Input("search-button", "n_clicks"),
        Input("search-progress", "n_intervals"),
        Input("refresh-button", "n_clicks"),
        Input("periodic-refresh", "n_intervals"),
        Input("upload-json", "contents"),
        Input({"type": "collection-radio", "index": ALL}, "value"),
        State("product-input", "value"),
        State("selected-collection", "data"),
        State("upload-json", "filename"),
        State("notifications", "data"),
        prevent_initial_call=True
    )
    @callback_with_error_handling
    def handle_all_operations(search_clicks, search_intervals, refresh_clicks, periodic_intervals, 
                              upload_contents, radio_values, product_name, selected_collection, upload_filename, notifications):
        global is_searching, search_result, collections
        
        ctx = callback_context
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        new_notification = None

        if trigger_id == 'search-button':
            new_notification = handle_search(product_name)
        elif trigger_id == 'search-progress':
            return handle_search_progress(selected_collection, notifications)
        elif trigger_id in ['refresh-button', 'periodic-refresh']:
            new_notification = handle_refresh()
        elif trigger_id == 'upload-json':
            new_notification = handle_upload(upload_contents, upload_filename)
        elif 'collection-radio' in trigger_id:
            selected_collection, new_notification = handle_collection_selection(radio_values, selected_collection)

        if new_notification:
            notifications.append(new_notification)

        return display_collections(selected_collection), True, notifications, selected_collection

    def handle_search(product_name):
        if not product_name:
            raise PreventUpdate
        
        global is_searching, search_result
        is_searching = True
        search_result = None
        threading.Thread(target=lambda: background_search(product_name)).start()
        return create_notification("Searching...", "info")

    def handle_search_progress(selected_collection, notifications):
        global is_searching, search_result, collections
        if is_searching:
            return display_collections(selected_collection), False, notifications, selected_collection

        if search_result is None:
            new_notification = create_notification("Search completed. No new collection found.", "warning")
        else:
            collections.append(search_result)
            new_notification = create_notification("Search completed. New collection added and saved to CSV.", "success")
        
        notifications.append(new_notification)
        return display_collections(selected_collection), True, notifications, selected_collection

    def handle_refresh():
        load_collections()
        return create_notification("Collections refreshed from CSV folder.", "info")

    def handle_upload(upload_contents, upload_filename):
        if upload_contents is None:
            return create_notification("No file selected for import.", "warning")
        
        try:
            content_type, content_string = upload_contents.split(',')
            decoded = base64.b64decode(content_string)
            json_data = json.loads(decoded.decode('utf-8'))
            imported_collection = DataManager.convertDicitonaryToCollection(json_data)
            DataManager.saveCollectionsToCsvFolder("CsvFolder", [imported_collection])
            load_collections()
            return create_notification(f"JSON imported from {upload_filename} and saved as CSV.", "success")
        except Exception as e:
            return create_notification(f"Error importing JSON: {str(e)}", "danger")

    def handle_collection_selection(radio_values, selected_collection):
        selected_values = [value for value in radio_values if value is not None]
        if not selected_values:
            return selected_collection, None

        new_selected = selected_values[0]
        if new_selected == selected_collection:
            return None, create_notification("Collection deselected", "info")
        else:
            return new_selected, create_notification(f"Selected collection: {new_selected}", "info")

    @app.callback(
        Output("download-json", "data"),
        Input("export-button", "n_clicks"),
        State("selected-collection", "data"),
        prevent_initial_call=True
    )
    @callback_with_error_handling
    def export_json(n_clicks, selected_collection):
        if not selected_collection:
            raise PreventUpdate
        
        selected_collection_obj = next((c for c in collections if c.name == selected_collection), None)
        if not selected_collection_obj:
            raise PreventUpdate
        
        collection_dict = DataManager.convertCollectionToDictionary(selected_collection_obj)
        return dict(content=json.dumps(collection_dict, indent=2), filename=f"{selected_collection}.json")

    @app.callback(
        Output("notification-container", "children"),
        Input("notification-interval", "n_intervals"),
        State("notifications", "data"),
    )
    def update_notifications(n, notifications):
        if not notifications:
            return []

        current_time = time.time()
        active_notifications = []
        for notification in notifications:
            age = current_time - notification["created_at"]
            if age < 5:  # Show for 5 seconds
                className = "notification"
                style = {"opacity": 1, "transform": "translateY(0)"}
            elif age < 5.5:  # Fade out for 0.5 seconds
                className = "notification"
                style = {"opacity": 0, "transform": "translateY(-20px)"}
            else:
                continue  # Remove notification

            active_notifications.append(
                dbc.Alert(
                    notification["message"],
                    id=notification["id"],
                    color=notification["color"],
                    dismissable=True,
                    is_open=True,
                    className=className,
                    style=style,
                )
            )

        return active_notifications

    @app.callback(
        Output("notifications", "data", allow_duplicate=True),
        Input({"type": "notification", "index": ALL}, "is_open"),
        State("notifications", "data"),
        prevent_initial_call=True
    )
    def remove_dismissed_notifications(is_open_list, notifications):
        if not callback_context.triggered:
            raise PreventUpdate

        updated_notifications = [
            notif for notif, is_open in zip(notifications, is_open_list)
            if is_open is None or is_open
        ]
        return updated_notifications
