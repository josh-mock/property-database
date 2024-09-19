# UK Land Registry CCOD and OCOD Database
Version: 1.1.0

This project builds a database for searching the CCOD and OCOD datasets released by the [UK Land Registry](https://use-land-property-data.service.gov.uk/).

## Installation

Install by downloading from the repository into your selected folder. Then run ```pip install -r requirements.txt```

## Usage
The project is designed for use with two connected scripts.

### `build.py`
`build.py` is used to construct the database. The user enters `build` into the terminal to run. The user is asked to input the year and month in which the datasets they wish to search were published. The user then needs to provide a valid API key for the OCOD and CCOD datasets which can be obtained [here](https://use-land-property-data.service.gov.uk/datasets/ocod#access) subject to the UK Land Registry's license.

The database is then constructed by loading the csv files obtained from the API call into `Pandas.DataFrame()`, splitting the data into titles, owners, and titles owners tables, and saving the tables as parquet files in a `/data` directory.

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


## Future improvements
- **Chunking**: `build.py` is memory intensive in the loading and saving to parquet sections. Chunking would reduce memory usage in the process.
- **Export ability**: Users will be able to export search results in a variety of file formats.
- **Graphical User Interface**: Creating  a GUI will make the search function more user friendly.
- **More data sets**: The project currently supports searching data from one month. OCOD and CCOD data is available dating back to 2015, and future versions of the project will allow a user to search historical records for companies and titles.
- **Bulk search**: You will be able to have a list of companeis and search in buulk. 

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
