import aiohttp
import asyncio
from aiohttp_retry import RetryClient, ExponentialRetry
from bs4 import BeautifulSoup
import json
import random
import re
import urllib.parse
from typing import List, Dict, Any
from src.Product import Product
from src.Collection import Collection

class WebScraper:
    USER_AGENTS: List[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/89.0",
        "Mozilla/5.0 (Android 11; Mobile; LG-M255; rv:89.0) Gecko/89.0 Firefox/89.0"
    ]
    MIN_SLEEP_TIME: int = 1.0
    MAX_SLEEP_TIME: int = 3.0
    MAX_CONCURRENT_REQUESTS: int = 5
    BASE_URL: str = "https://www.argos.co.uk"
    ROBOTS_TXT_CONTENT: str = None

    def __init__(self):
        raise TypeError("This is a utility class and cannot be instantiated")

    """
    This method chooses a random user agent out of the given list, and constructs 
    the request header that is to be send as part of the GET requests
    """
    @staticmethod
    def get_headers() -> Dict[str, str]:
        user_agent = random.choice(WebScraper.USER_AGENTS)
        return {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-full-version": "131.0.6778.140",
            "Sec-Ch-Ua-Full-Version-List": '"Google Chrome";v="131.0.6778.140", "Chromium";v="131.0.6778.140", "Not_A Brand";v="24.0.0.0"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
        }

    
    @staticmethod
    async def fetch_robots_txt(client: RetryClient) -> None:
        headers = WebScraper.get_headers()
        robotsUrl = urllib.parse.urljoin(WebScraper.BASE_URL, "/robots.txt")
        try:
            async with client.get(robotsUrl, headers=headers) as response:
                if response.status == 200:
                    WebScraper.ROBOTS_TXT_CONTENT = await response.text()
                else:
                    print(f"Failed to fetch robots.txt. Status: {response.status}")
                    WebScraper.ROBOTS_TXT_CONTENT = ""
        except Exception as e:
            print(f"Error fetching robots.txt: {e}")
            WebScraper.ROBOTS_TXT_CONTENT = ""

    """
    This method will check the robots.txt file of the base website and
    verify that the path we want to scrape is allowed
    """
    @staticmethod
    async def check_robots_txt(client: RetryClient, path: str) -> bool:
        if WebScraper.ROBOTS_TXT_CONTENT is None:
            await WebScraper.fetch_robots_txt(client)

        lines = WebScraper.ROBOTS_TXT_CONTENT.splitlines()
        for line in lines:
            if line.lower().startswith("disallow:"):
                disallowedPath = line.split(":", 1)[1].strip()
                if path.startswith(disallowedPath):
                    print(f"Access to {path} is disallowed by robots.txt")
                    return False
        print(f"Access to {path} is allowed by robots.txt")
        return True
    
    """
    Given a page URL, this method will extract the large JSON structure that it stored within a script tag
    """
    @staticmethod
    async def extract_script_json_data(
        client: RetryClient, 
        pageUrl: str, 
        referer : str, 
        jsonName : str
    ) -> Dict[str, Any]:
        headers = WebScraper.get_headers()
        headers["Referer"] = referer
        await asyncio.sleep(random.uniform(WebScraper.MIN_SLEEP_TIME, WebScraper.MAX_SLEEP_TIME))
        async with client.get(pageUrl, headers=headers) as response:
            if response.status == 200:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                script_tag = soup.find('script', string=lambda text: text and jsonName in text)
                if script_tag:
                    start_index = script_tag.string.find(jsonName) + len(jsonName)
                    end_index = script_tag.string.rfind('}') + 1
                    json_text = script_tag.string[start_index:end_index].replace('undefined', 'null')
                    try:
                        return json.loads(json_text)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                        return None
                else:
                    print("Failed to find {jsonName} script tag")
                    return None
            else:
                print(f"Failed to retrieve data from {pageUrl}. Status: {response.status}")
                print(f"Headers user-agent: {headers['User-Agent']}")
                return None
            
    @staticmethod
    def create_retry_client(session):
        retry_options = ExponentialRetry(
            attempts=5,
            start_timeout=1,
            max_timeout=60,
            factor=2,
            statuses={403, 429, 500, 502, 503, 504}
        )
        return RetryClient(client_session=session, retry_options=retry_options)

    """
    Given the name of a product that we want to collect data on this method will 
    search for the product and extract the URLs for each product page, it will then 
    extract the data of each product, and collect each product into a single collection
    
    
    """
    @staticmethod
    async def search_for_products(productName: str) -> Collection:
        async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar()) as session:
            retryClient : RetryClient = WebScraper.create_retry_client(session)
            
            # Check if search is allowed by robots.txt
            searchPath : str = f"/search/{productName}"
            if not await WebScraper.check_robots_txt(retryClient, searchPath):
                print("Searching is not allowed according to robots.txt. Aborting.")
                return None

            # Search for productName and gather all pages results
            searchResultsData: Dict[str, Any] = await WebScraper.fetch_all_search_results(
                retryClient, searchPath, productName
            )
            if not searchResultsData:
                print("No search results found")
                return None
            
            # From the search results construct each products page URL 
            # and save the total number of reviews each product has
            numOfResults : int = searchResultsData["redux"]["product"]["numberOfResults"]
            productPageUrlsAndNumOfReviews: List[tuple] = WebScraper.extract_product_urls_and_num_of_reviews(
                searchResultsData["redux"]["product"]["products"], 
                productName, 
                numOfResults
            )

            # Extract product data from each page constructed, resulting in a list of Products collected
            extractedProductData: List[Product] = []
            semaphore = asyncio.Semaphore(WebScraper.MAX_CONCURRENT_REQUESTS)
            tasks = [
                WebScraper.parse_product_page(
                    retryClient, 
                    productUrlAndNumOfReviews[0], 
                    productUrlAndNumOfReviews[1], 
                    f"https://www.argos.co.uk/search/{productName}/", 
                    semaphore
                ) 
                for productUrlAndNumOfReviews in productPageUrlsAndNumOfReviews
            ]
            extractedProductData = await asyncio.gather(*tasks)
            extractedProductData: List[Product] = [product for product in extractedProductData if product]
            
            if not extractedProductData:
                print("No products found")
                return None
            # Combining the list of products into a single collection
            print(f"Successfully retrieved data for {len(extractedProductData)} products")
            return Collection(productName, extractedProductData)

    """
    This method will fetch all search results for a given product name 
    and combine the JSON data structures for each page then return the combined JSON structure
    """
    @staticmethod
    async def fetch_all_search_results(
        retryClient: RetryClient, 
        searchPath : str, 
        productName : str
    ) -> Dict[str, Any]:
        # Constructing search URL for first page so that we can retrieve its JSON data 
        # structure to gain information on the total number of search results pages
        searchURL : str = f"{WebScraper.BASE_URL}{searchPath}/opt/page:1/?clickOrigin=searchbar:search:term:{productName}"
        searchResultsData: Dict[str, Any] = await WebScraper.extract_script_json_data(
            retryClient, searchURL, WebScraper.BASE_URL, "window.App="
        )
        if not searchResultsData:
            return None
        # Constructing the search URLs for every other page and 
        # creating tasks to extract the JSON data structure from each of them
        numOfPages: int = searchResultsData["redux"]["product"]["meta"]["totalPages"]
        tasks = []
        for page in range(2, min(7, numOfPages + 1)):
            searchURL : str = f"{WebScraper.BASE_URL}{searchPath}/opt/page:{page}/"
            tasks.append(WebScraper.extract_script_json_data(retryClient, searchURL, WebScraper.BASE_URL, "window.App="))

        # Combining the JSON data structures into one
        results = await asyncio.gather(*tasks)
        for result in results:
            if result:
                searchResultsData["redux"]["product"]["products"].extend(result["redux"]["product"]["products"])
        return searchResultsData

    """
    From the JSON data structure retrieved by a search, it extracts the data needed to construct the product pages URLs
    and extracts the total number of reviews for each product
    """
    @staticmethod
    def extract_product_urls_and_num_of_reviews(
        searchResultsProductsData: List[Dict[str, Any]], 
        productName : str, 
        numberOfResults : int
    ) -> List[str]:
        extractedProductUrlsAndNumOfReviews : List[tuple] = []
        for i, product in enumerate(searchResultsProductsData):
            productID: str = product["id"]
            productUrl: str = (f"{WebScraper.BASE_URL}/product/{productID}"
                               f"?clickSR=slp:term:{productName}:{i + 1}:{numberOfResults}:1")
            numOfReviews: int = product["attributes"]["reviewsCount"]
            extractedProductUrlsAndNumOfReviews.append((productUrl, numOfReviews))
        return extractedProductUrlsAndNumOfReviews

    """
    Parses a given product page, extracting data to instantiate a Product object
    """
    @staticmethod
    async def parse_product_page(
        client: RetryClient, 
        productUrl: str, 
        numOfReviews : int, 
        referer : str, 
        semaphore: asyncio.Semaphore
    ) -> Product:
        async with semaphore:
            # Check if product page access is allowed by robots.txt
            productPath = urllib.parse.urlparse(productUrl).path
            if not await WebScraper.check_robots_txt(client, productPath):
                print(f"Access to {productUrl} is not allowed according to robots.txt. Skipping.")
                return None
            # Extract the JSON data structure containing the product data
            await asyncio.sleep(random.uniform(WebScraper.MIN_SLEEP_TIME, WebScraper.MAX_SLEEP_TIME))
            productData: Dict[str, Any] = await WebScraper.extract_script_json_data(
                client, productUrl, referer, "window.__data="
            )
            if not productData:
                return None
            # Extract the product data needed within the JSON structure
            productID: str = productData["productStore"]["data"]["attributes"]["partNumber"]
            productName: str = productData["productStore"]["data"]["attributes"]["name"]
            price: str = productData["productStore"]["data"]["prices"]["attributes"]["now"]
            rating: str = productData["productStore"]["data"]["ratingSummary"]["attributes"]["avgRating"]
            dirtyDescription: str = productData["productStore"]["data"]["attributes"]["description"]
            # Removing HTML tags from the description
            descriptionSoup : BeautifulSoup = BeautifulSoup(dirtyDescription, 'html.parser')
            clean_description : str = descriptionSoup.get_text(separator=' ', strip=True)
            # Retrieve all the reviews for the product
            allReviews: List[str] = await WebScraper.get_reviews(client, productUrl, numOfReviews)

            print(f"Successfully retrieved data for product {productID}")
            return Product(productID, productName, price, productUrl, rating, clean_description, allReviews)

    """
    Extracts the product number from the URL
    """
    @staticmethod
    def get_product_number(url: str) -> str:
        match = re.search(r'/product/(\d+)', url)
        return match.group(1) if match else None

    """
    Retrieves the reviews for a product by sending a GET requests 
    with parameters for how many reviews to get and the offset from the first review
    You can only retrieve a maximum of 100 reviews at a time.
    """
    @staticmethod
    async def get_reviews(client: RetryClient, productUrl: str, numOfReviews : int = 10) -> List[str]:
        if numOfReviews < 1:
            return []
        productNumber : str = WebScraper.get_product_number(productUrl)
        if not productNumber:
            print("Could not extract product number from URL")
            return None

        apiUrl : str = f"{WebScraper.BASE_URL}/product-api/bazaar-voice-reviews/partNumber/{productNumber}"
        
        # Check if reviews API access is allowed by robots.txt
        apiPath = urllib.parse.urlparse(apiUrl).path
        if not await WebScraper.check_robots_txt(client, apiPath):
            print(f"Access to reviews API is not allowed according to robots.txt. Skipping.")
            return None

        # Setting params and headers to mimic how the browser sent the GET request
        headers : Dict[str, str] = WebScraper.get_headers()
        headers.update({
            "Accept": "application/json",
            "Referer": productUrl,
            "Sec-Ch-Ua-Platform": '"macOS"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "x-newrelic-id": "VQEPU15SARAGV1hVDgMBUVY="
        })
        
        allReviews : List[str] = []
        for i in range(0, numOfReviews // 100 + 1):
            offset : int = i * 100
            params = {
                "Limit": min(100, numOfReviews - offset),
                "Offset": offset,
                "Sort": "SubmissionTime:Desc",
                "returnMeta": "true"
            }

            await asyncio.sleep(random.uniform(WebScraper.MIN_SLEEP_TIME, WebScraper.MAX_SLEEP_TIME))
            async with client.get(apiUrl, params=params, headers=headers) as response:
                if response.status == 200:
                    try:
                        reviewsResponse = await response.json()
                        for review in reviewsResponse["data"]["Results"]:
                            allReviews.append(review["ReviewText"])
                    except aiohttp.ContentTypeError:
                        print(f"Unexpected content type: {response.headers.get('Content-Type')}")
                        text = await response.text()
                        print(f"Response text: {text[:200]}...")
                else:
                    print(f"Failed to retrieve reviews. Status: {response.status}")
                    print(f"Params: {params}")
        
        return allReviews
