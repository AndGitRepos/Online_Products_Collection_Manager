from Collection import Collection
from typing import List, Dict
from typing import Any

# Might be best as a static class
# Each List[Dict[str, Any]] is a collection
# To store a bunch of collections could use
# Dict[str, List[Dict[str, Any]]] where first key is name of collection?
# Have it store data within spreadsheet file where each table is the collections name (key)
class DataManager:
    def __init__(self):
        pass

    @staticmethod
    def loadFromCsv(filename: str) -> List[Collection]:
        pass

    @staticmethod
    def saveToCsv(filename: str, collections: List[Collection]):
        pass

    @staticmethod
    def loadFromJson(filename: str) -> Collection:
        pass
    
    @staticmethod
    def saveToJson(filename: str, collection: Collection):
        pass

    @staticmethod
    def convertDicitonaryToCollection(dictionary: List[Dict[str, Any]]) -> Collection:
        pass
    
    @staticmethod
    def convertCollectionToDictionary(collection: Collection) -> List[Dict[str, Any]]:
        pass