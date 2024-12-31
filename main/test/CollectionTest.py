import unittest
from src.Collection import Collection
from src.Product import Product

class CollectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.testProduct : Product = Product("ProductID", "TestName", 100.0, "https://www.test.co.uk/", 4.5, "Description", [])
        self.newProduct : Product = Product("ProductID", "TestName", 100.0, "https://www.amazon.co.uk/", 4.5, "Description", [])
        self.collection : Collection = Collection("TestName", [self.testProduct])

    # Name Tests
    def test_setting_valid_name(self) -> None:
        self.collection.name = "NewName"
        self.assertEqual(self.collection.name, "NewName")
    
    def test_setting_invalid_name_type(self) -> None:
        with self.assertRaises(TypeError):
            self.collection.name = 123

    def test_setting_empty_name(self) -> None:
        with self.assertRaises(ValueError):
            self.collection.name = ""
    
    # Products Tests
    def test_setting_valid_products(self) -> None:
        self.collection.products = [self.newProduct]
        self.assertEqual(self.collection.products, [self.newProduct])
    
    def test_setting_invalid_products_type(self) -> None:
        with self.assertRaises(TypeError):
            self.collection.products = "Not a list"
    
    # Adding Products Tests
    def test_adding_valid_product(self) -> None:
        self.collection.addProduct(self.newProduct)
        self.assertEqual(self.collection.products, [self.testProduct, self.newProduct])
    
    def test_adding_invalid_product_type(self) -> None:
        with self.assertRaises(TypeError):
            self.collection.addProduct("Not a product")
    
    # Removing Products Tests
    def test_removing_valid_products(self) -> None:
        self.collection.removeProduct(self.testProduct)
        self.assertEqual(self.collection.products, [])
    
    def test_removing_invalid_product_type(self) -> None:
        with self.assertRaises(TypeError):
            self.collection.removeProduct("Not a product")
    
    def test_removing_product_not_in_collections(self) -> None:
        with self.assertRaises(ValueError):
            self.collection.removeProduct(self.newProduct)
    

if __name__ == '__main__':
    unittest.main()