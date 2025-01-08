# Online_Products_Collection_Manager

## Description

This is an online products collection manager that allows a user to enter the name of any product they want to search for.  
This application will then scrape all of the given product within the Argos website, aggregating the data into data structures such as: Product and Collection.  
The collected data can then be viewed in a variety of visual ways.  
It can also be exported as JSON, or downloaded as CSV.

**On average the scraper takes 0.57 seconds per product scraped**

## Home page

The home page is where you are able to search for products you want to scrape.  
On this page you are also able to view collected collections, export, download and delete them.

## Collections page

The collections page is where you can choose a collection you want to view, view all of the products it contains, click on a product to view the individual products details, and view whole collections data in different ways with the graph view.

## User Stories

* As a customer I want to be able to Filter my data so that I can keep track on individual products and data
* As a customer I want to be able to compare different tables so that I can know what product is best for me
* As a customer I want to be able to load data from a csv file so that I can store large amounts of data
* As a customer I want to be able to load data from a json file so that I can export and import individual collections
* As a customer I want to be able to represent my data in different ways so that I can see any patterns and correlations

## How to run

### Install dependencies

(Make sure you have `cd`'d within the Online_Products_Collection_Manager folder)

To install the dependencies of the collection manager you can either run:  
`pip install -r requirements.txt`

Or you can use the `install_dependencies.py` file by running:  
`python -m src.install_dependencies`

### Run the application
To start the application run the following command:  
`python -m src.app`

If ran succesfully the console with display the following text:  
`Dash is running on http://127.0.0.1:8050/`  
On a web-browser navigate to the following page outputted (your localhost `http://127.0.0.1:8050/`).  
That page will contain the running application.
