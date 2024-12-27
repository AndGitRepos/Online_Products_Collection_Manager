import sys
import os
import time
import subprocess
import pkg_resources
from pathlib import Path
import base64
import json
import io

# Get the path to the project root directory
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def install_dependencies(requirements_file='main/requirements.txt'):
    required = set()
    with open(requirements_file, 'r') as f:
        for line in f:
            package = line.strip()
            if package and not package.startswith('#'):
                required.add(package)

    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = required - installed

    if missing:
        python = sys.executable
        subprocess.check_call([python, '-m', 'pip', 'install', '-r', requirements_file], stdout=subprocess.DEVNULL)
        print(f"Installed missing dependencies: {', '.join(missing)}")
    else:
        print("All dependencies are already installed.")

if __name__ == "__main__":
    requirements_file = Path('main/requirements.txt')
    if not requirements_file.exists():
        print("No requirements file found.")
        sys.exit(1)

    install_dependencies(str(requirements_file))

    # Now that dependencies are installed, we can import them
    import dash
    from dash import dcc, html, Input, Output, State, ALL
    import dash_bootstrap_components as dbc
    from dash.exceptions import PreventUpdate
    import asyncio
    import threading
    from src.WebScraper import WebScraper
    from src.DataManager import DataManager
    from src.Collection import Collection

    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    # Global variables to store collections and search result
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

    app.layout = dbc.Container([
        html.H1("Online Products Collection Manager"),
        
        dbc.Row([
            dbc.Col([
                dbc.Input(id="product-input", placeholder="Enter product name", type="text"),
                dbc.Button("Search", id="search-button", color="primary", className="mt-2 me-2"),
                dbc.Button("Refresh Collections", id="refresh-button", color="secondary", className="mt-2 me-2"),
                dcc.Upload(
                    id='upload-json',
                    children=dbc.Button('Import JSON', color="info", className="mt-2 me-2"),
                    multiple=False
                ),
                dbc.Button("Export JSON", id="export-button", color="success", className="mt-2"),
            ], width=12)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dcc.Loading(
                    id="loading",
                    type="default",
                    children=[html.Div(id="collection-display")]
                ),
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                html.Div(id="operation-status", className="mt-2")
            ])
        ]),

        dcc.Interval(id='search-progress', interval=1000, n_intervals=0, disabled=True),
        dcc.Interval(id='periodic-refresh', interval=300000, n_intervals=0),  # 5 minutes = 300000 ms
        dcc.Store(id='selected-collection', data=None),
        dcc.Download(id="download-json")
    ])

    def background_search(product_name):
        global search_result, is_searching
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        search_result = loop.run_until_complete(WebScraper.searchForProducts(product_name))
        loop.close()
        is_searching = False
        if search_result:
            DataManager.saveCollectionsToCsvFolder("CsvFolder", [search_result])

    @app.callback(
        Output("collection-display", "children"),
        Output("search-progress", "disabled"),
        Output("operation-status", "children"),
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
    )
    def handle_all_operations(search_clicks, search_intervals, refresh_clicks, periodic_intervals, 
                              upload_contents, radio_values, product_name, selected_collection, upload_filename):
        global is_searching, search_result, collections
        
        ctx = dash.callback_context
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'search-button':
            if not product_name:
                raise PreventUpdate
            
            is_searching = True
            search_result = None
            # Start the background task
            threading.Thread(target=lambda: background_search(product_name)).start()
            return display_collections(selected_collection), False, "Searching...", selected_collection

        elif trigger_id == 'search-progress':
            if is_searching:
                return display_collections(selected_collection), False, "Searching...", selected_collection

            if search_result is None:
                return display_collections(selected_collection), True, "Search completed. No new collection found.", selected_collection

            collections.append(search_result)
            
            return display_collections(selected_collection), True, "Search completed. New collection added and saved to CSV.", selected_collection

        elif trigger_id in ['refresh-button', 'periodic-refresh']:
            load_collections()
            return display_collections(selected_collection), True, "Collections refreshed from CSV folder.", selected_collection

        elif trigger_id == 'upload-json':
            if upload_contents is not None:
                content_type, content_string = upload_contents.split(',')
                decoded = base64.b64decode(content_string)
                try:
                    json_data = json.loads(decoded.decode('utf-8'))
                    imported_collection = DataManager.convertDicitonaryToCollection(json_data)
                    DataManager.saveCollectionsToCsvFolder("CsvFolder", [imported_collection])
                    load_collections()
                    return display_collections(selected_collection), True, f"JSON imported from {upload_filename} and saved as CSV.", selected_collection
                except Exception as e:
                    return display_collections(selected_collection), True, f"Error importing JSON: {str(e)}", selected_collection
            return display_collections(selected_collection), True, "No file selected for import.", selected_collection

        elif 'collection-radio' in trigger_id:
            selected_values = [value for value in radio_values if value is not None]
            if selected_values:
                new_selected = selected_values[0]
                if new_selected == selected_collection:
                    # If the same collection is selected again, deselect it
                    return display_collections(None), True, "Collection deselected", None
                else:
                    return display_collections(new_selected), True, f"Selected collection: {new_selected}", new_selected

        return display_collections(selected_collection), True, "", selected_collection

    @app.callback(
        Output("download-json", "data"),
        Input("export-button", "n_clicks"),
        State("selected-collection", "data"),
        prevent_initial_call=True
    )
    def export_json(n_clicks, selected_collection):
        if not selected_collection:
            raise PreventUpdate
        
        selected_collection_obj = next((c for c in collections if c.name == selected_collection), None)
        if not selected_collection_obj:
            raise PreventUpdate
        
        collection_dict = DataManager.convertCollectionToDictionary(selected_collection_obj)
        return dict(content=json.dumps(collection_dict, indent=2), filename=f"{selected_collection}.json")

    def display_collections(selected_collection):
        if not collections:
            return html.Div("No collections to display.")
        
        return html.Div([
            html.H2("All Collections"),
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
                            html.Span(collection.name, className="ms-2")
                        ]),
                        dbc.CardBody([
                            html.Ul([html.Li(f"{product.name} - £{product.price}") for product in collection.products[:5]])
                        ])
                    ], color="primary" if selected_collection == collection.name else "light", inverse=selected_collection == collection.name, className="mb-3")
                ], width=4) for i, collection in enumerate(collections)
            ], className="overflow-auto flex-nowrap")
        ])

    app.run_server(debug=True)
