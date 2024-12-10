import unittest
from src.Collection import Collection
from src.Product import Product

class CollectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.testProduct : Product = Product("TestName", 100.0, "https://www.test.co.uk/", 4.5, [])
        self.collection : Collection = Collection("TestName", [self.testProduct])

    # Name Tests
    def testSettingValidName(self) -> None:
        self.collection.name = "NewName"
        self.assertEqual(self.collection.name, "NewName")
    
    def testSettingInvalidNameType(self) -> None:
        with self.assertRaises(TypeError):
            self.collection.name = 123

    def testSettingEmptyName(self) -> None:
        with self.assertRaises(ValueError):
            self.collection.name = ""
    
    # Products Tests
    def testSettingValidProducts(self) -> None:
        newProducts = [Product("TestName", 100.0, "https://www.amazon.co.uk/", 4.5, [])]
        self.collection.products = newProducts
        self.assertEqual(self.collection.products, newProducts)
    
    def testSettingInvalidProductsType(self) -> None:
        with self.assertRaises(TypeError):
            self.collection.products = "Not a list"
    
    # Adding Products Tests
    def testAddingValidProduct(self) -> None:
        newProduct = Product("TestName", 100.0, "https://www.amazon.co.uk/", 4.5, [])
        self.collection.addProduct(newProduct)
        self.assertEqual(self.collection.products, [self.testProduct, newProduct])
    
    def testAddingInvalidProductType(self) -> None:
        with self.assertRaises(TypeError):
            self.collection.addProduct("Not a product")
    
    # Removing Products Tests
    def testRemovingValidProduct(self) -> None:
        self.collection.removeProduct(self.testProduct)
        self.assertEqual(self.collection.products, [])
    
    def testRemovingInvalidProductType(self) -> None:
        with self.assertRaises(TypeError):
            self.collection.removeProduct("Not a product")
    
    def testRemovingProductNotInCollection(self) -> None:
        newProduct = Product("TestName", 100.0, "https://www.amazon.co.uk/", 4.5, [])
        with self.assertRaises(ValueError):
            self.collection.removeProduct(newProduct)
    

if __name__ == '__main__':
    unittest.main()