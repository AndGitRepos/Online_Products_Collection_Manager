# Online_Products_Collection_Manager

## Description

This is an online products collection manager that allows a user to enter the name of any product they want to search for.  
This application will then scrape all of the given product within the Argos website, aggregating the data into data structures such as: Product and Collection.  
The collected data can then be viewed in a variety of visual ways.  
It can also be exported as JSON, or downloaded as CSV.

## User Stories
* As a customer I want to be able to Filter my data
* As a customer I want to be able to compare different tables
* As a customer I want to be able to load data from a csv file
* As a customer I want to be able to load data from a json file
* As a customer I want to be able to represent my data in different ways

## How to run

### Install dependencies

(Make sure you have `cd`'d within the Online_Products_Collection_Manager folder)

To install the dependencies of the collection manager you can either run:  
`pip install -r requirements.txt`

Or you can you the `install_dependencies.py` file by running:  
`python -m src.install_dependencies`

### Run the application
To start the application run the following command:  
`python -m src.app`

If ran succesfull the console with display the following text:  
`Dash is running on http://127.0.0.1:8050/`  
On a web-browser navigate to the following page (your localhost `http://127.0.0.1:8050/`).  
That page will contain the application.
