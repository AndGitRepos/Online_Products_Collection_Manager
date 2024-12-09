from typing import List
import regex as re
from urllib.parse import urlparse

class Product:
    def __init__(self, name : str, price : float, url : str, rating : float, reviews : List[str]) -> None:
        self._name = name
        self._price = price
        self._url = url
        self._rating = rating
        self._reviews = reviews

    @property
    def name(self) -> str:
        return self._name
    @name.setter
    def name(self, name : str) -> None:
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        elif len(name) == 0:
            raise ValueError("Name cannot be empty")
        else:
            self._name = name
    
    @property
    def price(self) -> float:
        return self._price
    @price.setter
    def price(self, price : float) -> None:
        if not isinstance(price, float):
            raise TypeError("Price must be a float")
        elif price < 0:
            raise ValueError("Price cannot be negative")
        else:
            self._price = price
    
    @property
    def url(self) -> str:
        return self._url
    @url.setter
    def url(self, url: str) -> None:
        if not isinstance(url, str):
            raise TypeError("URL must be a string")
        elif len(url) == 0:
            raise ValueError("URL cannot be empty")
        
        # URL pattern for validation
        url_pattern = re.compile(
            r'^(https?:\/\/)'  # http:// or https://
            r'([\da-z\.-]+)'   # domain name
            r'\.([a-z\.]{2,6})'  # dot + top level domain
            r'([\/\w \.-]*)*\/?$'  # path
        )
        
        # Add http:// prefix if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Validate URL format
        if not url_pattern.match(url):
            raise ValueError("Invalid URL format")
        
        # Additional validation using urlparse
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL")
        except Exception:
            raise ValueError("Invalid URL")
        
        self._url = url
    
    @property
    def rating(self) -> float:
        return self._rating
    @rating.setter
    def rating(self, rating : float) -> None:
        if not isinstance(rating, float):
            raise TypeError("Rating must be a float")
        elif rating < 0 or rating > 5:
            raise ValueError("Rating must be between 0 and 5")
        else:
            self._rating = rating
    
    @property
    def reviews(self) -> List[str]:
        return self._reviews
    @reviews.setter
    def reviews(self, reviews : List[str]) -> None:
        if not isinstance(reviews, list):
            raise TypeError("Reviews must be a list")
        else:
            self._reviews = reviews
    
    def addReview(self, review : str) -> None:
        if not isinstance(review, str):
            raise TypeError("Review must be a string")
        elif len(review) == 0:
            raise ValueError("Review cannot be empty")
        else:
            self._reviews.append(review)
    
    def removeReview(self, review : str) -> None:
        if not isinstance(review, str):
            raise TypeError("Review must be a string")
        elif len(review) == 0:
            raise ValueError("Review cannot be empty")
        else:
            self._reviews.remove(review)

    def __str__(self) -> str:
        return f"Name: {self._name}\nPrice: {self._price}\nURL: {self._url}\nRating: {self._rating}\nReviews: {self._reviews}"   