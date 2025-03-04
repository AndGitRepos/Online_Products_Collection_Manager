from dash import Input, Output, State, ALL, callback_context, no_update, html, dcc
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
from src.callbacks.common_funcs import load_collections, create_notification, verify_pathname_and_get_trigger
from src.backend.Product import Product
from src.backend.DataManager import DataManager
from src.backend.Collection import Collection

# Global variables
collections : List[Collection] = []

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
    """
    Updating the grid of collections that are shown within the collection container
    """
    @app.callback(
        Output('collections-grid', 'children', allow_duplicate=True),
        Output('notification-container', 'children', allow_duplicate=True),
        Input('url', 'pathname'),
        Input('refresh-button', 'n_clicks'),
        Input('initial-refresh', 'n_intervals'),
        prevent_initial_call=True
    )
    def update_collections_grid(pathname, refresh_clicks, initial_refresh):
        global collections
        trigger = verify_pathname_and_get_trigger(callback_context, pathname, '/collections')
        if trigger is None:
            raise PreventUpdate
        
        collections = load_collections()
        collections_grid = [
            html.Div(collection.name, 
                    className="grid-item",
                    id={'type': 'collection-item', 'index': i})
            for i, collection in enumerate(collections)
        ]
        return collections_grid, create_notification("Collections refreshed")
    
    """
    Updating the grid of products of a selected collection within the products container
    """
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
        if trigger is None:
            raise PreventUpdate
        
        if 'index' in trigger:
            clicked_index = json.loads(trigger)['index']
            if clicked_index < len(collections):
                selected_collection = collections[clicked_index]
                products = selected_collection.products
                return [
                    html.Div(
                        product.name,
                        className="grid-item",
                        id={'type': 'product-item', 'product-index': i},
                        title=product.name
                    )
                    for i, product in enumerate(products)
                ], {'display': 'grid'}, {'display': 'none'}, selected_collection.name
        
        return [], {'display': 'grid'}, {'display': 'none'}, None
    
    
    """
    When the add product button is clicked,
    this method creates a temporary product with temporary details that can be edited,
    if the user wants to save the product that they added they will need to press the save buton
    """
    @app.callback(
        Output('product-details', 'children', allow_duplicate=True),
        Output('product-details', 'style', allow_duplicate=True),
        Output('products-grid', 'style', allow_duplicate=True),
        Input('add-product-button', 'n_clicks'),
        State('selected-collection', 'data'),
        State('url', 'pathname'),
        prevent_initial_call=True
    )
    def add_new_product(n_clicks, selected_collection_name, pathname):
        trigger = verify_pathname_and_get_trigger(callback_context, pathname, '/collections')
        if trigger is None or n_clicks is None or n_clicks == 0:
            raise PreventUpdate

        try:
            global collections
            selected_collection = next((c for c in collections if c.name == selected_collection_name), None)
            if selected_collection:
                # Create a new product with temporary values
                new_product = Product(
                    productID=f"temp_{int(time.time())}",
                    name="New Product",
                    price=0.0,
                    url="https://example.com",
                    rating=0.0,
                    description="Product description",
                    reviews=[]
                )
                selected_collection.add_product(new_product)
                
                # Get the index of the new product
                new_product_index = len(selected_collection.products) - 1

                # Return the product details form for the new product
                return [
                    html.H3("Edit New Product Details"),
                    html.Div([
                        html.Label("Name:"),
                        dcc.Input(
                            id='edit-product-name',
                            type='text',
                            value=new_product.name,
                            className='edit-input'
                        ),
                        html.Label("Price (£):"),
                        dcc.Input(
                            id='edit-product-price',
                            type='number',
                            value=new_product.price,
                            step=0.01,
                            className='edit-input'
                        ),
                        html.Label("URL:"),
                        dcc.Input(
                            id='edit-product-url',
                            type='text',
                            value=new_product.url,
                            className='edit-input'
                        ),
                        html.Label("Rating (0-5):"),
                        dcc.Input(
                            id='edit-product-rating',
                            type='number',
                            value=new_product.rating,
                            min=0,
                            max=5,
                            step=0.1,
                            className='edit-input'
                        ),
                        html.Label("Description:"),
                        dcc.Textarea(
                            id='edit-product-description',
                            value=new_product.description,
                            className='edit-textarea'
                        ),
                        html.Label("Reviews:"),
                        html.Div([
                            dcc.Input(
                                id={'type': 'edit-product-review', 'index': 0},
                                type='text',
                                placeholder='Add new review',
                                className='edit-input review-input'
                            )
                        ], id='reviews-container', className='reviews-container'),
                    ], className="edit-form"),
                    html.Div([
                        html.Button(
                            "Back to Products", 
                            id="back-to-products", 
                            n_clicks=0,
                            className="button"
                        ),
                        html.Button(
                            "Save Changes",
                            id="save-product-changes",
                            n_clicks=0,
                            className="button"
                        ),
                        html.Button(
                            "Delete Product", 
                            id="delete-product",
                            className="button",
                            n_clicks=0
                        )
                    ], className="product-actions"),
                    # Hidden store for product index
                    dcc.Store(id='editing-product-index', data=new_product_index)
                ], {'display': 'block'}, {'display': 'none'}

        except Exception as e:
            return no_update, no_update, no_update

        raise PreventUpdate
    
    """
    When a grid product item is selected, this method will change the product container
    to show the selected products details which can then be viewed and edited if they user wants to
    """
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
        if trigger is None:
            raise PreventUpdate
        
        if 'product-index' in trigger:
            clicked_index = json.loads(trigger)['product-index']
            if (n_clicks[clicked_index]):
                selected_collection = next((c for c in collections if c.name == selected_collection_name), None)
                if selected_collection and clicked_index < len(selected_collection.products):
                    product = selected_collection.products[clicked_index]
                    return {'display': 'none'}, {'display': 'block'}, [
                        html.H3("Edit Product Details"),
                        html.Div([
                            html.Label("Name:"),
                            dcc.Input(
                                id='edit-product-name',
                                type='text',
                                value=product.name,
                                className='edit-input'
                            ),
                            html.Label("Price (£):"),
                            dcc.Input(
                                id='edit-product-price',
                                type='number',
                                value=product.price,
                                step=0.01,
                                className='edit-input'
                            ),
                            html.Label("URL:"),
                            dcc.Input(
                                id='edit-product-url',
                                type='text',
                                value=product.url,
                                className='edit-input'
                            ),
                            html.Label("Rating (0-5):"),
                            dcc.Input(
                                id='edit-product-rating',
                                type='number',
                                value=product.rating,
                                min=0,
                                max=5,
                                step=0.1,
                                className='edit-input'
                            ),
                            html.Label("Description:"),
                            dcc.Textarea(
                                id='edit-product-description',
                                value=product.description,
                                className='edit-textarea'
                            ),
                            html.Label("Reviews:"),
                            html.Div([
                                dcc.Input(
                                    id={'type': 'edit-product-review', 'index': i},
                                    type='text',
                                    value=review,
                                    className='edit-input review-input'
                                ) for i, review in enumerate(product.reviews)
                            ] + [
                                dcc.Input(
                                    id={'type': 'edit-product-review', 'index': len(product.reviews)},
                                    type='text',
                                    placeholder='Add new review',
                                    className='edit-input review-input'
                                )
                            ], id='reviews-container', className='reviews-container'),
                        ], className="edit-form"),
                        html.Div([
                            html.Button(
                                "Back to Products", 
                                id="back-to-products", 
                                n_clicks=0,
                                className="button"
                            ),
                            html.Button(
                                "Save Changes",
                                id="save-product-changes",
                                n_clicks=0,
                                className="button"
                            ),
                            html.Button(
                                "Delete Product", 
                                id="delete-product",
                                className="button",
                                n_clicks=0
                            )
                        ], className="product-actions"),
                        # Hidden store for product index
                        dcc.Store(id='editing-product-index', data=clicked_index)
                    ]
        
        return no_update, no_update, no_update
    
    """
    When pressed this will save the current product details within the currently selected collection
    and save this new collection within the CSV folder (overwriting the old CSV file)
    """
    @app.callback(
        Output('products-grid', 'children', allow_duplicate=True),
        Output('products-grid', 'style', allow_duplicate=True),
        Output('product-details', 'style', allow_duplicate=True),
        Output('notification-container', 'children', allow_duplicate=True),
        Input('save-product-changes', 'n_clicks'),
        State('editing-product-index', 'data'),
        State('edit-product-name', 'value'),
        State('edit-product-price', 'value'),
        State('edit-product-url', 'value'),
        State('edit-product-rating', 'value'),
        State('edit-product-description', 'value'),
        State({'type': 'edit-product-review', 'index': ALL}, 'value'),
        State('selected-collection', 'data'),
        State('url', 'pathname'),
        prevent_initial_call=True
    )
    def save_product_changes(n_clicks, product_index, name, price, url, rating, 
                            description, reviews, selected_collection_name, pathname):
        if n_clicks is None or n_clicks == 0:
            raise PreventUpdate
        
        try:
            global collections
            selected_collection = next((c for c in collections if c.name == selected_collection_name), None)
            if selected_collection and product_index < len(selected_collection.products):
                product = selected_collection.products[product_index]
                
                # Update product attributes with new values
                product.name = name
                product.price = float(price)
                product.url = url
                product.rating = float(rating)
                product.description = description
                product.reviews = [rev for rev in reviews if rev is not None and rev.strip()]  # Remove empty reviews
                
                # If this was a new product, generate a proper productID
                if product.productID.startswith('temp_'):
                    product.productID = f"PROD_{int(time.time())}"
                
                # Save the modified collection
                DataManager.save_collections_to_csv_folder("CsvFolder", [selected_collection])
                
                # Refresh collections list
                collections = load_collections()
                
                # Update the products grid
                products_grid = [
                    html.Div(
                        product.name,
                        className="grid-item",
                        id={'type': 'product-item', 'product-index': i},
                        title=product.name
                    )
                    for i, product in enumerate(selected_collection.products)
                ]
                
                return products_grid, {'display': 'grid'}, {'display': 'none'}, create_notification("Product updated successfully")
                
        except ValueError as e:
            return no_update, no_update, no_update, create_notification(f"Error: {str(e)}")
        except Exception as e:
            return no_update, no_update, no_update, create_notification(f"An error occurred: {str(e)}")
        
        raise PreventUpdate

    """
    This method will disable the product details section from being shown within the products container
    and allow the grid list of products to be shown again
    """
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
        Output('products-grid', 'children', allow_duplicate=True),
        Output('products-grid', 'style', allow_duplicate=True),
        Output('product-details', 'style', allow_duplicate=True),
        Output('notification-container', 'children', allow_duplicate=True),
        Input('delete-product', 'n_clicks'),
        State('editing-product-index', 'data'),
        State('selected-collection', 'data'),
        State('url', 'pathname'),
        prevent_initial_call=True
    )
    def delete_product(n_clicks, product_index, selected_collection_name, pathname):
        if n_clicks is None or n_clicks == 0:
            raise PreventUpdate

        try:
            global collections
            selected_collection = next((c for c in collections if c.name == selected_collection_name), None)
            if selected_collection and product_index < len(selected_collection.products):
                # Remove the product
                product = selected_collection.products[product_index]
                selected_collection.remove_product(product)
                
                # Save the modified collection
                DataManager.save_collections_to_csv_folder("CsvFolder", [selected_collection])
                
                # Refresh collections list
                collections = load_collections()
                
                # Update the products grid
                products_grid = [
                    html.Div(
                        product.name,
                        className="grid-item",
                        id={'type': 'product-item', 'product-index': i},
                        title=product.name
                    )
                    for i, product in enumerate(selected_collection.products)
                ]
                
                return products_grid, {'display': 'grid'}, {'display': 'none'}, create_notification("Product deleted successfully")
        except Exception as e:
            return no_update, no_update, no_update, create_notification(f"An error occurred: {str(e)}")

        raise PreventUpdate
    
    @app.callback(
        Output('selected-collection', 'data'),
        [Input({'type': 'collection-item', 'index': ALL}, 'n_clicks')],
        [State({'type': 'collection-item', 'index': ALL}, 'id'),
         State('url', 'pathname')]
    )
    def store_selected_collection(n_clicks, ids, pathname):
        trigger = verify_pathname_and_get_trigger(callback_context, pathname, '/collections')
        if trigger is None:
            raise PreventUpdate
        
        if 'index' in trigger:
            clicked_index = json.loads(trigger)['index']
            print(f"Collection clicked, index: {clicked_index}")
            if clicked_index < len(collections):
                print(f"Selected collection: {collections[clicked_index].name}")
                return collections[clicked_index].name
        
        return no_update
    
    """
    This method is called each time the user changes the data 
    they want to be displayed within the graph container
    """
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
        if trigger is None:
            raise PreventUpdate
        
        selected_collection = None
        if selected_collection_data is not None:
            print(f"Using stored collection: {selected_collection_data}")
            selected_collection = next((c for c in collections if c.name == selected_collection_data), None)
        else:
            print("No collection selected, cannot update graph")
            return px.bar(title="Select a collection to view product data"), [], []
        
        try:
            print(f"Graph type changed to {graph_type}")
            products = selected_collection.products
            print(f"Number of products: {len(products)}")

            df = pd.DataFrame([
                {'Name': product.name, 'Price': product.price, 'Rating': product.rating, 'Reviews-Count': len(product.reviews)}
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
                xaxis = {
                'tickmode': 'array',
                'tickvals': list(range(len(products))),
                'ticktext': df['Name'].str.slice(0, 10).tolist(),
                },
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