# UK Land Registry CCOD and OCOD Database
Version: 1.2.0

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

- Run the script using ```python build.py`` You will be prompted for:
  - An API key (which should follow the format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).
  - The year (YYYY) and month (MM) for the dataset you want to process.

- The script will:
   - Download and unzip the datasets.
   - Load the data and process it into three tables: titles, owners, and titles_owners.
   - Save the tables as Parquet files in the data directory.
   - Clean up intermediate CSV files.

### Output
The script produces three parquet files: 
1. data/titles.parquet: Contains unique property titles with price and address.
2. data/owners.parquet: Contains owner information, including country of incorporation.
3. data/titles_owners.parquet: Contains the relationship between titles and owners.

### Error Handling
1. **Invalid API Key**: The script checks if the API key matches the expected UUID pattern. If not, it will ask you to re-enter a valid key.
2. **Invalid Month/Year Input**: If the month or year input is invalid, the script prompts for a correct value.
3. **File Not Found**: If the downloaded CSV files are missing or the provided path is incorrect, the script raises a FileNotFoundError.


### `search.py`
`search.py` creates an instance of the `PropertyDatabase` using `property_database.py`. The `PropertyDatabase` currently supports two search functions. The user enters `search` into the terminal to search. 
#### `title_search`
The user enters a title number via `input`. The function then searches the `PropertyDatabase` for records and returns the following information in two tables:

- Title Number
- Address associated with that title number
- The price last paid to acquire the property associated with that title number
- The names of UK companies ('UK company' as defined by the [UK Land Registry](https://use-land-property-data.service.gov.uk/datasets/ccod/tech-spec)) which own the property
- The names of overseas comapnies ('overseas company' as defined by the [UK Land Registry](https://use-land-property-data.service.gov.uk/datasets/ocod/tech-spec)) which own the property

Note that titles may have owners which are not covered in the scopes of the OCOD and CCOD datasets.

The search result is saved in a folder called "results" in PDF format. 

#### `company_search`
The user enters a company name via `input()`. The function then searches the `PropertyDatabase` for records and returns the following information:

- The company's country/jurisdiction of incorporation
- Title numbers owned by the company
- Addresses associated with each title number
- The price last paid to acquire the property associated with that title number

The search result is saved in a folder called "results" in PDF format. 

#### `fuzzy_search`
Used for finding a company's name as recorded in the dataset. This is currently only available for companies not incorporated in the UK.

The user enters a search term when prompted. Optionally, the user can then add a jurisdiction. These are currently not standardised and are based on how the jurisdictions are written in the dataset. A future version of the project will standardise the jurisdictions

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
