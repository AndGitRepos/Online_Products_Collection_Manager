from src.Collection import Collection
from src.Product import Product
from typing import List, Dict, Any
import json
import csv
import os

# Might be best as a static class
# Each Dict[str, Any] is a collection
# To store a bunch of collections could use
# Have it store data within spreadsheet file where each table is the collections name
class DataManager:
    def __init__(self):
        raise TypeError("This is a utility class and cannot be instantiated")

    @staticmethod
    def loadCollectionsFromCsvFolder(csvFolderName : str) -> List[Collection]:
        if not isinstance(csvFolderName, str):
            raise TypeError("Filename must be a string")
        elif not csvFolderName.exists():
            raise FileNotFoundError("Folder not found")

        collections = []
        for path, folders, files in os.walk(csvFolderName):
            for file in files:
                if file.endswith(".csv"):
                    with open(os.path.join(path, file), "r") as csvFile:
                        reader = csv.reader(csvFile)
                        next(reader)
                        products = []
                        for row in reader:
                            products.append(Product(row[0], float(row[1]), row[2], float(row[3]), row[4]))
                        collections.append(Collection(file[:-4], products))
        return collections

    # Maybe change to only save one collection per csv file
    # And make it so that it saves all collections to one spreadsheet
    # where each table within the spreadsheet is one collection
    # If collection with same name exists, then come up with a way to have 
    # past and present data to allow for data analysis
    @staticmethod
    def saveCollectionsToCsvFolder(csvFolderName : str, collections : List[Collection]) -> None:
        if not isinstance(csvFolderName, str):
            raise TypeError("Filename must be a string")
        elif not isinstance(collections, list):
            raise TypeError("Collections must be a list")
        elif not all(isinstance(collection, Collection) for collection in collections):
            raise TypeError("All collections must be a Collection")
        
        if not csvFolderName.exists():
            csvFolderName.mkdir()
        
        # Iterate through collection, creating a csv for each one
        for collection in collections:
            with open(os.path.join(csvFolderName, collection.name + "_Collection.csv"), "w") as file:
                writer = csv.writer(file)
                writer.writerow(["name", "price", "url", "rating", "reviews"])
                for product in collection.products:
                    writer.writerow([product.name, product.price, product.url, product.rating, product.reviews])
        

    @staticmethod
    def loadCollectionFromJson(filePath : str) -> Collection:
        if not isinstance(filePath, str):
            raise TypeError("Filename must be a string")
        elif not filePath.endswith(".json"):
            raise ValueError("Filename must end with .json")
        elif not filePath.exists():
            raise FileNotFoundError("File not found")
        
        with open(filePath, "r") as file:
            collectionDict = json.load(file)
        return DataManager.convertDicitonaryToCollection(collectionDict)
    
    @staticmethod
    def saveCollectionToJson(directoryPath : str, collection : Collection):
        if not isinstance(directoryPath, str):
            raise TypeError("Directory path must be a string")
        elif not isinstance(collection, Collection):
            raise TypeError("Collection must be a Collection")
        elif not directoryPath.exists():
            raise FileNotFoundError("Directory not found")
        
        collectionDict = DataManager.convertCollectionToDictionary(collection)
        with open(os.path.join(directoryPath, collection.name + "_Collection.json"), "w") as file:
            json.dump(collectionDict, file)

    """
    Dictionary format:
    {
        "name": "Collection Name",
        "products": [
            {
                "name": "Product Name",
                "price": 100.0,
                "url": "https://www.example.co.uk/",
                "rating": 4.5,
                "reviews": ["Review 1", "Review 2"]
            },
            ...
        ]
    }
    """
    @staticmethod
    def convertDicitonaryToCollection(dictionary : Dict[str, Any]) -> Collection:
        if not isinstance(dictionary, dict):
            raise TypeError("Dictionary must be a dictionary")
        elif "name" not in dictionary:
            raise ValueError("Dictionary must contain a name (collection name)")
        elif "products" not in dictionary:
            raise ValueError("Dictionary must contain products (list of products)")
        elif not isinstance(dictionary["products"], list):
            raise TypeError("Products must be a list")

        collection : Collection = Collection(dictionary["name"], [])
        for product in dictionary["products"]:
            if not isinstance(product, dict):
                raise TypeError("Product must be a dictionary")
            collection.addProduct(Product(product["name"], product["price"], product["url"], product["rating"], product["reviews"]))
    
    @staticmethod
    def convertCollectionToDictionary(collection : Collection) -> Dict[str, Any]:
        if not isinstance(collection, Collection):
            raise TypeError("Collection must be a Collection")

        dictionary : Dict[str, Any] = {
            "name": collection.name,
            "products": []
        }
        for product in collection.products:
            dictionary["products"].append({
                "name": product.name,
                "price": product.price,
                "url": product.url,
                "rating": product.rating,
                "reviews": product.reviews
            })
        return dictionary