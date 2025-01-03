from dash import Input, Output, State, ALL, callback_context, no_update, html
from dash.exceptions import PreventUpdate
import time
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import random
from collections import Counter
from typing import List
from src.dashApp.callbacks.common_funcs import load_collections, create_notification, verify_pathname_and_get_trigger
from src.backend.DataManager import DataManager
from src.backend.Collection import Collection

# Global variables
collections : List[Collection] = []

"""
Truncates (shortens) a string to a length passed in or default 25
"""
def truncate_name(name : str, max_length : int = 25) -> str:
    return (name[:max_length] + '...') if len(name) > max_length else name

"""
Using regex to find all of the words within a given text,
Initialising Counter with the gathered words and aggregating 
the most commonly used words with their value depending on how 
common it was
"""
def generate_word_cloud_data(text, max_words=100):
    words = re.findall(r'\w+', text.lower())
    word_counts = Counter(words)
    max_count = max(word_counts.values())
    return [{'text': word, 'value': count / max_count} for word, count in word_counts.most_common(max_words)]

"""
This method allows the main app file (app.py) to only need 
to call one method to register all callbacks for the collection page
"""
def register_collections_callbacks(app) -> None:
    @app.callback(
        Output('collections-grid', 'children', allow_duplicate=True),
        #Output('notification-container', 'children', allow_duplicate=True),
        Input('url', 'pathname'),
        Input('refresh-button', 'n_clicks'),
        Input('initial-refresh', 'n_intervals'),
        prevent_initial_call=True
    )
    def update_collections_grid(pathname, refresh_clicks, initial_refresh):
        global collections
        trigger = verify_pathname_and_get_trigger(callback_context, pathname, '/collections')
        if trigger == None:
            raise PreventUpdate
        
        collections = load_collections()
        collections_grid = [
            html.Div(collection.name, 
                    className="collection-item",
                    id={'type': 'collection-item', 'index': i})
            for i, collection in enumerate(collections)
        ]
        return collections_grid#, create_notification("Collections refreshed")
    
    @app.callback(
        Output('products-grid', 'children'),
        Output('products-grid', 'style'),
        Output('product-details', 'style'),
        Output('selected-collection', 'data', allow_duplicate=True),
        Input('selected-collection', 'data'),
        Input({'type': 'collection-item', 'index': ALL}, 'n_clicks'),
        State({'type': 'collection-item', 'index': ALL}, 'id'),
        State('url', 'pathname'),
        prevent_initial_call=True
    )
    def update_products_grid(selected_collection, n_clicks, ids, pathname):
        trigger = verify_pathname_and_get_trigger(callback_context, pathname, '/collections')
        if trigger == None:
            raise PreventUpdate
        
        if 'index' in trigger:
            clicked_index = json.loads(trigger)['index']
            if clicked_index < len(collections):
                selected_collection = collections[clicked_index]
                products = selected_collection.products
                return [
                    html.Div(
                        truncate_name(product.name),
                        className="product-item",
                        id={'type': 'product-item', 'product-index': i},
                        title=product.name
                    )
                    for i, product in enumerate(products)
                ], {'display': 'grid'}, {'display': 'none'}, selected_collection.name
        
        return [], {'display': 'grid'}, {'display': 'none'}, None
    
    @app.callback(
        Output('products-grid', 'style', allow_duplicate=True),
        Output('product-details', 'style', allow_duplicate=True),
        Output('product-details', 'children'),
        Input({'type': 'product-item', 'product-index': ALL}, 'n_clicks'),
        State({'type': 'product-item', 'product-index': ALL}, 'id'),
        State('selected-collection', 'data'),
        State('url', 'pathname'),
        prevent_initial_call=True
    )
    def show_product_details(n_clicks, ids, selected_collection_name, pathname):
        trigger = verify_pathname_and_get_trigger(callback_context, pathname, '/collections')
        if trigger == None:
            raise PreventUpdate
        
        if 'product-index' in trigger:
            clicked_index = json.loads(trigger)['product-index']
            if (n_clicks[clicked_index]):
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
        Output('selected-collection', 'data'),
        [Input({'type': 'collection-item', 'index': ALL}, 'n_clicks')],
        [State({'type': 'collection-item', 'index': ALL}, 'id'),
         State('url', 'pathname')]
    )
    def store_selected_collection(n_clicks, ids, pathname):
        trigger = verify_pathname_and_get_trigger(callback_context, pathname, '/collections')
        if trigger == None:
            raise PreventUpdate
        
        if 'index' in trigger:
            clicked_index = json.loads(trigger)['index']
            print(f"Collection clicked, index: {clicked_index}")
            if clicked_index < len(collections):
                print(f"Selected collection: {collections[clicked_index].name}")
                return collections[clicked_index].name
        
        return no_update
    
    @app.callback(
        [Output('product-graph', 'figure'),
        Output('filter-product', 'options'),
        Output('filter-product', 'value')],
        [Input('graph-type', 'value'),
        Input('filter-product', 'value'),
        Input('filter-product-data', 'value'),
        Input('selected-collection', 'data'),
        State('url', 'pathname')]
    )
    def update_graph(graph_type, filter_product_value, filter_product_data_value, selected_collection_data, pathname):
        trigger = verify_pathname_and_get_trigger(callback_context, pathname, '/collections')
        if trigger == None:
            raise PreventUpdate
        
        selected_collection = None
        if selected_collection_data is not None:
            print(f"Using stored collection: {selected_collection_data}")
            selected_collection = next((c for c in collections if c.name == selected_collection_data), None)
        else:
            print("No collection selected, cannot update graph")
            return px.bar(title="Select a collection to view product data"), [], []
        
        try:
            if trigger == 'graph-type' or 'selected-collection' or trigger == "filter-product":
                print(f"Graph type changed to {graph_type}")
                products = selected_collection.products
                print(f"Number of products: {len(products)}")

                df = pd.DataFrame([
                    {'Name': truncate_name(product.name, 20), 'Price': product.price, 'Rating': product.rating, 'Reviews-Count': len(product.reviews)}
                    for product in products
                ])

                if filter_product_value:
                    df = df[df['Name'].isin(filter_product_value)]

                print(f"Creating {graph_type} graph")
                if graph_type == 'bar':
                    fig = px.bar(df, x='Name', y=filter_product_data_value, title=f'Product {filter_product_data_value} in {selected_collection.name}')
                elif graph_type == 'line':
                    fig = px.line(df, x='Name', y=filter_product_data_value, title=f'Product {filter_product_data_value} in {selected_collection.name}')
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
                                    fill_color='#FFB507',
                                    align='left'),
                        cells=dict(values=[df[col] for col in df.columns],
                                fill_color='#393E46',
                                align='left'))
                    ])
                    fig.update_layout(title=f'Spreadsheet View: {selected_collection.name}')

                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#EEEEEE'
                )

                filter_options = [{'label': name, 'value': name} for name in df['Name']]
                print("Returning updated graph and filter options")
                return fig, filter_options, filter_product_value if filter_product_value else []
        except Exception as e:
            print(f"Error in update_graph: {str(e)}")
            import traceback
            print(traceback.format_exc())
        
        print("Returning default empty graph")
        return px.bar(title="Select a collection to view product data"), [], []