from dash import html
import time
from typing import List
from src.backend.DataManager import DataManager
from src.backend.Collection import Collection

def load_collections() -> List[Collection]:
    collections = []
    try:
        collections = DataManager.load_collections_from_csv_folder("CsvFolder")
        print(f"Loaded {len(collections)} collections from CsvFolder")
    except FileNotFoundError:
        print("CsvFolder not found. Starting with empty collections.")
    except Exception as e:
        print(f"Error loading collections: {str(e)}")
    return collections

def create_notification(message : str):
    return html.Div([
        html.Div(className="notification-stripe"),
        html.Div("Notification", className="notification-title"),
        html.Div(message, className="notification-text"),
    ], className="notification-box", id={"type": "notification", "index": time.time()})

"""
Verifys that the current webpages pathname is expected
Also verifys if there is a trigger for the callee and if so returns it
"""
def verify_pathname_and_get_trigger(callback_context, pathname, expected_pathname):
    if pathname != expected_pathname:
        #print(f"Not on {expected_pathname} page, preventing update")
        return None
    if not callback_context.triggered:
        print("No trigger, preventing update")
        return None
    
    return callback_context.triggered[0]['prop_id'].split('.')[0]