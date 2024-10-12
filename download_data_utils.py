import re
from tkinter import messagebox
import urllib.request
from zipfile import ZipFile
import requests
import os
import pandas as pd
import sqlite3
from download_data_constants import DATASETS_COLUMNS
from datetime import datetime


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

    if not month and not year:
        messagebox.showerror("Error", "Missing dataset publication month and year")
        return None

    if not month:
        messagebox.showerror("Error", "Missing dataset publication month")
        return None

    if not year:
        messagebox.showerror("Error", "Missing dataset publication year")
        return None

    # Check if the selected date is valid
    try:
        selected_date = datetime(int(year), int(month), 1)  # 1st day of the selected month/year
    except ValueError:
        messagebox.showerror("Error", "Invalid month or year")
        return None

    # Check if the selected date is in the future
    current_date = datetime.now()
    if selected_date > current_date:
        messagebox.showerror("Error", "Date cannot be in the future")
        return None

    # Return the valid month and year if all checks pass
    return month, year


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


def get_raw_data(api_entry, month_combobox, year_combobox):
    # Get csv files from the dataset using the API
    api_key = validate_api_key(api_entry)
    if not api_key:
        return

    date = validate_date(month_combobox, year_combobox)
    if not date:
        return

    month, year = date

    month = convert_month(month)

    for dataset in DATASETS_COLUMNS.keys():
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

def load_data(file_path: str, columns: list, dtypes: dict, source: str) -> pd.DataFrame:
    """Load CSV data into a DataFrame with specified columns and data types."""
    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    # Load the CSV file into a DataFrame
    data = pd.read_csv(file_path, encoding="utf-8", usecols=columns, dtype=dtypes)

    # Replace NaN values with "NO DATA"
    data = data.apply(lambda col: col.fillna("NO DATA") if col.name != "Price Paid" else col)

    filtered_data = data[data["Title Number"] != "Row Count"]

    filtered_data["source"] = source

    return filtered_data

def concatenate(ocod_df: pd.DataFrame, ccod_df: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([ocod_df, ccod_df], axis=0, join="outer", ignore_index=True)

def create_titles_table(df: pd.DataFrame) -> pd.DataFrame:
    """Create the 'Titles' table with unique IDs and clean text data."""

    # Select the relevant columns and create a copy
    titles = df[["Title Number", "Property Address", "Price Paid"]].copy()

    # Add unique ID for each title
    titles["title_id"] = range(1, len(titles) + 1)

    # Rename the columns
    titles = titles.rename(columns={
        "Title Number": "title_number",
        "Property Address": "address",
        "Price Paid": "price"
    })

    # Clean the data
    titles["address"] = titles["address"].apply(lambda x: re.sub(
        r"\s{2,}", " ", x.strip()).upper() if isinstance(x, str) else x)

    return titles


def create_owners_table(df: pd.DataFrame) -> pd.DataFrame:
    """Create the 'Owners' table by unpivoting proprietor and country columns."""
    owners_list = []

    # Loop through each proprietor set (1 to 4) and their corresponding country
    for i in range(1, 5):
        proprietor_col = f"Proprietor Name ({i})"
        country_col = f"Country Incorporated ({i})"
        source = "source"

        # Select the proprietor and country columns, dropping rows with NaN proprietors
        temp_df = df[[proprietor_col, country_col, source]].dropna(
            subset=[proprietor_col])

        # Rename columns to common "Proprietor Name" and "Country Incorporated"
        temp_df = temp_df.rename(columns={
            proprietor_col: "owner",
            country_col: "country"
        })

        # Clean data
        temp_df["owner"] = temp_df["owner"].apply(lambda x: re.sub(
            r"\s{2,}", " ", x.strip()).upper() if isinstance(x, str) else x)

        # Append to the list of owners
        owners_list.append(temp_df)

    # Concatenate all owners into a single DataFrame, remove duplicates, and add a unique ID
    owners_df = pd.concat(
        owners_list, ignore_index=True).drop_duplicates(subset="owner")
    # Add unique ID to each owner
    owners_df["owner_id"] = range(1, len(owners_df) + 1)

    return owners_df


def create_titles_owners_table(combined_data: pd.DataFrame, titles_df: pd.DataFrame, owners_df: pd.DataFrame) -> pd.DataFrame:
    """Create the 'Titles Owners' table and merge with the Owners table to get Owner IDs."""
    titles_owners_list = []

    for i in range(1, 5):
        proprietor_col = f"Proprietor Name ({i})"

        # Ensure the proprietor column exists in combined_data
        if proprietor_col not in combined_data.columns:
            continue  # Skip if the column doesn't exist

        # Select "Title Number" and proprietor column, drop rows with NaN proprietors
        temp_df = combined_data[["Title Number", proprietor_col]].dropna(subset=[
                                                                         proprietor_col])

        # Rename the proprietor column to "owner"
        temp_df = temp_df.rename(columns={proprietor_col: "owner"})

        titles_owners_list.append(temp_df)

    # Concatenate all proprietor entries
    titles_owners_df = pd.concat(titles_owners_list, ignore_index=True)

    # Merge with Owners table to get "owner_id"
    titles_owners_df = pd.merge(
        titles_owners_df, owners_df[["owner", "owner_id"]], on="owner", how="inner")

    # Rename 'Title Number' to 'title_number' to match titles_df
    titles_owners_df = titles_owners_df.rename(
        columns={"Title Number": "title_number"})

    # Select relevant columns
    titles_owners_df = titles_owners_df[["title_number", "owner_id"]]

    # Create a mapping from 'title_number' to 'title_id'
    title_number_to_id = titles_df.set_index(
        "title_number")["title_id"].to_dict()

    # Map 'title_number' to 'title_id'
    titles_owners_df["title_id"] = titles_owners_df["title_number"].map(
        title_number_to_id)

    # Drop 'title_number' as it's no longer needed
    titles_owners_df = titles_owners_df[["title_id", "owner_id"]]

    return titles_owners_df


def save_to_db(df: pd.DataFrame, table_name: str, db_file: str):
    """Save a DataFrame to an SQLite database."""
    conn = sqlite3.connect(db_file)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()

def create_indexes(db_file):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute('CREATE INDEX IF NOT EXISTS idx_owners ON owners (owner)')
    conn.close()

