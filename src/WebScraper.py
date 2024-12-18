from typing import List, Dict, Any
from src.Product import Product
from src.Collection import Collection
from src.DataManager import DataManager
import json
from bs4 import BeautifulSoup
import requests
import re
import time


class WebScraper:
    PRODUCT_WEBSITES : List[str] = ["https://www.argos.co.uk/search/"]
    USER_AGENTS : List[str] = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"]
    MAX_RESULTS : int = 100

    def __init__(self):
        raise TypeError("This is a utility class and cannot be instantiated")
    
    
    @staticmethod
    def searchForProducts(productName : str) -> Collection:
        searchURL = f"https://www.argos.co.uk/search/{productName}/opt/page:1/"
        searchResultsData = WebScraper.extractSearchResultsJSON(searchURL)
        if not searchResultsData:
            return None
        numOfPages : int = searchResultsData["redux"]["product"]["meta"]["totalPages"]
        # TODO - currently capped at maximum 10 pages
        for page in range(1, min(5, numOfPages + 1)):
            time.sleep(0.2)
            searchURL = f"https://www.argos.co.uk/search/{productName}/opt/page:{page}/"
            currPageSearchResultsData = WebScraper.extractSearchResultsJSON(searchURL)
            if not currPageSearchResultsData:
                print(f"Failed to retrieve search results for page {page}")
                continue
            print(f"Successfully retrieved search results for page {page}")
            searchResultsData["redux"]["product"]["products"].extend(currPageSearchResultsData["redux"]["product"]["products"])
        
        productPageUrls : List[str] = WebScraper.extractProductUrls(searchResultsData["redux"]["product"]["products"])
        
        extractedProductData : List[Product] = []
        for productUrl in productPageUrls:
            time.sleep(0.15)
            productData : Product = WebScraper.parseProductPage(productUrl)
            if not productData:
                print(f"Failed to retrieve product data for {productUrl}")
                continue
            print(f"Successfully retrieved product data for {productUrl}")
            extractedProductData.append(productData)
        print(f"Successfully retrieved data for {len(extractedProductData)} products")
        collection : Collection = Collection(productName, extractedProductData)
        return collection
        
    
    @staticmethod
    def extractSearchResultsJSON(productUrl : str) -> Dict[str, Any]:
        response = requests.get(productUrl, headers={"User-Agent": WebScraper.USER_AGENTS[0]})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the script tag containing window.__data
        script_tag = soup.find('script', string=lambda text: text and 'window.App=' in text)
        
        if script_tag:
            # Find the start and end of the JSON data
            start_index = script_tag.string.find('window.App=') + len('window.App=')
            end_index = script_tag.string.rfind('}') + 1
            
            # Extract the JSON data
            # Replacing undefined with null or will get an error when parse JSON structure
            # with json.loads()
            json_text = script_tag.string[start_index:end_index].replace('undefined', 'null')
            
            # Parse the JSON data
            try:
                data = json.loads(json_text)
                return data
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return None
        else:
            print("Could not find window.App in the page source")
            return None
    
    """
    Extracts every product pages URL from search results page
    
    @param rawHtml: The raw HTML of the search results page
    @return: A list of product page URLs
    """
    @staticmethod
    def extractProductUrls(searchResultsProductsData : List[Dict[str, Any]]) -> List[str]:
        extractedProductUrls : List[str] = []
        for product in searchResultsProductsData:
            productId : str = product["id"]
            productUrl = f"https://www.argos.co.uk/product/{productId}"
            extractedProductUrls.append(productUrl)
        return extractedProductUrls

    """
    Extracts product data from a products page
    Constructs the data into a Product object
    
    @param productUrl: The URL of the product
    @return: A Product object containing the product data
    """
    @staticmethod
    def parseProductPage(productUrl : str) -> Product:
        productData : Dict[str, Any] = WebScraper.extractProductData(productUrl)
        if not productData:
            return None
        
        productID : str = productData["productStore"]["data"]["attributes"]["partNumber"]
        productName : str = productData["productStore"]["data"]["attributes"]["name"]
        price : str = productData["productStore"]["data"]["prices"]["attributes"]["now"]
        rating : str = productData["productStore"]["data"]["ratingSummary"]["attributes"]["avgRating"]
        dirtyDescription : str = productData["productStore"]["data"]["attributes"]["description"]
        # Creating beautiful soup object to strip HTML tags
        descriptionSoup = BeautifulSoup(dirtyDescription, 'html.parser')
        # Extract all text, stripping HTML tags
        clean_description = descriptionSoup.get_text(separator=' ', strip=True)
        
        # Instead of extracting first 10 reviews then also extractin additional 
        # and concatinating, just using GET request to retrieve all reviews
        reviews_list: List[str] = []
        # Get all reviews
        allReviews: Dict[str, Any] = WebScraper.getAdditionalReviews(productUrl, 0, 100)
        if allReviews:
            reviews: List[Dict[str, Any]] = allReviews["data"]["Results"]
            for review in reviews:
                reviews_list.append(review["ReviewText"])
        
        return Product(productID, productName, price, productUrl, rating, clean_description, reviews_list)
    
    """
    Retrieves the product number from the product URL
    """
    @staticmethod
    def getProductNumber(url : str) -> str:
        match = re.search(r'/product/(\d+)', url)
        return match.group(1) if match else None

    """
    Retrieves additional reviews for a product
    This is achieved by making a GET request to the Argos product API for 'bazaar-voice-reviews'
    
    @param productUrl: The URL of the product
    @param offset: The number of reviews to skip (default: 10)
    @param limit: The number of reviews to retrieve (default: 10)
    @return: A JSON object containing the additional reviews
    """
    @staticmethod
    def getAdditionalReviews(productUrl : str, offset : int = 10, limit : int = 10) -> Any:
        product_number = WebScraper.getProductNumber(productUrl)
        if not product_number:
            print("Could not extract product number from URL")
            return None

        api_url = f"https://www.argos.co.uk/product-api/bazaar-voice-reviews/partNumber/{product_number}"
        params = {
            "Limit": limit,
            "Offset": offset,
            "Sort": "SubmissionTime:Desc",
            "returnMeta": "true"
        }

        headers = {
            "accept": "application/json",
            "referer": productUrl,
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"'
        }

        response = requests.get(api_url, params=params, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None

    """
    Extracting the product data from the product page
    This is performed by finding the script tag containing window.__data 
    which contains a large JSON object with all the product data
    
    @param productUrl: The URL of the product
    @return: A JSON object containing the product data
    """
    @staticmethod
    def extractProductData(productUrl : str) -> Dict[str, Any]:
        response = requests.get(productUrl, headers={"User-Agent": WebScraper.USER_AGENTS[0]})
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the script tag containing window.__data
        script_tag = soup.find('script', string=lambda text: text and 'window.__data=' in text)
        
        if script_tag:
            # Find the start and end of the JSON data
            start_index = script_tag.string.find('window.__data=') + len('window.__data=')
            end_index = script_tag.string.rfind('}') + 1
            
            # Extract the JSON data
            # Replacing undefined with null or will get an error when parse JSON structure
            # with json.loads()
            json_text = script_tag.string[start_index:end_index].replace('undefined', 'null')
            
            # Parse the JSON data
            try:
                data = json.loads(json_text)
                return data
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return None
        else:
            print("Could not find window.__data in the page source")
            return None

    @staticmethod
    def validateProductData(productData : Dict[str, Any]) -> bool:
        pass

if __name__ == "__main__":
    collection = WebScraper.searchForProducts("phone")
    DataManager.saveCollectionsToCsvFolder("CsvFolder", [collection])
    DataManager.saveCollectionToJson("JsonFolder", collection)
    #WebScraper.parseProductPage("https://www.argos.co.uk/product/3186567?clickSR=slp:term:computer:38:930:1")