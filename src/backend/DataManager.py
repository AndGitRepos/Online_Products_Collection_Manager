from src.backend.Collection import Collection
from src.backend.Product import Product
from typing import List, Dict, Any
import json
import io
import csv
import sys
import os
import ast

csv.field_size_limit(sys.maxsize)

"""
This class is used to perform all data operations.
Loading and uploading of data structures.
Conversions between classes and data structures and vice-versa.
"""
class DataManager:
    def __init__(self):
        raise TypeError("This is a utility class and cannot be instantiated")

    """
    Loads all csvs within folder and converts them to collections
    
    @param csvFolderName: The name of the folder containing the csvs
    @return: A list of collections
    """
    @staticmethod
    def load_collections_from_csv_folder(csvFolderName : str) -> List[Collection]:
        if not isinstance(csvFolderName, str):
            raise TypeError("Filename must be a string")
        elif not os.path.exists(csvFolderName):
            raise FileNotFoundError("Folder not found")

        collections : List[Collection] = []
        for path, folders, files in os.walk(csvFolderName):
            for file in files:
                if file.endswith(".csv"):
                    with open(os.path.join(path, file), "r") as csvFile:
                        reader = csv.reader(csvFile)
                        next(reader)
                        products = []
                        for row in reader:
                            # Reading all of the products data
                            productID = row[0]
                            name = row[1]
                            price = float(row[2])
                            url = row[3]
                            rating = float(row[4])
                            description = row[5]
                            reviews = ast.literal_eval(row[6])
                            # Instantiating the product using the data from the file
                            products.append(Product(
                                productID=productID,
                                name=name,
                                price=price,
                                url=url,
                                rating=rating,
                                description=description,
                                reviews=reviews
                            ))
                        # Creating a collection by passing in the collection name and its products
                        collections.append(Collection(file[:-4], products))
        return collections

    """
    Saves a list of collections into a folder.
    A single collection is converted to a single CSV file.
    """
    @staticmethod
    def save_collections_to_csv_folder(csvFolderName : str, collections : List[Collection]) -> None:
        if not isinstance(csvFolderName, str):
            raise TypeError("Filename must be a string")
        elif not isinstance(collections, list):
            raise TypeError("Collections must be a list")
        elif not all(isinstance(collection, Collection) for collection in collections):
            raise TypeError("All collections must be a Collection")
        
        if not os.path.exists(csvFolderName):
            os.mkdir(csvFolderName)
        
        # Iterate through each collection, creating a csv for each one
        for collection in collections:
            with open(os.path.join(csvFolderName, collection.name + ".csv"), "w") as file:
                writer = csv.writer(file)
                # Writing the csv header with each columns name
                writer.writerow(["productID", "name", "price", "url", "rating", "description", "reviews"])
                for product in collection.products:
                    writer.writerow([
                        product.productID,
                        product.name,
                        product.price,
                        product.url,
                        product.rating,
                        product.description,
                        product.reviews])

        

    """
    Loads json data from given path and converts it to a collection
    
    @param filePath: The path to the json file
    @return: The collection loaded from the json file
    """
    @staticmethod
    def load_collection_from_json(filePath : str) -> Collection:
        if not isinstance(filePath, str):
            raise TypeError("Filename must be a string")
        elif not filePath.endswith(".json"):
            raise ValueError("Filename must end with .json")
        elif not os.path.exists(filePath):
            raise FileNotFoundError("File not found")
        
        with open(filePath, "r") as file:
            collectionDict = json.load(file)
            
        return DataManager.convert_dictionary_to_collection(collectionDict)
    
    """
    Saves a collection to a json file within a directory(folder)
    
    @param directoryPath: The path to the directory where the json file will be saved
    @param collection: The collection to be saved
    """
    @staticmethod
    def save_collection_to_json(directoryPath : str, collection : Collection) -> None:
        if not isinstance(directoryPath, str):
            raise TypeError("Directory path must be a string")
        elif not isinstance(collection, Collection):
            raise TypeError("Collection must be a Collection")
        elif not os.path.exists(directoryPath):
            os.mkdir(directoryPath)
        
        collectionDict = DataManager.convert_collection_to_dictionary(collection)
        with open(os.path.join(directoryPath, collection.name + ".json"), "w") as file:
            json.dump(collectionDict, file)

    """
    Dictionary format:
    {
        "name": "Collection Name",
        "products": [
            {
                "productID": "123",
                "name": "Product Name",
                "price": 100.0,
                "url": "https://www.example.co.uk/",
                "rating": 4.5,
                "description": "Product Description",
                "reviews": ["Review 1", "Review 2"]
            },
            ...
        ]
    }
    """
    @staticmethod
    def convert_dictionary_to_collection(dictionary: Dict[str, Any]) -> Collection:
        if not isinstance(dictionary, dict):
            raise TypeError("Dictionary must be a dictionary")
        elif "name" not in dictionary:
            raise ValueError("Dictionary must contain a name (collection name)")
        elif "products" not in dictionary:
            raise ValueError("Dictionary must contain products (list of products)")
        elif not isinstance(dictionary["products"], list):
            raise TypeError("Products must be a list")

        collection: Collection = Collection(dictionary["name"], [])
        for product_dict in dictionary["products"]:
            if not isinstance(product_dict, dict):
                raise TypeError("Product must be a dictionary")
            
            # Extract product data with proper type conversion
            product = Product(
                productID=product_dict["productID"],
                name=product_dict["name"],
                price=float(product_dict["price"]),
                url=product_dict["url"],
                rating=float(product_dict["rating"]),
                description=product_dict["description"],
                reviews=product_dict["reviews"]
            )
            collection.addProduct(product)
        return collection
    """
    Converts a collection into its dictionary format structure
    """
    @staticmethod
    def convert_collection_to_dictionary(collection: Collection) -> Dict[str, Any]:
        if not isinstance(collection, Collection):
            raise TypeError("Collection must be a Collection")

        dictionary: Dict[str, Any] = {
            "name": collection.name,
            "products": []
        }
        
        for product in collection.products:
            product_dict = {
                "productID": product.productID,
                "name": product.name,
                "price": product.price,
                "url": product.url,
                "rating": product.rating,
                "description": product.description,
                "reviews": product.reviews
            }
            dictionary["products"].append(product_dict)
        
        return dictionary
    """
    This method is used to convert a collection into CSV 
    format but store this format within a String and return it
    """
    @staticmethod
    def convert_collection_to_csv_string(collection: Collection) -> str:
        if not isinstance(collection, Collection):
            raise TypeError("Collection must be a Collection")

        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["productID", "name", "price", "url", "rating", "description", "reviews"])
        
        # Write product data
        for product in collection.products:
            writer.writerow([
                product.productID,
                product.name,
                product.price,
                product.url,
                product.rating,
                product.description,
                json.dumps(product.reviews)  # Convert reviews list to JSON string
            ])
        
        return output.getvalue()
    
    """
    Deletes a given collections data that is stored within 
    the CSV and JSON folders
    """
    @staticmethod
    def delete_collection(collection_name: str) -> None:
        csv_path = os.path.join("CsvFolder", f"{collection_name}.csv")
        json_path = os.path.join("JsonFolder", f"{collection_name}.json")
        
        if os.path.exists(csv_path):
            os.remove(csv_path)
        
        if os.path.exists(json_path):
            os.remove(json_path)