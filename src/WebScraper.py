from typing import List, Dict, Any


class WebScraper:
    PRODUCT_WEBSITES : List[str] = ["amazon.co.uk"]
    USER_AGENTS : List[str] = ["Mozilla/5.0"]
    MAX_RESULTS : int = 100

    def __init__(self):
        raise TypeError("This class cannot be instantiated")
    
    @staticmethod
    def searchForProducts(productName : str) -> List[Dict[str, Any]]:
        pass

    @staticmethod
    def parseProductPage(productUrl : str) -> Dict[str, Any]:
        pass

    @staticmethod
    def extractProductData(rawHtml : str) -> Dict[str, Any]:
        pass

    @staticmethod
    def validateProductData(productData : Dict[str, Any]) -> bool:
        pass