import sys
import os

# Get the path to the project root directory
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

import time
import asyncio
from src.WebScraper import WebScraper
from src.DataManager import DataManager

async def main():
    start_time = time.time()
    collection = await WebScraper.searchForProducts("case")
    if collection is None:
        print("No collection found")
        return
    DataManager.saveCollectionsToCsvFolder("CsvFolder", [collection])
    DataManager.saveCollectionToJson("JsonFolder", collection)
    end_time = time.time()
    print(f"Time taken: {end_time - start_time}")

if __name__ == "__main__":
    asyncio.run(main())