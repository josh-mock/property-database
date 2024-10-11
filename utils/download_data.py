import re
from tkinter import messagebox
import urllib.request
from zipfile import ZipFile
import requests
import os


DATASETS = [
    {
        "name": "ocod",
        "columns_to_load": [
            "Title Number",
            "Property Address",
            "Price Paid",
            "Proprietor Name (1)",
            "Proprietor Name (2)",
            "Proprietor Name (3)",
            "Proprietor Name (4)",
            "Country Incorporated (1)",
            "Country Incorporated (2)",
            "Country Incorporated (3)",
            "Country Incorporated (4)",
        ],
    },
    {
        "name": "ccod",
        "columns_to_load": [
            "Title Number",
            "Property Address",
            "Price Paid",
            "Proprietor Name (1)",
            "Proprietor Name (2)",
            "Proprietor Name (3)",
            "Proprietor Name (4)",
        ],
    }
]

DTYPE_DICT = {
    "Title Number": "object",
    "Property Address": "object",
    "Price Paid": "float",
    "Proprietor Name (1)": "object",
    "Proprietor Name (2)": "object",
    "Proprietor Name (3)": "object",
    "Proprietor Name (4)": "object",
    "Country Incorporated (1)": "object",
    "Country Incorporated (2)": "object",
    "Country Incorporated (3)": "object",
    "Country Incorporated (4)": "object"}



def validate_api_key(api_entry):
    api_key_pattern = re.compile(
        r"^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$")
    api_key = api_entry.get()

    if api_key_pattern.match(api_key):
        return api_key
    else:
        messagebox.showerror("Error", "Invalid API key.")


def validate_date(month_combobox, year_combobox):
    month = month_combobox.get()
    year = year_combobox.get()

    if month and year:
        return month, year
    elif month and not year:
        messagebox.showerror("Error", "Missing dataset publication year")
    elif year and not month:
        messagebox.showerror("Error", "Missing dataset publication month")
    else:
        messagebox.showerror(
            "Error", "Missing dataset publication month and year")


def convert_month(month):
    month_to_number = {
        "January": "01",
        "February": "02",
        "March": "03",
        "April": "04",
        "May": "05",
        "June": "06",
        "July": "07",
        "August": "08",
        "September": "09",
        "October": "10",
        "November": "11",
        "December": "12"
    }

    return month_to_number.get(month)


def download_data(api_entry, month_combobox, year_combobox):
    # Get csv files from the dataset using the API
    api_key = validate_api_key(api_entry)
    if not api_key:
        return

    date = validate_date(month_combobox, year_combobox)
    if not date:
        return

    month, year = date

    month = convert_month(month)

    for data in DATASETS:
        dataset = data["name"]

        file_name = f"{dataset.upper()}_FULL_{year}_{month}.zip"
        headers = {"Authorization": f"{api_key}", "Accept": "application/json"}
        response = requests.get(
            fr"https://use-land-property-data.service.gov.uk/api/v1/datasets/{dataset}/{file_name}", headers=headers)

        downloaded_data = response.json()

        download_url = downloaded_data["result"]["download_url"]
        zip_file = f"{dataset.upper()}.zip"
        csv_file = f"{dataset.upper()}.csv"

        urllib.request.urlretrieve(download_url, zip_file)

        with ZipFile(zip_file, "r") as zip:
            file_name = zip.namelist()[0]
            zip.extractall()
            os.rename(file_name, csv_file)

        os.remove(zip_file)




    ocod_df = load_data("ocod.csv", DATASETS["ocod"]["columns_to_load"], DTYPE_DICT, "OCOD")
#     print("Loading CCOD dataset...")
#     ccod_df = load_data("ccod.csv",
#                         ccod_columns_to_load, dtype_dict, "CCOD")

#     print("Merging datasets...")
#     combined_data = concatenate(ocod_df, ccod_df)

#     print("Creating database table: titles...")
#     titles = create_titles_table(combined_data)
#     print("Creating database table: owners...")
#     owners = create_owners_table(combined_data)
#     print("Creating database table: titles_owners...")
#     titles_owners = create_titles_owners_table(combined_data, titles, owners)

#     if not os.path.exists('data'):
#         os.makedirs('data')
#     print("Saving database tables as parquet files...")
#     save_to_parquet(titles, r"data/titles.parquet")
#     save_to_parquet(owners, r"data/owners.parquet")
#     save_to_parquet(titles_owners, r"data/titles_owners.parquet")

#     print("Removing csv files...")
#     os.remove("ccod.csv")
#     os.remove("ocod.csv")

#     print("Database built.")
