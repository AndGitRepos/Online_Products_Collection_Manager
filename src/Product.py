from typing import List

class Product:
    def __init__(self, name : str, price : float, url : str, rating : float, reviews : List[str]) -> None:
        self.name = name
        self.price = price
        self.url = url
        self.rating = rating
        self.reviews = reviews

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
    def url(self, url : str) -> None:
        if not isinstance(url, str):
            raise TypeError("URL must be a string")
        elif len(url) == 0:
            raise ValueError("URL cannot be empty")
        else:
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
        return f"Name: {self.name}\nPrice: {self.price}\nURL: {self.url}\nRating: {self.rating}\nReviews: {self.reviews}"   