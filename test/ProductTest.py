import unittest
from src.Product import Product

class ProductTest(unittest.TestCase):
    # Name Tests
    def testSettingValidName(self):
        product = Product()
        product.name = "iPhone"
        self.assertEqual(product.name, "iPhone")
    
    def testSettingInvalidNameType(self):
        product = Product()
        self.assertRaises(TypeError, product.set_name, 25)
    
    def testSettingEmptyName(self):
        product = Product()
        self.assertRaises(ValueError, product.set_name, "")

    # Price Tests
    def testSettingValidPrice(self):
        product = Product()
        product.price = 1000
        self.assertEqual(product.price, 1000)
    
    def testSettingInvalidPriceType(self):
        product = Product()
        self.assertRaises(TypeError, product.set_price, "1000")
    
    def testSettingInvalidPriceValue(self):
        product = Product()
        self.assertRaises(ValueError, product.set_price, -1000)

    # Url Tests
    def testSettingValidUrl(self):
        product = Product()
        product.url = "https://www.amazon.co.uk/"
        self.assertEqual(product.url, "https://www.amazon.co.uk/")
    
    def testSettingInvalidUrlType(self):
        product = Product()
        self.assertRaises(TypeError, product.set_url, 25)
    
    def testSettingEmptyUrl(self):
        product = Product()
        self.assertRaises(ValueError, product.set_url, "")
    
    def testSettingInvalidUrl(self):
        product = Product()
        self.assertRaises(ValueError, product.set_url, "amazon.co.uk")
    
    # Rating Tests
    def testSettingValidRating(self):
        product = Product()
        product.rating = 5
        self.assertEqual(product.rating, 5)
    
    def testSettingInvalidRatingType(self):
        product = Product()
        self.assertRaises(TypeError, product.set_rating, "5")
    
    def testSettingInvalidRatingValue(self):
        product = Product()
        self.assertRaises(ValueError, product.set_rating, 6)
    
    # Reviews Tests
    def testSettingValidReviews(self):
        product = Product()
        product.reviews = ["review1", "review2"]
        self.assertEqual(product.reviews, ["review1", "review2"])
    
    def testSettingInvalidReviewsType(self):
        product = Product()
        self.assertRaises(TypeError, product.set_reviews, "review1")
    
    # Adding Review Tests
    def testAddingValidReview(self):
        product = Product()
        product.add_review("review1")
        self.assertEqual(product.reviews, ["review1"])
    
    def testAddingInvalidReviewType(self):
        product = Product()
        self.assertRaises(TypeError, product.add_review, 25)
    
    def testAddingEmptyReview(self):
        product = Product()
        self.assertRaises(ValueError, product.add_review, "")
    
    # Removing Review Tests
    def testRemovingValidReview(self):
        product = Product()
        product.add_review("review1")
        product.remove_review("review1")
        self.assertEqual(product.reviews, [])
    
    def testRemovingInvalidReviewType(self):
        product = Product()
        self.assertRaises(TypeError, product.remove_review, 25)
    
    def testRemovingEmptyReview(self):
        product = Product()
        self.assertRaises(ValueError, product.remove_review, "")

if __name__ == '__main__':
    unittest.main()