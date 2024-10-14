import re
from tkinter import messagebox
import urllib.request
from zipfile import ZipFile
import requests
import os
import pandas as pd
import sqlite3
from constants import DATASETS_COLUMNS
from datetime import datetime


def validate_api_key(api_entry):
    api_key_pattern = re.compile(
        r"^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$")
    api_key = api_entry.get()

    if api_key_pattern.match(api_key):
        return api_key
    else:
        messagebox.showerror("Error", "Invalid API key.")


def get_date(month_combobox, year_combobox):
    month = month_combobox.get()
    year = year_combobox.get()

    if not month and not year:
        messagebox.showerror(
            "Error", "Missing dataset publication month and year")
        return None

    if not month:
        messagebox.showerror("Error", "Missing dataset publication month")
        return None

    if not year:
        messagebox.showerror("Error", "Missing dataset publication year")
        return None

    # Return the valid month and year if all checks pass
    return (month, year)


def validate_date(month_year: tuple) -> tuple:
    month, year = month_year

    month = convert_month(month)

    selected_date = datetime(int(year), int(month), 1)

    current_datetime = datetime.now()
    current_month_start = datetime(
        current_datetime.year, current_datetime.month, 1)

    if selected_date > current_month_start:
        messagebox.showerror("Error", "Date cannot be in the future.")
        return 1

    return (month, year)


def convert_month(month: str) -> str:
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

    date = get_date(month_combobox, year_combobox)
    valid_date = validate_date(date)

    if valid_date == 1:
        return

    month, year = valid_date

    for dataset in DATASETS_COLUMNS.keys():
        file_name = f"{dataset.upper()}_FULL_{year}_{month}.zip"
        headers = {"Authorization": f"{api_key}", "Accept": "application/json"}

        try:
            response = requests.get(
                fr"https://use-land-property-data.service.gov.uk/api/v1/datasets/{dataset}/{file_name}",
                headers=headers
            )
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        except requests.exceptions.HTTPError as http_err:
            messagebox.showerror("HTTP Error", f"HTTP error occurred: {http_err}")
            return
        except requests.exceptions.RequestException as req_err:
            messagebox.showerror("Request Error", f"Error occurred while requesting data: {req_err}")
            return

        try:
            downloaded_data = response.json()
        except ValueError:
            messagebox.showerror("Data Error", "Received invalid JSON response.")
            return

        if "result" not in downloaded_data or "download_url" not in downloaded_data["result"]:
            messagebox.showerror("Data Error", "Download URL not found in the response.")
            return

        download_url = downloaded_data["result"]["download_url"]
        zip_file = f"{dataset.upper()}.zip"
        csv_file = f"{dataset.upper()}.csv"

        try:
            urllib.request.urlretrieve(download_url, zip_file)
        except Exception as download_err:
            messagebox.showerror("Download Error", f"Error occurred while downloading the file: {download_err}")
            return

        try:
            with ZipFile(zip_file, "r") as zip:
                if not zip.namelist():
                    raise Exception("Zip file is empty or corrupted.")
                file_name = zip.namelist()[0]
                zip.extractall()
                os.rename(file_name, csv_file)
        except Exception as zip_err:
            messagebox.showerror("Extraction Error", f"Error occurred while extracting the zip file: {zip_err}")
            return
        finally:
            # Clean up the zip file regardless of success or failure
            if os.path.exists(zip_file):
                os.remove(zip_file)

    return 0


def load_data(file_path: str, columns: list, dtypes: dict, source: str) -> pd.DataFrame:
    """Load CSV data into a DataFrame with specified columns and data types."""
    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    # Load the CSV file into a DataFrame
    data = pd.read_csv(file_path, encoding="utf-8",
                       usecols=columns, dtype=dtypes)

    filtered_data = data[data["Title Number"] != "Row Count"]

    filtered_data["source"] = source

    return filtered_data


def concatenate(ocod_df: pd.DataFrame, ccod_df: pd.DataFrame) -> pd.DataFrame:
    merged = pd.concat([ocod_df, ccod_df], axis=0, join="outer", ignore_index=True)

    for i in range(1, 5):
        merged[f"Proprietor Name ({i})"] = merged[f"Proprietor Name ({i})"].apply(clean_owner_data)

    return merged



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


def clean_owner_data(owner: str) -> str:
    """Clean the 'owner' column data."""
    if not isinstance(owner, str):
        return owner

    # Remove extra spaces and make it uppercase
    owner = re.sub(r"\s{2,}", " ", owner.strip()).upper()

    # Replace "LTD" with "LIMITED"
    owner = re.sub("LTD", "LIMITED", owner, flags=re.IGNORECASE)

    # Remove unwanted characters
    allowed_chars = r"[^()A-Z0-9&@£$€¥#.,:; ]"
    owner = re.sub(allowed_chars, "", owner, flags=re.IGNORECASE)

    return owner


def create_owners_table(df: pd.DataFrame) -> pd.DataFrame:
    """Create the 'Owners' table by unpivoting proprietor and country columns."""
    owners_list = []

    # Loop through each proprietor set (1 to 4) and their corresponding country
    for i in range(1, 5):
        proprietor_col = f"Proprietor Name ({i})"
        country_col = f"Country Incorporated ({i})"
        source = "source"

        # Select the proprietor and country columns, dropping rows with NaN proprietors
        temp_df = df[[proprietor_col, country_col, source]].dropna(subset=[proprietor_col])

        # Rename columns to common "Proprietor Name" and "Country Incorporated"
        temp_df = temp_df.rename(columns={
            proprietor_col: "owner",
            country_col: "country"
        })

        # Append to the list of owners
        owners_list.append(temp_df)

    # Concatenate all owners into a single DataFrame, remove duplicates, and add a unique ID
    owners_df = pd.concat(owners_list, ignore_index=True).drop_duplicates(subset="owner")

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
    create_indexes(db_file)
    conn.close()


def create_indexes(db_file):
    try:
        conn = sqlite3.connect(db_file)
        cur = conn.cursor()

        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_owners ON owners (owner)',
            'CREATE INDEX IF NOT EXISTS idx_owners_owner_id ON owners(owner_id)',
            'CREATE INDEX IF NOT EXISTS idx_titles_owners_owner_id ON titles_owners(owner_id)',
            'CREATE INDEX IF NOT EXISTS idx_titles_owners_title_id ON titles_owners(title_id)',
            'CREATE INDEX IF NOT EXISTS idx_titles_title_id ON titles(title_id)',
            'CREATE INDEX IF NOT EXISTS idx_titles_title_number ON titles(title_number)'
        ]

        # Create indexes if they don't already exist
        for index in indexes:
            cur.execute(index)

        # Commit the changes
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error occurred: {e}")
    finally:
        # Close the connection
        if conn:
            conn.close()
