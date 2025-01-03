from typing import List
import re
from urllib.parse import urlparse

class Product:
    def __init__(self, productID : str, name : str, price : float, url : str, rating : float, description : str, reviews : List[str]) -> None:
        self._productID : str = productID
        self._name : str = name
        self._price : float = price
        self._url : str = url
        self._rating : float = rating
        self._description : str = description
        self._reviews : List[str] = reviews
        
    @property
    def productID(self) -> str:
        return self._productID
    @productID.setter
    def productID(self, productID : int) -> None:
        if not isinstance(productID, str):
            raise TypeError("Product ID must be a string")
        elif len(productID) == 0:
            raise ValueError("Product ID cannot be empty")
        else:
            self._productID = productID

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
    def description(self) -> str:
        return self._description
    @description.setter
    def description(self, description : str) -> None:
        if not isinstance(description, str):
            raise TypeError("Description must be a string")
        else:
            self._description = description
    
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
        return f"""Product ID: {self.productID}
    Name: {self.name}
    Price: {self.price}
    URL: {self.url}
    Rating: {self.rating}
    Description: {self.description}
    Reviews: {self.reviews}"""
    
    def __eq__(self, other : object) -> bool:
        if not isinstance(other, Product):
            return False
        return (self.productID == other.productID 
                and self.name == other.name 
                and self.price == other.price 
                and self.url == other.url 
                and self.rating == other.rating 
                and self.description == other.description 
                and self.reviews == other.reviews)