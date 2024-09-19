# UK Land Registry CCOD and OCOD Database
Version: 1.2.0

# Table of Contents

1. [UK Land Registry CCOD and OCOD Database](#uk-land-registry-ccod-and-ocod-database)
   - [Overview](#overview)
   - [Installation](#installation)
2. [`build.py`](#buildpy)
   - [Overview](#overview-1)
   - [Features](#features)
   - [Usage](#usage)
   - [Output](#output)
   - [Error Handling](#error-handling)
3. [Class: `PropertyDatabase`](#class-propertydatabase)
   - [`perform_title_search(title_number: str) -> dict`](#perform_title_searchtitle_number-str-dict)
   - [`perform_company_search(company: str) -> dict`](#perform_company_searchcompany-str-dict)
   - [`perform_fuzzy_search(search_term: str) -> list`](#perform_fuzzy_searchsearch_term-str-list)
4. [`search.py`](#searchpy)
   - [Overview](#overview-2)
   - [Functions](#functions)
     - [`menu(database: PropertyDatabase)`](#menudatabase-propertydatabase)
     - [`title_search(database, project_name, title_number=None)`](#title_searchdatabase-project_name-title_numbernone)
     - [`company_search(database, project_name, company=None)`](#company_searchdatabase-project_name-companynone)
     - [`fuzzy_search(database, project_name, search_term=None)`](#fuzzy_searchdatabase-project_name-search_termnone)
     - [`print_title_search_result(clean_result)`](#print_title_search_resultclean_result)
     - [`clean_title_search_result(result: dict) -> dict`](#clean_title_search_resultresult-dict-dict)
     - [`print_company_search_result(cleaned_result)`](#print_company_search_resultcleaned_result)
     - [`clean_company_search_result(result: dict) -> dict`](#clean_company_search_resultresult-dict-dict)
   - [Usage](#usage-1)
5. [`save_results.py`](#save_resultspy)
   - [Overview](#overview-3)
   - [Functions](#functions-1)
     - [`save_title_result_to_pdf(clean_result, project_name)`](#save_title_result_to_pdfclean_result-project_name)
     - [`save_company_result_to_pdf(clean_result, project_name)`](#save_company_result_to_pdfclean_result-project_name)
     - [`save_fuzzy_result_to_txt(project_name, search_term, results)`](#save_fuzzy_result_to_txtproject_name-search_term-results)
   - [File Structure](#file-structure)
   - [Usage](#usage-2)
6. [License](#license)
7. [Acknowledgements](#acknowledgements)


## Overview
This project builds a database for searching the CCOD and OCOD datasets released by the [UK Land Registry](https://use-land-property-data.service.gov.uk/).

## Installation

Install by downloading from the repository into your selected folder. Then run ```pip install -r requirements.txt```

## `build.py`
### Overview
This script automates the process of downloading and transforming land property datasets (OCOD and CCOD) into parquet files suitable for further analysis. The script allows the user to input an API key (which can be obtained [here](https://use-land-property-data.service.gov.uk/datasets/ocod#access)) and select a dataset year and month, retrieves the dataset, processes it, and generates three tables: titles, owners, and titles_owners. These tables are saved as Parquet files for efficient storage and access.

### Features
- **API Key Authentication**: Prompts the user to enter a valid API key following a specific format (UUID).
- **Year and Month Validation**: Ensures the user provides valid year and month input for dataset selection.
- **Dataset Downloading**: Fetches datasets (OCOD and CCOD) from the API, unzips them, and saves CSV files.
- **Data Loading**: Loads specified columns from the downloaded CSV files into Pandas DataFrames.
- **Data Merging**: Combines the OCOD and CCOD datasets into a single dataset.
- **Table Creation**: Generates three main tables from the merged data:
  1. titles: Information about the property titles, including title number and price.
  2. owners: Details of the property owners, cleaned and organized.
  3. titles_owners: Relationship between titles and their owners.
- **Data Storage**: Saves the final tables as Parquet files in the data directory.
- **CSV Cleanup**: Deletes the intermediate CSV files after processing.

### Usage

- Run the script using `python build.py`. You will be prompted for:
  - An API key (which should follow the format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).
  - The year (YYYY) and month (MM) for the dataset you want to process.

- The script will:
   - Download and unzip the datasets.
   - Load the data and process it into three tables: titles, owners, and titles_owners.
   - Save the tables as Parquet files in the data directory.
   - Clean up intermediate CSV files.

### Output
The script produces three parquet files:
1. **`data/titles.parquet`**: Contains unique property titles with price and address.
2. **`data/owners.parquet`**: Contains owner information, including country of incorporation.
3. **`data/titles_owners.parquet`**: Contains the relationship between titles and owners.

### Error Handling
1. **Invalid API Key**: The script checks if the API key matches the expected UUID pattern. If not, it will ask you to re-enter a valid key.
2. **Invalid Month/Year Input**: If the month or year input is invalid, the script prompts for a correct value.
3. **File Not Found**: If the downloaded CSV files are missing or the provided path is incorrect, the script raises a FileNotFoundError.

## Class: `PropertyDatabase`
### Methods
#### `perform_title_search(title_number: str) -> dict`
Performs a search for a property using the given title number and returns relevant details.

#### Parameters:
- **title_number (string)**: The title number of the property.

  Returns a dictionary containing:
  - **TITLE_NUMBER**: The title number.
  - **ADDRESS**: The property address.
  - **PRICE**: Price last paid.
  - **OWNERS**: A list of owners, each with:
    - **OWNER**: Owner's name.
    - **COUNTRY**: Country of incorporation (if applicable).
    - **SOURCE**: Data source.

  If the title number is not found, the method returns 0.

#### `perform_company_search(company: str) -> dict`
Searches for all properties owned by a specific company.

#### Parameters:
- **company (string)**: The company name.

  Returns a dictionary containing:
    - **COMPANY**: The name of the company.
    - **COUNTRY**: The country of incorporation (if applicable).
    - **SOURCE**: Data source.
    - **PROPERTIES**: A list of properties owned by the company, each with:
    - **TITLE NUMBER**: The title number.
    - **ADDRESS**: The property address.
    - **PRICE LAST PAID**: The price of the property.

  If the company is not found, the method returns 0.

#### `perform_fuzzy_search(search_term: str) -> list`
Performs a fuzzy search on the owners dataset, returning partial matches to the provided search term.

#### Parameters:
- **search_term (string)**: The term to search for within the owners' names.

  Returns a list of matching owners.

## `search.py`
### Overview
This script provides a command-line interface for searching the property database. Users can search by title number, company name, or perform a fuzzy search for company names. Results can be saved to PDF or TXT files. The script consists of the following main functions:

- **`menu()`**: Displays the main menu and processes user input.
- **`title_search()`**: Searches the database by title number.
- **`company_search()`**: Searches the database by company name.
- **`fuzzy_search()`**: Performs a fuzzy search for company names.
- **`print_title_search_result()`**: Formats and prints the search results for a title number.
- **`print_company_search_result()`**: Formats and prints the search results for a company.
- **`clean_title_search_result()`**: Cleans and formats the results from a title search.
- **`clean_company_search_result()`**: Cleans and formats the results from a company search.

### Functions
#### `menu(database: PropertyDatabase)`

Prompts the user to enter a project name and then displays a menu for search options.

Options:
- **t**: Search by title number.
- **c**: Search by company name.
- **f**: Fuzzy search for company names.
- **x**: Exit the program.

#### `title_search(database, project_name, title_number=None)`
- Searches the database for a property by title number.
- If no title number is provided, prompts the user to enter one
- Saves the results to a PDF file.

#### `company_search(database, project_name, company=None)`
- Searches the database for a company by name.
- If no company name is provided, prompts the user to enter one.
- Saves the results to a PDF file.

#### `fuzzy_search(database, project_name, search_term=None)`
- Performs a fuzzy search for company names containing a given search term.
- If no search term is provided, prompts the user to enter one.
- Saves the results to a TXT file.

#### `print_title_search_result(clean_result)`
- Prints formatted results for a title search, including title number, address, price, and owner information.

#### `clean_title_search_result(result: dict) -> dict`

- Cleans and formats the results of a title search.
- Handles missing or NaN values, formats prices, and wraps text for addresses.

#### `print_company_search_result(cleaned_result)`

- Prints formatted results for a company search, including company incorporation details and property ownership information.

#### `clean_company_search_result(result: dict) -> dict`

- Cleans and formats the results of a company search.
- Handles missing or NaN values, formats prices, and wraps text for addresses.

### Usage
1. Run the script using `python search.py`
2. Enter the project name when prompted.
3. Choose a search option from the menu.
4. Follow the prompts to enter search criteria.
5. View the results in the console and check the output files (PDF or TXT) as specified.

## `save_results.py`

### Overview

This script provides functions for saving search results to various file formats, specifically PDF and TXT. It uses the `FPDF` library to create PDF documents and basic file handling for TXT files.

### Functions

#### `save_title_result_to_pdf(clean_result, project_name)`
- **Purpose**: Saves the result of a title search to a PDF file.
- **Parameters**:
  - `clean_result` (dict): Contains cleaned search results with keys like `TITLE_NUMBER`, `ADDRESS`, `PRICE`, and `OWNERS`.
  - `project_name` (str): The name of the project, used to create a folder for saving the PDF.
- **Details**:
  - Creates a new PDF document with a title and date of the search.
  - Formats and adds a table with title search results.
  - Includes a list of property owners in another table.
  - Saves the PDF to a directory structure based on the `project_name`.

#### `save_company_result_to_pdf(clean_result, project_name)`
- **Purpose**: Saves the result of a company search to a PDF file.
- **Parameters**:
  - `clean_result` (dict): Contains cleaned search results with keys like `COMPANY`, `COUNTRY`, and `PROPERTIES`.
  - `project_name` (str): The name of the project, used to create a folder for saving the PDF.
- **Details**:
  - Creates a new PDF document with a title and date of the search.
  - Formats and adds a description of the company and its properties.
  - Includes a table with property details.
  - Saves the PDF to a directory structure based on the `project_name`.

#### `save_fuzzy_result_to_txt(project_name, search_term, results)`
- **Purpose**: Saves the results of a fuzzy search to a TXT file.
- **Parameters**:
  - `project_name` (str): The name of the project, used to create a folder for saving the TXT file.
  - `search_term` (str): The search term used in the fuzzy search.
  - `results` (list): List of results from the fuzzy search.
- **Details**:
  - Creates a TXT file with the search term in its name.
  - Writes each result to a new line in the file.
  - Saves the file to a directory structure based on the `project_name`.

### File Structure
- **PDF Files**: Saved in a directory `results/{project_name}/` with filenames indicating the type of result (e.g., `title_{title_number}.pdf`, `company_{company}.pdf`).
- **TXT Files**: Saved in a directory `results/{project_name}/` with filenames based on the search term (e.g., `fuzzy_{search_term}.txt`).


### Usage
Call the appropriate function (`save_title_result_to_pdf`, `save_company_result_to_pdf`, or `save_fuzzy_result_to_txt`) with the required parameters to save the results of a search to a file.







## License

Copyright (c) 2024 Joshua Mock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Acknowledgements
This programme is made possible using the datasets and API provided by the [UK Land Registry](https://use-land-property-data.service.gov.uk/).
