import unittest
from src.DataManager import DataManager
from src.Collection import Collection
from src.Product import Product
import os
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
    
    def testSaveCollectionAsCsv(self) -> None:
        DataManager.saveCollectionsToCsvFolder("CsvTestFolder", [self.testCollection])
        self.assertTrue(os.path.exists(os.path.join("CsvTestFolder", self.testCollection.name + ".csv")))
        with open(os.path.join("CsvTestFolder", self.testCollection.name + ".csv"), "r") as f:
            csvLines: List[str] = f.readlines()
            self.assertEqual(csvLines[0], "productID,name,price,url,rating,description,reviews\n")
            self.assertEqual(csvLines[1], "productID,productName,10.0,https://www.test.co.uk/,3.5,description,\"['review1', 'review2']\"\n")
            
    def testLoadCollectionsFromCsvFolder(self) -> None:
        DataManager.saveCollectionsToCsvFolder("CsvTestFolder", [self.testCollection])
        collections: List[Collection] = DataManager.loadCollectionsFromCsvFolder("CsvTestFolder")
        self.assertEqual(len(collections), 1)
        self.assertEqual(collections[0], self.testCollection)
    
    def testSaveCollectionAsJson(self) -> None:
        DataManager.saveCollectionToJson("JsonTestFolder", self.testCollection)
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
    
    def testLoadCollectionFromJson(self) -> None:
        DataManager.saveCollectionToJson("JsonTestFolder", self.testCollection)
        collection: Collection = DataManager.loadCollectionFromJson(os.path.join("JsonTestFolder", self.testCollection.name + ".json"))
        self.assertEqual(collection, self.testCollection)

if __name__ == '__main__':
    unittest.main()