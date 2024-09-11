# COPYRIGHT (C) 2024 JOSHUA MOCK MIT LICENSE
import requests
import urllib.request
from zipfile import ZipFile
import os
import pandas as pd
import re

def get_valid_api_key():
    api_key_pattern = re.compile(r"^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$")

    while True:
        api_key = input("ENTER YOUR API KEY: ")

        if api_key_pattern.match(api_key):
            return api_key
        else:
            print("Invalid API key format. Please ensure your API key follows the format:")
            print("8 alphanumeric lowercase characters - 4 alphanumeric lowercase characters - 4 alphanumeric lowercase characters - 4 alphanumeric lowercase characters - 12 alphanumeric lowercase characters")

def get_valid_month():
    while True:
        month = input("ENTER MONTH (MM) DATASET WAS PUBLISHED: ")

        if len(month) == 2 and month.isdigit():
            try:
                month_int = int(month)
                if 1 <= month_int <= 12:
                    # Return the month as a two-digit string with leading zero if necessary
                    return f"{month_int:02d}"
                else:
                    print("Month must be between 01 and 12.")
            except ValueError:
                print("Invalid input. Please enter a valid month.")
        else:
            print("Invalid month format. Please enter a two-digit month.")

def get_valid_year():
    while True:
        year = input("ENTER YEAR (YYYY) DATASET WAS PUBLISHED: ")
        if len(year) == 4 and year.isdigit():
            try:
                year_int = int(year)
                if 1900 <= year_int <= 2100:  # Example range
                    return year_int
                else:
                    print("Year must be between 1900 and 2100.")
            except ValueError:
                print("Invalid input. Please enter a valid year.")
        else:
            print("Invalid year format. Please enter a four-digit year.")

def get_csv_files(dataset_name, year, month, api_key):
    file_name = f"{dataset_name.upper()}_FULL_{year}_{month}.zip"
    headers = {"Authorization": f"{api_key}", "Accept": "application/json"}
    response = requests.get(fr"https://use-land-property-data.service.gov.uk/api/v1/datasets/{dataset_name}/{file_name}", headers=headers)

    data = response.json()

    download_url = data["result"]["download_url"]
    zip_file = f"{dataset_name.upper()}.zip"
    csv_file = f"{dataset_name.upper()}.csv"

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
    data = pd.read_csv(file_path, encoding="utf-8",
                       usecols=columns, dtype=dtypes)

    filtered_data = data[data["Title Number"] != "Row Count"]

    filtered_data["source"] = source

    return filtered_data


def concatenate(ocod_df: pd.DataFrame, ccod_df: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([ocod_df, ccod_df], axis=0, join="outer", ignore_index=True)


def create_titles_table(df: pd.DataFrame) -> pd.DataFrame:
    """Create the 'Titles' table with unique IDs and clean text data."""

    # Select the relevant columns and create a copy
    titles = df[["Title Number", "Property Address",
                 "Price Paid", "source"]].copy()

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


def save_to_parquet(df: pd.DataFrame, file_path: str):
    """Save a DataFrame to a Parquet file, ensuring the directory exists."""
    # Extract the directory from the file path
    dir_name = os.path.dirname(file_path)

    # Create the directory if it doesn't exist
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # Save the DataFrame to the Parquet file
    df.to_parquet(file_path, index=False)


def main():
    # Get csv files from the dataset using the API

    year = get_valid_year()
    month = get_valid_month()
    api_key = get_valid_api_key()

    print("Downloading datasets...")
    get_csv_files("ocod", year, month, api_key)
    get_csv_files("ccod", year, month, api_key)

    ocod_columns_to_load = ["Title Number", "Property Address", "Price Paid", "Proprietor Name (1)", "Proprietor Name (2)", "Proprietor Name (3)", "Proprietor Name (4)",
                            "Country Incorporated (1)", "Country Incorporated (2)", "Country Incorporated (3)", "Country Incorporated (4)"]
    ccod_columns_to_load = ["Title Number", "Property Address", "Price Paid",
                            "Proprietor Name (1)", "Proprietor Name (2)", "Proprietor Name (3)", "Proprietor Name (4)"]
    dtype_dict = {"Title Number": "string", "Property Address": "string", "Price Paid": "float", "Proprietor Name (1)": "string", "Proprietor Name (2)": "string", "Proprietor Name (3)": "string", "Proprietor Name (4)": "string",
                  "Country Incorporated (1)": "string", "Country Incorporated (2)": "string", "Country Incorporated (3)": "string", "Country Incorporated (4)": "string"}

    print("Loading datasets...")
    ocod_df = load_data("ocod.csv",
                        ocod_columns_to_load, dtype_dict, "OCOD")
    ccod_df = load_data("ccod.csv",
                        ccod_columns_to_load, dtype_dict, "CCOD")

    print("Merging datasets...")
    combined_data = concatenate(ocod_df, ccod_df)

    print("Creating database tables...")
    titles = create_titles_table(combined_data)
    owners = create_owners_table(combined_data)
    titles_owners = create_titles_owners_table(combined_data, titles, owners)

    print("Saving database tables as parquet files...")
    save_to_parquet(titles, r"data/titles.parquet")
    save_to_parquet(owners, r"data/owners.parquet")
    save_to_parquet(titles_owners, r"data/titles_owners.parquet")

    print("Removing csv files...")
    os.remove("ccod.csv")
    os.remove("ocod.csv")

    print("Database built.")


if __name__ == "__main__":
    main()
