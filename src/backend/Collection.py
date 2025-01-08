from src.backend.Product import Product
from typing import List

"""
This class is used to hold a list of products,
giving a name to the list of products.
A collection is the main class structure that is used
to hold the data that is then converted to data structures (Ditionaries to JSON and CSV)
"""
class Collection:
    def __init__(self, name : str, products : List[Product]) -> None:
        self._name = name
        self._products = products
    
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
    def products(self) -> List[Product]:
        return self._products
    
    @products.setter
    def products(self, products : List[Product]) -> None:
        if not isinstance(products, list):
            raise TypeError("Products must be a list")
        else:
            self._products = products
    
    def add_product(self, product : Product) -> None:
        if not isinstance(product, Product):
            raise TypeError("Product must be a Product")
        else:
            self._products.append(product)
    
    def remove_product(self, product : Product) -> None:
        if not isinstance(product, Product):
            raise TypeError("Product must be a Product")
        elif product not in self._products:
            raise ValueError("Product not in collection")
        else:
            self._products.remove(product)
    
    def __str__(self) -> str:
        return f"Collection: {self.name}\nProducts: {self.products}"
    
    def __eq__(self, other : object) -> bool:
        if not isinstance(other, Collection):
            return False
        return self.name == other.name and self.products == other.products