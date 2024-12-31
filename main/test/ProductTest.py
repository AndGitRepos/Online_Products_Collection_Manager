import unittest
from src.Product import Product

class ProductTest(unittest.TestCase):
    def setUp(self) -> None:
        # This will run before each test method
        self.testProduct : Product = Product("ProductID", "TestName", 100.0, "https://www.test.co.uk/", 4.5, "Description", [])
    
    # Product ID Tests
    def test_setting_valid_product_id(self) -> None:
        self.testProduct.productID = "ProductID2"
        self.assertEqual(self.testProduct.productID, "ProductID2")
    
    def test_setting_invalid_product_id_type(self) -> None:
        with self.assertRaises(TypeError):
            self.testProduct.productID = 2
    
    def test_setting_empty_product_id(self) -> None:
        with self.assertRaises(ValueError):
            self.testProduct.productID = ""

    # Name Tests
    def test_setting_valid_name(self) -> None:
        self.testProduct.name = "iPhone"
        self.assertEqual(self.testProduct.name, "iPhone")
    
    def test_setting_invalid_name_type(self) -> None:
        with self.assertRaises(TypeError):
            self.testProduct.name = 25
    
    def test_setting_empty_name(self) -> None:
        with self.assertRaises(ValueError):
            self.testProduct.name = ""

    # Price Tests
    def test_setting_valid_price(self) -> None:
        self.testProduct.price = 1000.0
        self.assertEqual(self.testProduct.price, 1000.0)
    
    def test_setting_invalid_price_type(self) -> None:
        with self.assertRaises(TypeError):
            self.testProduct.price = "1000"
    
    def test_setting_invalid_price_value(self) -> None:
        with self.assertRaises(ValueError):
            self.testProduct.price = -1000.0

    # Url Tests
    def test_setting_valid_url(self) -> None:
        self.testProduct.url = "https://www.amazon.co.uk/"
        self.assertEqual(self.testProduct.url, "https://www.amazon.co.uk/")
    
    def test_setting_invalid_url_type(self) -> None:
        with self.assertRaises(TypeError):
            self.testProduct.url = 25
    
    def test_setting_empty_url(self) -> None:
        with self.assertRaises(ValueError):
            self.testProduct.url = ""
    
    def test_setting_invalid_url(self) -> None:
        with self.assertRaises(ValueError):
            self.testProduct.url = "amazon"
    
    # Rating Tests
    def test_setting_valid_rating(self) -> None:
        self.testProduct.rating = 5.0
        self.assertEqual(self.testProduct.rating, 5.0)
    
    def test_setting_invalid_rating_type(self) -> None:
        with self.assertRaises(TypeError):
            self.testProduct.rating = "5"
    
    def test_setting_invalid_rating_value(self) -> None:
        with self.assertRaises(ValueError):
            self.testProduct.rating = 6.0
    
    # Description Tests
    def test_setting_valid_description(self) -> None:
        self.testProduct.description = "Description2"
        self.assertEqual(self.testProduct.description, "Description2")
    
    def test_setting_invalid_description_type(self) -> None:
        with self.assertRaises(TypeError):
            self.testProduct.description = 25
    
    # Reviews Tests
    def test_setting_valid_reviews(self) -> None:
        self.testProduct.reviews = ["review1", "review2"]
        self.assertEqual(self.testProduct.reviews, ["review1", "review2"])
    
    def test_setting_invalid_reviews_type(self) -> None:
        with self.assertRaises(TypeError):
            self.testProduct.reviews = "review1"
    
    # Adding Review Tests
    def test_adding_valid_reviews(self) -> None:
        self.testProduct.addReview("review1")
        self.assertEqual(self.testProduct.reviews, ["review1"])
    
    def test_adding_invalid_review_type(self) -> None:
        with self.assertRaises(TypeError):
            self.testProduct.addReview(25)
    
    def test_adding_empty_review(self) -> None:
        with self.assertRaises(ValueError):
            self.testProduct.addReview("")
    
    # Removing Review Tests
    def test_removing_valid_review(self) -> None:
        self.testProduct.addReview("review1")
        self.testProduct.removeReview("review1")
        self.assertEqual(self.testProduct.reviews, [])
    
    def test_removing_invalid_review_type(self) -> None:
        with self.assertRaises(TypeError):
            self.testProduct.removeReview(25)
    
    def test_removing_empty_review(self) -> None:
        with self.assertRaises(ValueError):
            self.testProduct.removeReview("")

if __name__ == '__main__':
    unittest.main()
