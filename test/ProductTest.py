import unittest
import sample

class ProductTest(unittest.TestCase):
    # Name Tests
    def testSettingValidName(self):
        product = sample.Product()
        product.name = "iPhone"
        self.assertEqual(product.name, "iPhone")
    
    def testSettingInvalidNameType(self):
        product = sample.Product()
        self.assertRaises(TypeError, product.set_name, 25)
    
    def testSettingEmptyName(self):
        product = sample.Product()
        self.assertRaises(ValueError, product.set_name, "")

    # Price Tests
    def testSettingValidPrice(self):
        product = sample.Product()
        product.price = 1000
        self.assertEqual(product.price, 1000)
    
    def testSettingInvalidPriceType(self):
        product = sample.Product()
        self.assertRaises(TypeError, product.set_price, "1000")
    
    def testSettingInvalidPriceValue(self):
        product = sample.Product()
        self.assertRaises(ValueError, product.set_price, -1000)

    # Url Tests
    def testSettingValidUrl(self):
        product = sample.Product()
        product.url = "https://www.amazon.co.uk/"
        self.assertEqual(product.url, "https://www.amazon.co.uk/")
    
    def testSettingInvalidUrlType(self):
        product = sample.Product()
        self.assertRaises(TypeError, product.set_url, 25)
    
    def testSettingEmptyUrl(self):
        product = sample.Product()
        self.assertRaises(ValueError, product.set_url, "")
    
    def testSettingInvalidUrl(self):
        product = sample.Product()
        self.assertRaises(ValueError, product.set_url, "amazon.co.uk")
    
    # Rating Tests
    def testSettingValidRating(self):
        product = sample.Product()
        product.rating = 5
        self.assertEqual(product.rating, 5)
    
    def testSettingInvalidRatingType(self):
        product = sample.Product()
        self.assertRaises(TypeError, product.set_rating, "5")
    
    def testSettingInvalidRatingValue(self):
        product = sample.Product()
        self.assertRaises(ValueError, product.set_rating, 6)
    
    # Reviews Tests
    def testSettingValidReviews(self):
        product = sample.Product()
        product.reviews = ["review1", "review2"]
        self.assertEqual(product.reviews, ["review1", "review2"])
    
    def testSettingInvalidReviewsType(self):
        product = sample.Product()
        self.assertRaises(TypeError, product.set_reviews, "review1")
    
    # Adding Review Tests
    def testAddingValidReview(self):
        product = sample.Product()
        product.add_review("review1")
        self.assertEqual(product.reviews, ["review1"])
    
    def testAddingInvalidReviewType(self):
        product = sample.Product()
        self.assertRaises(TypeError, product.add_review, 25)
    
    def testAddingEmptyReview(self):
        product = sample.Product()
        self.assertRaises(ValueError, product.add_review, "")
    
    # Removing Review Tests
    def testRemovingValidReview(self):
        product = sample.Product()
        product.add_review("review1")
        product.remove_review("review1")
        self.assertEqual(product.reviews, [])
    
    def testRemovingInvalidReviewType(self):
        product = sample.Product()
        self.assertRaises(TypeError, product.remove_review, 25)
    
    def testRemovingEmptyReview(self):
        product = sample.Product()
        self.assertRaises(ValueError, product.remove_review, "")

if __name__ == '__main__':
    unittest.main()