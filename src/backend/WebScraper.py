import aiohttp
import asyncio
from aiohttp_retry import RetryClient, ExponentialRetry
from bs4 import BeautifulSoup
import json
import random
import math
import time
import urllib.parse
from typing import List, Dict, Any
from src.backend.Product import Product
from src.backend.Collection import Collection

"""
A class to dynamically adjust the rate of requests based on server responses.
It helps in avoiding rate limiting by increasing or decreasing the request rate as needed.
"""
class AdaptiveRateLimiter:
    def __init__(self, initial_rate=1, max_rate=10, min_delay=1.0, max_delay=2.0):
        self.rate = initial_rate
        self.max_rate = max_rate
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
    """
    Ensures that requests are not made too quickly by waiting if necessary.
    """
    async def wait(self):
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        delay = max(1 / self.rate - time_since_last_request, 0)
        delay += random.uniform(self.min_delay, self.max_delay)
        if delay > 0:
            await asyncio.sleep(delay)
        self.last_request_time = time.time()
    """
    Increases the request rate after successful requests.
    """
    def increase_rate(self):
        self.rate = min(self.rate * 1.1, self.max_rate)
    """
    Decreases the request rate if rate limiting is detected.
    """
    def decrease_rate(self):
        self.rate = max(self.rate * 0.9, 1)
"""
A utility class for scraping product information from the Argos website.
It includes methods for searching products, parsing product pages, and fetching reviews.
"""
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
    MIN_SLEEP_TIME: float = 0.3
    MAX_SLEEP_TIME: float = 0.6
    MAX_CONCURRENT_REQUESTS: int = 6
    MAX_NUMBER_OF_REVIEWS: int = 400
    MAX_NUMBER_OF_PRODUCTS: int = 150 # Limiting size so that searches dont take too long for when you are reviewing/testing
    BASE_URL: str = "https://www.argos.co.uk"
    ROBOTS_TXT_CONTENT: str = None
    rate_limiter: AdaptiveRateLimiter = AdaptiveRateLimiter(
        initial_rate=1, 
        max_rate=10, 
        min_delay=MIN_SLEEP_TIME, 
        max_delay=MAX_SLEEP_TIME
    )

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
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",#image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
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

    """
    Retrieves the robots.txt file from the target website.
    """
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
    Verifies if the given paths are allowed to be scraped according to robots.txt.
    """
    @staticmethod
    async def check_paths_allowed(client: RetryClient, paths: List[str]) -> bool:
        if WebScraper.ROBOTS_TXT_CONTENT is None:
            await WebScraper.fetch_robots_txt(client)

        lines = WebScraper.ROBOTS_TXT_CONTENT.splitlines()
        for path in paths:
            for line in lines:
                if line.lower().startswith("disallow:"):
                    disallowedPath = line.split(":", 1)[1].strip()
                    if path.startswith(disallowedPath):
                        print(f"Access to {path} is disallowed by robots.txt")
                        return False
        return True
    """
    Creates a RetryClient with specific retry options for handling failed requests.
    """  
    @staticmethod
    def create_retry_client(session):
        retry_options = ExponentialRetry(
            attempts=3,
            start_timeout=0.8,
            max_timeout=60,
            factor=2,
            statuses={403, 429, 500, 502, 503, 504}
        )
        return RetryClient(client_session=session, retry_options=retry_options)
    """
    Implements an exponential backoff strategy for rate limiting.
    """
    @staticmethod
    async def handle_rate_limit(attempt):
        wait_time = min((2 ** attempt) + random.uniform(0, 1), 60)  # Cap at 60 seconds
        print(f"Rate limited. Waiting for {wait_time:.2f} seconds before retry.")
        await asyncio.sleep(wait_time)
        
    @staticmethod
    def create_ssl_context():
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.load_default_certs()
        return ssl_context

    """
    Main method to search for products and collect their data.
    It orchestrates the entire scraping process for a given product search term.
    """
    @staticmethod
    async def search_for_products(productName: str) -> Collection:
        ssl_context = WebScraper.create_ssl_context()
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(
            cookie_jar=aiohttp.CookieJar(),
            connector=connector
        ) as session:
            retryClient : RetryClient = WebScraper.create_retry_client(session)
            
            # Check if all required paths are allowed by robots.txt
            paths_to_check = [
                "/finder-api/product",
                "/product/",
                "/product-api/bazaar-voice-reviews/partNumber/"
            ]
            if not await WebScraper.check_paths_allowed(retryClient, paths_to_check):
                print("One or more required paths are not allowed by robots.txt. Aborting.")
                return None

            # Search for productName and gather all pages results
            searchResultsData: Dict[str, Any] = await WebScraper.fetch_all_search_results(
                retryClient, productName
            )
            if not searchResultsData:
                print("No search results found")
                return None
            
            # From the search results construct each products page URL 
            # and save the total number of reviews each product has
            productData: List[Dict[str, Any]] = WebScraper.extract_product_data_from_search(
                searchResultsData["data"]["response"]["data"]
            )

            # Extract product data from each page constructed, resulting in a list of Products collected
            extractedProductData: List[Product] = []
            semaphore = asyncio.Semaphore(WebScraper.MAX_CONCURRENT_REQUESTS)
            tasks = [
                WebScraper.parse_product_page(
                    retryClient, 
                    product["url"], 
                    product["numOfReviews"], 
                    f"https://www.argos.co.uk/search/{productName}/", 
                    semaphore,
                    product
                ) 
                for product in productData
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
    Retrieves all search result pages for a given product name.
    """
    @staticmethod
    async def fetch_all_search_results(
        retryClient: RetryClient, 
        productName : str
    ) -> Dict[str, Any]:
        base_url = f"{WebScraper.BASE_URL}/finder-api/product"
        all_results = []
        current_page = 1
        total_pages = 1

        async def fetch_page(page):
            url = f"{base_url};isSearch=true;searchTerm={productName};queryParams={{\"page\":\"{page}\"}};payloadPath=/search/{productName}?returnMeta=true"
            headers = WebScraper.get_headers()
            
            await WebScraper.rate_limiter.wait()
            
            async with retryClient.get(url, headers=headers) as response:
                if response.status == 200:
                    WebScraper.rate_limiter.increase_rate()
                    data = await response.json()
                    return data["data"]["response"]["data"], data["data"]["response"]["meta"]["totalPages"]
                elif response.status == 429:
                    WebScraper.rate_limiter.decrease_rate()
                    await WebScraper.exponential_backoff(page)
                    return None, None
                else:
                    print(f"Failed to retrieve search results for page {page}. Status: {response.status}")
                    return None, None

        while current_page <= min(total_pages, math.ceil(WebScraper.MAX_NUMBER_OF_PRODUCTS / 60)):
            results, pages = await fetch_page(current_page)
            if results:
                all_results.extend(results)
                total_pages = pages
                current_page += 1
            else:
                break

        return {"data": {"response": {"meta": {"totalData": WebScraper.MAX_NUMBER_OF_PRODUCTS}, "data": all_results[:WebScraper.MAX_NUMBER_OF_PRODUCTS]}}}

    """
    Extracts relevant product data from the search results.
    """
    @staticmethod
    def extract_product_data_from_search(
        searchResultsProductsData: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        return [{
            "id": product["id"],
            "url": f"{WebScraper.BASE_URL}/product/{product['id']}",
            "numOfReviews": product["attributes"]["reviewsCount"],
            "name": product["attributes"]["name"],
            "price": product["attributes"]["price"],
            "rating": product["attributes"]["avgRating"]
        } for product in searchResultsProductsData]

    """
    Extracts detailed information from a single product page.
    """
    @staticmethod
    async def parse_product_page(
        client: RetryClient, 
        productUrl: str, 
        numOfReviews : int, 
        referer : str, 
        semaphore: asyncio.Semaphore,
        productData: Dict[str, Any]
    ) -> Product:
        async with semaphore:
            await WebScraper.rate_limiter.wait()
            # Extract the description from the HTML content
            description = await WebScraper.fetch_description(client, productUrl, referer)
            
            # Retrieve all the reviews for the product
            allReviews: List[str] = await WebScraper.get_reviews(
                client, productData['id'], productUrl, min(WebScraper.MAX_NUMBER_OF_REVIEWS, numOfReviews)
            )

            print(f"Successfully retrieved data for product {productData['id']}")
            return Product(
                productData['id'], 
                productData['name'], 
                productData['price'], 
                productUrl, 
                productData['rating'], 
                description, 
                allReviews
            )
    
    """
    Retrieves and extracts the product description from the product page.
    """
    @staticmethod
    async def fetch_description(client: RetryClient, url: str, referer: str) -> str:
        headers = WebScraper.get_headers()
        headers["Referer"] = referer
        
        await WebScraper.rate_limiter.wait()
        
        async with client.get(url, headers=headers) as response:
            if response.status == 200:
                WebScraper.rate_limiter.increase_rate()
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html.parser')
                description_element = soup.select_one('div.product-description-content-text')
                return description_element.get_text(strip=True) if description_element else "Description not found"
            elif response.status == 429:
                WebScraper.rate_limiter.decrease_rate()
                await WebScraper.exponential_backoff(1)
                return "Description not found (Rate limited)"
            else:
                print(f"Failed to retrieve HTML content. Status: {response.status}")
                return "Description not found"

    """
    Retrieves the reviews for a product by sending a GET requests 
    with parameters for how many reviews to get and the offset from the first review
    You can only retrieve a maximum of 100 reviews at a time.
    """
    @staticmethod
    async def get_reviews(client: RetryClient, productId : str, productUrl: str, numOfReviews : int = 10) -> List[str]:
        if numOfReviews < 1:
            return []

        apiUrl : str = f"{WebScraper.BASE_URL}/product-api/bazaar-voice-reviews/partNumber/{productId}"
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
        offset : int = 0
        
        async def fetch_reviews(offset):
            params = {
                "Limit": min(100, numOfReviews - offset),
                "Offset": offset,
                "Sort": "SubmissionTime:Desc",
                "returnMeta": "true"
            }
            
            await WebScraper.rate_limiter.wait()
            
            async with client.get(apiUrl, params=params, headers=headers) as response:
                if response.status == 200:
                    WebScraper.rate_limiter.increase_rate()
                    try:
                        reviewsResponse = await response.json()
                        return [review["ReviewText"] for review in reviewsResponse["data"]["Results"]]
                    except aiohttp.ContentTypeError:
                        print(f"Unexpected content type: {response.headers.get('Content-Type')}")
                        return []
                elif response.status == 429:
                    WebScraper.rate_limiter.decrease_rate()
                    await WebScraper.exponential_backoff(1)
                    return []
                else:
                    print(f"Failed to retrieve reviews. Status: {response.status}")
                    return []

        tasks = []
        for i in range(0, numOfReviews, 100):
            tasks.append(fetch_reviews(i))

        results = await asyncio.gather(*tasks)
        for result in results:
            allReviews.extend(result)
            if len(allReviews) >= numOfReviews:
                break

        return allReviews[:numOfReviews]
