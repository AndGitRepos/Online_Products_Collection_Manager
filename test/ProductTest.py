import unittest
from src.Product import Product

class ProductTest(unittest.TestCase):
    def setUp(self):
        # This will run before each test method
        self.product = Product("TestName", 100.0, "https://www.test.co.uk/", 4.5, [])

    # Name Tests
    def testSettingValidName(self):
        self.product.name = "iPhone"
        self.assertEqual(self.product.name, "iPhone")
    
    def testSettingInvalidNameType(self):
        with self.assertRaises(TypeError):
            self.product.name = 25
    
    def testSettingEmptyName(self):
        with self.assertRaises(ValueError):
            self.product.name = ""

    # Price Tests
    def testSettingValidPrice(self):
        self.product.price = 1000.0
        self.assertEqual(self.product.price, 1000.0)
    
    def testSettingInvalidPriceType(self):
        with self.assertRaises(TypeError):
            self.product.price = "1000"
    
    def testSettingInvalidPriceValue(self):
        with self.assertRaises(ValueError):
            self.product.price = -1000.0

    # Url Tests
    def testSettingValidUrl(self):
        self.product.url = "https://www.amazon.co.uk/"
        self.assertEqual(self.product.url, "https://www.amazon.co.uk/")
    
    def testSettingInvalidUrlType(self):
        with self.assertRaises(TypeError):
            self.product.url = 25
    
    def testSettingEmptyUrl(self):
        with self.assertRaises(ValueError):
            self.product.url = ""
    
    def testSettingInvalidUrl(self):
        with self.assertRaises(ValueError):
            self.product.url = "amazon"
    
    # Rating Tests
    def testSettingValidRating(self):
        self.product.rating = 5.0
        self.assertEqual(self.product.rating, 5.0)
    
    def testSettingInvalidRatingType(self):
        with self.assertRaises(TypeError):
            self.product.rating = "5"
    
    def testSettingInvalidRatingValue(self):
        with self.assertRaises(ValueError):
            self.product.rating = 6.0
    
    # Reviews Tests
    def testSettingValidReviews(self):
        self.product.reviews = ["review1", "review2"]
        self.assertEqual(self.product.reviews, ["review1", "review2"])
    
    def testSettingInvalidReviewsType(self):
        with self.assertRaises(TypeError):
            self.product.reviews = "review1"
    
    # Adding Review Tests
    def testAddingValidReview(self):
        self.product.addReview("review1")
        self.assertEqual(self.product.reviews, ["review1"])
    
    def testAddingInvalidReviewType(self):
        with self.assertRaises(TypeError):
            self.product.addReview(25)
    
    def testAddingEmptyReview(self):
        with self.assertRaises(ValueError):
            self.product.addReview("")
    
    # Removing Review Tests
    def testRemovingValidReview(self):
        self.product.addReview("review1")
        self.product.removeReview("review1")
        self.assertEqual(self.product.reviews, [])
    
    def testRemovingInvalidReviewType(self):
        with self.assertRaises(TypeError):
            self.product.removeReview(25)
    
    def testRemovingEmptyReview(self):
        with self.assertRaises(ValueError):
            self.product.removeReview("")

if __name__ == '__main__':
    unittest.main()
