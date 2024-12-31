from dash import Input, Output, State, ALL, MATCH, callback_context, no_update, html
from dash.exceptions import PreventUpdate
import time
import threading
import json
import asyncio
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import random
from collections import Counter
from typing import List
from src.WebScraper import WebScraper
from src.DataManager import DataManager
from src.Collection import Collection

# Global variables
collections : List[Collection] = []
search_result : Collection = None
is_searching : bool = False
search_start_time : float = None
last_scrape_duration : float = None

def load_collections() -> None:
    global collections
    try:
        collections = DataManager.load_collections_from_csv_folder("CsvFolder")
        print(f"Loaded {len(collections)} collections from CsvFolder")
    except FileNotFoundError:
        print("CsvFolder not found. Starting with empty collections.")
        collections = []
    except Exception as e:
        print(f"Error loading collections: {str(e)}")
        collections = []

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

def create_notification(message : str, color : int):
    return html.Div([
        html.Div(style={"width": "9px", "height": "56px", "left": "0px", "top": "0px", "position": "absolute", "background": color, "borderRadius": "5px"}),
        html.Div("Notification", style={"left": "19px", "top": "5px", "position": "absolute", "color": "white", "fontSize": "13px", "fontWeight": "700"}),
        html.Div(message, style={"left": "22px", "top": "28px", "position": "absolute", "color": "white", "fontSize": "12px", "fontWeight": "400"}),
    ], style={"width": "177px", "height": "56px", "position": "relative", "background": "#393E46", "borderRadius": "5px", "border": "1px #00ADB5 solid", "marginBottom": "10px"}, id={"type": "notification", "index": time.time()})

def display_collections():
    return [create_collection_item(collection.name, len(collection.products), i) for i, collection in enumerate(collections)]

def format_time(seconds : float) -> str:
    return f"{seconds:.2f}" if seconds is not None else "0.00"

def truncate_name(name : str, max_length : int = 25) -> str:
    return (name[:max_length] + '...') if len(name) > max_length else name

def create_collection_item(name : str, total_products : int, index : int):
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

def generate_word_cloud_data(text, max_words=100):
    words = re.findall(r'\w+', text.lower())
    word_counts = Counter(words)
    max_count = max(word_counts.values())
    return [{'text': word, 'value': count / max_count} for word, count in word_counts.most_common(max_words)]

def register_callbacks(app) -> None:
    @app.callback(
        Output('url', 'pathname'),
        Input('url', 'pathname')
    )
    def update_url(pathname : str):
        return pathname
    
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
    )
    def handle_main_page_updates(pathname, refresh_clicks, search_clicks, search_intervals, 
                                initial_refresh, notification_interval, product_name, current_notifications):
        if pathname != '/':
            return [no_update] * 7

        ctx = callback_context
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'no_trigger'

        # Initialize outputs
        outputs = [no_update] * 7

        if trigger_id in ['initial-refresh', 'refresh-button', 'url']:
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
            collection_dict = DataManager.convert_collection_to_dictionary(collection)
            return dict(content=json.dumps(collection_dict, indent=2), filename=f"{collection.name}.json")
        
        raise PreventUpdate
    
    @app.callback(
        Output('collections-grid', 'children', allow_duplicate=True),
        Output('selected-collection', 'data', allow_duplicate=True),
        Input('url', 'pathname'),
        Input('refresh-button', 'n_clicks'),
        Input('initial-refresh', 'n_intervals'),
        prevent_initial_call=True
    )
    def update_collections_grid(pathname, refresh_clicks, initial_refresh):
        if pathname != '/collections':
            raise PreventUpdate
        
        load_collections()
        collections_grid = [
            html.Div(collection.name, 
                    className="collection-item",
                    id={'type': 'collection-item', 'index': i})
            for i, collection in enumerate(collections)
        ]
        return collections_grid, None

    @app.callback(
        Output('products-grid', 'children'),
        Output('products-grid', 'style'),
        Output('product-details', 'style'),
        Output('selected-product', 'data'),
        Input('selected-collection', 'data'),
        Input({'type': 'collection-item', 'index': ALL}, 'n_clicks'),
        State({'type': 'collection-item', 'index': ALL}, 'id'),
        State('url', 'pathname'),
        prevent_initial_call=True
    )
    def update_products_grid(selected_collection, n_clicks, ids, pathname):
        if pathname != '/collections':
            raise PreventUpdate
        
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger == 'selected-collection':
            return [], {'display': 'grid'}, {'display': 'none'}, None
        
        if 'index' in trigger:
            clicked_index = json.loads(trigger)['index']
            if clicked_index < len(collections):
                selected_collection = collections[clicked_index]
                products = selected_collection.products
                return [
                    html.Div(
                        truncate_name(product.name),
                        className="product-item",
                        id={'type': 'product-item', 'index': i},
                        title=product.name
                    )
                    for i, product in enumerate(products)
                ], {'display': 'grid'}, {'display': 'none'}, selected_collection.name
        
        return [], {'display': 'grid'}, {'display': 'none'}, None

    @app.callback(
        Output('products-grid', 'style', allow_duplicate=True),
        Output('product-details', 'style', allow_duplicate=True),
        Output('product-details', 'children'),
        Input({'type': 'product-item', 'index': ALL}, 'n_clicks'),
        State({'type': 'product-item', 'index': ALL}, 'id'),
        State('selected-product', 'data'),
        State('url', 'pathname'),
        prevent_initial_call=True
    )
    def show_product_details(n_clicks, ids, selected_collection_name, pathname):
        if pathname != '/collections':
            raise PreventUpdate
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if 'index' in trigger:
            clicked_index = json.loads(trigger)['index']
            selected_collection = next((c for c in collections if c.name == selected_collection_name), None)
            if selected_collection and clicked_index < len(selected_collection.products):
                product = selected_collection.products[clicked_index]
                return {'display': 'none'}, {'display': 'block'}, [
                    html.H3(product.name),
                    html.P(f"Price: £{product.price}"),
                    html.P(f"URL: {product.url}"),
                    html.Button("Back to Products", id="back-to-products", n_clicks=0)
                ]
        
        return no_update, no_update, no_update

    @app.callback(
        Output('products-grid', 'style', allow_duplicate=True),
        Output('product-details', 'style', allow_duplicate=True),
        Input('back-to-products', 'n_clicks'),
        prevent_initial_call=True
    )
    def back_to_products(n_clicks):
        if n_clicks > 0:
            return {'display': 'grid'}, {'display': 'none'}
        raise PreventUpdate

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
        [Output('product-graph', 'figure'),
        Output('filter-dropdown', 'options'),
        Output('filter-dropdown', 'value')],
        [Input('graph-type', 'value'),
        Input('filter-dropdown', 'value'),
        Input({'type': 'collection-item', 'index': ALL}, 'n_clicks')],
        [State({'type': 'collection-item', 'index': ALL}, 'id'),
        State('selected-collection', 'data'),
        State('url', 'pathname')]
    )
    def update_graph(graph_type, filter_value, n_clicks, ids, selected_collection_data, pathname):
        print(f"update_graph called with graph_type: {graph_type}, pathname: {pathname}")
        if pathname != '/collections':
            print("Not on collections page, preventing update")
            raise PreventUpdate
        ctx = callback_context
        if not ctx.triggered:
            print("No trigger, preventing update")
            raise PreventUpdate
        
        try:
            trigger = ctx.triggered[0]['prop_id'].split('.')[0]
            print(f"Trigger: {trigger}")
            
            selected_collection = None
            if trigger == 'graph-type':
                print(f"Graph type changed to {graph_type}")
                if selected_collection_data is not None:
                    print(f"Using stored collection: {selected_collection_data}")
                    selected_collection = next((c for c in collections if c.name == selected_collection_data), None)
                else:
                    print("No collection selected, cannot update graph")
                    return px.bar(title="Select a collection to view product data"), [], []
            elif 'index' in trigger:
                clicked_index = json.loads(trigger)['index']
                print(f"Collection clicked, index: {clicked_index}")
                if clicked_index < len(collections):
                    selected_collection = collections[clicked_index]
                    print(f"Selected collection: {selected_collection.name}")
            else:
                print(f"Trigger not recognized: {trigger}")
                return px.bar(title="Select a collection to view product data"), [], []
            
            if selected_collection:
                products = selected_collection.products
                print(f"Number of products: {len(products)}")

                df = pd.DataFrame([
                    {'Name': product.name, 'Price': product.price, 'Rating': product.rating}
                    for product in products
                ])

                if filter_value:
                    df = df[df['Name'].isin(filter_value)]

                print(f"Creating {graph_type} graph")
                if graph_type == 'bar':
                    fig = px.bar(df, x='Name', y='Price', title=f'Product Prices in {selected_collection.name}')
                elif graph_type == 'line':
                    fig = px.line(df, x='Name', y='Price', title=f'Product Prices in {selected_collection.name}')
                elif graph_type == 'wordcloud':
                    text = ' '.join([review for product in products for review in product.reviews])
                    word_cloud_data = generate_word_cloud_data(text)
                    x = [random.uniform(0, 1) for _ in word_cloud_data]
                    y = [random.uniform(0, 1) for _ in word_cloud_data]
                    sizes = [item['value'] * 50 for item in word_cloud_data]
                    texts = [item['text'] for item in word_cloud_data]
                    colors = [item['value'] for item in word_cloud_data]
                    
                    fig = go.Figure(data=[go.Scatter(
                        x=x, y=y, mode='text',
                        text=texts,
                        textfont=dict(size=sizes),
                        marker=dict(color=colors, colorscale='Viridis', showscale=True),
                        hoverinfo='text'
                    )])
                    fig.update_layout(
                        title=f'Review Word Cloud for {selected_collection.name}',
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                    )
                elif graph_type == 'spreadsheet':
                    fig = go.Figure(data=[go.Table(
                        header=dict(values=list(df.columns),
                                    fill_color='paleturquoise',
                                    align='left'),
                        cells=dict(values=[df[col] for col in df.columns],
                                fill_color='lavender',
                                align='left'))
                    ])
                    fig.update_layout(title=f'Spreadsheet View: {selected_collection.name}')

                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )

                filter_options = [{'label': name, 'value': name} for name in df['Name']]
                print("Returning updated graph and filter options")
                return fig, filter_options, filter_value if filter_value else []
            else:
                print("No collection selected")
                return px.bar(title="Select a collection to view product data"), [], []

        except Exception as e:
            print(f"Error in update_graph: {str(e)}")
            import traceback
            print(traceback.format_exc())
        
        print("Returning default empty graph")
        return px.bar(title="Select a collection to view product data"), [], []
    
    @app.callback(
        Output('selected-collection', 'data'),
        [Input({'type': 'collection-item', 'index': ALL}, 'n_clicks')],
        [State({'type': 'collection-item', 'index': ALL}, 'id')]
    )
    def store_selected_collection(n_clicks, ids):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]
        if 'index' in trigger:
            clicked_index = json.loads(trigger)['index']
            if clicked_index < len(collections):
                return collections[clicked_index].name
        
        return None
