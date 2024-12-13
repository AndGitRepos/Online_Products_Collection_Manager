import unittest
from src.Product import Product

class ProductTest(unittest.TestCase):
    def setUp(self) -> None:
        # This will run before each test method
        self.testProduct : Product = Product("ProductID", "TestName", 100.0, "https://www.test.co.uk/", 4.5, "Description", [])
    
    # Product ID Tests
    def testSettingValidProductID(self) -> None:
        self.testProduct.productID = "ProductID2"
        self.assertEqual(self.testProduct.productID, "ProductID2")
    
    def testSettingInvalidProductIDType(self) -> None:
        with self.assertRaises(TypeError):
            self.testProduct.productID = 2
    
    def testSettingEmptyProductID(self) -> None:
        with self.assertRaises(ValueError):
            self.testProduct.productID = ""

    # Name Tests
    def testSettingValidName(self) -> None:
        self.testProduct.name = "iPhone"
        self.assertEqual(self.testProduct.name, "iPhone")
    
    def testSettingInvalidNameType(self) -> None:
        with self.assertRaises(TypeError):
            self.testProduct.name = 25
    
    def testSettingEmptyName(self) -> None:
        with self.assertRaises(ValueError):
            self.testProduct.name = ""

    # Price Tests
    def testSettingValidPrice(self) -> None:
        self.testProduct.price = 1000.0
        self.assertEqual(self.testProduct.price, 1000.0)
    
    def testSettingInvalidPriceType(self) -> None:
        with self.assertRaises(TypeError):
            self.testProduct.price = "1000"
    
    def testSettingInvalidPriceValue(self) -> None:
        with self.assertRaises(ValueError):
            self.testProduct.price = -1000.0

    # Url Tests
    def testSettingValidUrl(self) -> None:
        self.testProduct.url = "https://www.amazon.co.uk/"
        self.assertEqual(self.testProduct.url, "https://www.amazon.co.uk/")
    
    def testSettingInvalidUrlType(self) -> None:
        with self.assertRaises(TypeError):
            self.testProduct.url = 25
    
    def testSettingEmptyUrl(self) -> None:
        with self.assertRaises(ValueError):
            self.testProduct.url = ""
    
    def testSettingInvalidUrl(self) -> None:
        with self.assertRaises(ValueError):
            self.testProduct.url = "amazon"
    
    # Rating Tests
    def testSettingValidRating(self) -> None:
        self.testProduct.rating = 5.0
        self.assertEqual(self.testProduct.rating, 5.0)
    
    def testSettingInvalidRatingType(self) -> None:
        with self.assertRaises(TypeError):
            self.testProduct.rating = "5"
    
    def testSettingInvalidRatingValue(self) -> None:
        with self.assertRaises(ValueError):
            self.testProduct.rating = 6.0
    
    # Description Tests
    def testSettingValidDescription(self) -> None:
        self.testProduct.description = "Description2"
        self.assertEqual(self.testProduct.description, "Description2")
    
    def testSettingInvalidDescriptionType(self) -> None:
        with self.assertRaises(TypeError):
            self.testProduct.description = 25
    
    # Reviews Tests
    def testSettingValidReviews(self) -> None:
        self.testProduct.reviews = ["review1", "review2"]
        self.assertEqual(self.testProduct.reviews, ["review1", "review2"])
    
    def testSettingInvalidReviewsType(self) -> None:
        with self.assertRaises(TypeError):
            self.testProduct.reviews = "review1"
    
    # Adding Review Tests
    def testAddingValidReview(self) -> None:
        self.testProduct.addReview("review1")
        self.assertEqual(self.testProduct.reviews, ["review1"])
    
    def testAddingInvalidReviewType(self) -> None:
        with self.assertRaises(TypeError):
            self.testProduct.addReview(25)
    
    def testAddingEmptyReview(self) -> None:
        with self.assertRaises(ValueError):
            self.testProduct.addReview("")
    
    # Removing Review Tests
    def testRemovingValidReview(self) -> None:
        self.testProduct.addReview("review1")
        self.testProduct.removeReview("review1")
        self.assertEqual(self.testProduct.reviews, [])
    
    def testRemovingInvalidReviewType(self) -> None:
        with self.assertRaises(TypeError):
            self.testProduct.removeReview(25)
    
    def testRemovingEmptyReview(self) -> None:
        with self.assertRaises(ValueError):
            self.testProduct.removeReview("")

if __name__ == '__main__':
    unittest.main()
