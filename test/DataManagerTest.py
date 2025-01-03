import unittest
import os
from src.backend.DataManager import DataManager
from src.backend.Collection import Collection
from src.backend.Product import Product
from typing import List

class DataManagerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.testCollection: Collection = Collection("test", 
            [Product(
                productID="productID",
                name="productName",
                price=10.0,
                url="https://www.test.co.uk/",
                rating=3.5,
                description="description",
                reviews=["review1", "review2"]
            )])
    
    def test_save_collection_as_csv(self) -> None:
        DataManager.save_collections_to_csv_folder("CsvTestFolder", [self.testCollection])
        self.assertTrue(os.path.exists(os.path.join("CsvTestFolder", self.testCollection.name + ".csv")))
        with open(os.path.join("CsvTestFolder", self.testCollection.name + ".csv"), "r") as f:
            csvLines: List[str] = f.readlines()
            self.assertEqual(csvLines[0], "productID,name,price,url,rating,description,reviews\n")
            self.assertEqual(csvLines[1], "productID,productName,10.0,https://www.test.co.uk/,3.5,description,\"['review1', 'review2']\"\n")
            
    def test_load_collections_from_csv_folder(self) -> None:
        DataManager.save_collections_to_csv_folder("CsvTestFolder", [self.testCollection])
        collections: List[Collection] = DataManager.load_collections_from_csv_folder("CsvTestFolder")
        self.assertEqual(len(collections), 1)
        self.assertEqual(collections[0], self.testCollection)
    
    def test_save_collection_as_json(self) -> None:
        DataManager.save_collection_to_json("JsonTestFolder", self.testCollection)
        self.assertTrue(os.path.exists(os.path.join("JsonTestFolder", self.testCollection.name + ".json")))
        with open(os.path.join("JsonTestFolder", self.testCollection.name + ".json"), "r") as f:
            self.assertEqual(f.read(), 
                '{"name": "test", "products": [{'
                '"productID": "productID", '
                '"name": "productName", '
                '"price": 10.0, '
                '"url": "https://www.test.co.uk/", '
                '"rating": 3.5, '
                '"description": "description", '
                '"reviews": ["review1", "review2"]'
                '}]}')
    
    def test_load_collection_from_json(self) -> None:
        DataManager.save_collection_to_json("JsonTestFolder", self.testCollection)
        collection: Collection = DataManager.load_collection_from_json(os.path.join("JsonTestFolder", self.testCollection.name + ".json"))
        self.assertEqual(collection, self.testCollection)

if __name__ == '__main__':
    unittest.main()