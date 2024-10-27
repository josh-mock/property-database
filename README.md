# UK OCOD and CCOD Database
Version 2.0.0

This programme merges the OCOD and CCOD datasets released by the UK land registry into one searchable database.

## Installation

Download the release from the release page or clone the repository from GitHub

```bash
git clone https://github.com/jwmock88/property-database
```

Install the required pip packages

```python
pip install -r requirements.txt
```

## Usage

```python
python run uk-land-registry-search
```

## Features
- **Download data sets**: You can download the Overseas Companies That Own Property In England And Wales Datasets ('OCOD') and the UK Companies That Own Property In England And Wales Datasets ('CCOD') published between 2018 and now. The programme cleans and merges the data
- **Company search**: Search a company name to see what title numbers it is listed as owning. The feature has an autocomplete search bar to help you find your company in the dataset. Provides title numbers, addresses, and price last paid.
- **Title search**: Search a title number to see what companies are listed as owning it. Provides detail on the owners' countries of incorporation.
- **Result export**: Export search results as CSVs or PDFs.

## Acknowledgements

Datasets provided by HM Land Registry under licence. You must have an API key to access the datasets.

## License

MIT License

Copyright (c) 2024 Joshua Mock

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

