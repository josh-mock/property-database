import os
import re
import sqlite3
import requests
import shutil
import urllib.request
from flask import render_template
from datetime import datetime
import pandas as pd
from zipfile import ZipFile
from constants import DATABASE, DATASETS_COLUMNS, DTYPE_DICT


def validate_api_key(api_key):
    api_key_pattern = re.compile(
        r"^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$"
    )
    return api_key_pattern.match(api_key) is not None


def convert_month_to_number(month):
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


def validate_date(converted_month, input_year, current_month_start):
    input_date = datetime(input_year, converted_month, 1)

    if input_date > current_month_start:
        return False

    return True


def validate_inputs(api_key, download_option, converted_month, input_year, current_month_start):
    # Validate API key
    if not api_key:
        return "Error: Missing API key"
    elif not validate_api_key(api_key):
        return "Error: Invalid API key"

    # Validate inputs for historical downloads
    if download_option == "historical":
        if not converted_month:
            return "Error: Missing month"
        if not input_year:
            return "Error: Missing year"

        # Ensure month and year can be converted properly
        try:
            month_number = int(converted_month)
            year_number = int(input_year)
        except ValueError:
            return "Error: Invalid month or year format"

        # Check date validity
        if not validate_date(month_number, year_number, current_month_start):
            return "Error: Date cannot be in the future"

    # All checks passed
    return None


def get_file_name(download_option, dataset, input_year, converted_month, headers):
    if download_option == "historical":
        return f"{dataset.upper()}_FULL_{input_year}_{converted_month}.zip"
    if download_option == "latest":
        try:
            response = requests.get(
                fr"https://use-land-property-data.service.gov.uk/api/v1/datasets/{dataset}", headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            return f"HTTP error occurred: {http_err}"
        except requests.exceptions.RequestException as req_err:
            return f"Request error occurred: {req_err}"

        # Check and retrieve download URL
        try:
            downloaded_data = response.json()
        except ValueError as error_text:
            return f"JSON decoding error: {error_text}"

        full_file_name = next(
            (resource["file_name"] for resource in downloaded_data["result"]
             ["resources"] if resource["name"] == "Full File"),
            None
        )
        return full_file_name


def process_dataset_download(api_key, download_option, dataset, input_year, converted_month):
    headers = {"Authorization": api_key, "Accept": "application/json"}
    file_name = get_file_name(download_option, dataset,
                              input_year, converted_month, headers)

    if download_option == "latest":
        base_url = fr"https://use-land-property-data.service.gov.uk/api/v1/datasets"
    elif download_option == "historical":
        base_url = fr"https://use-land-property-data.service.gov.uk/api/v1/datasets/history"

    # Attempt to download data
    try:
        response = requests.get(
            fr"{base_url}/{dataset}/{file_name}", headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except requests.exceptions.RequestException as req_err:
        return f"Request error occurred: {req_err}"

    # Check and retrieve download URL
    try:
        downloaded_data = response.json()
    except ValueError as error_text:
        return f"JSON decoding error: {error_text}"

    if "result" not in downloaded_data or "download_url" not in downloaded_data["result"]:
        return "Download URL not found in the response."

    download_url = downloaded_data["result"]["download_url"]
    return download_and_extract_zip(download_url, dataset)


def download_and_extract_zip(download_url, dataset):
    # Define paths
    temp_dir = "instance/temp"
    zip_file = os.path.join(temp_dir, f"{dataset.upper()}.zip")
    csv_file = os.path.join(temp_dir, f"{dataset.upper()}.csv")

    # Create temp directory if it doesn't exist
    os.makedirs(temp_dir, exist_ok=True)

    # Download file
    try:
        urllib.request.urlretrieve(download_url, zip_file)
    except Exception as download_err:
        cleanup_temp(temp_dir)
        return f"Download error: {download_err}"

    # Extract file
    try:
        with ZipFile(zip_file, "r") as zip_ref:
            if not zip_ref.namelist():
                cleanup_temp(temp_dir)
                return "Zip file is empty or corrupted."
            file_name = zip_ref.namelist()[0]
            zip_ref.extractall(temp_dir)
            os.rename(os.path.join(temp_dir, file_name), csv_file)
    except Exception as zip_err:
        cleanup_temp(temp_dir)
        return f"Zip extraction error: {zip_err}"
    finally:
        if os.path.exists(zip_file):
            os.remove(zip_file)

    return None


def cleanup_temp(temp_dir):
    """Delete the contents of the temp directory."""
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)


def load_data(file_path, columns, dtypes, source):
    """Load CSV data into a DataFrame with specified columns and data types."""
    if not os.path.exists(file_path):
        return render_template("download_error.html", message=f"The file {file_path} does not exist.")

    data = pd.read_csv(file_path, encoding="utf-8",
                       usecols=columns, dtype=dtypes)

    filtered_data = data[data["Title Number"] != "Row Count"]

    filtered_data["source"] = source

    return filtered_data


def concatenate(ocod_df, ccod_df):
    merged = pd.concat([ocod_df, ccod_df], axis=0,
                       join="outer", ignore_index=True)

    for i in range(1, 5):
        merged[f"Proprietor Name ({i})"] = merged[f"Proprietor Name ({
            i})"].apply(clean_owner_data)

    return merged


def clean_owner_data(owner):
    """Clean the 'owner' column data."""
    if not isinstance(owner, str):
        return owner

    # Remove extra spaces and make it uppercase
    owner = re.sub(r"\s{2,}", " ", owner.strip()).upper()

    # Replace "LTD" with "LIMITED" to minimise duplicates
    owner = re.sub("LTD", "LIMITED", owner, flags=re.IGNORECASE)

    # Remove unwanted characters
    allowed_chars = r"[^()A-Z0-9&@£$€¥#.,:; ]"
    owner = re.sub(allowed_chars, "", owner, flags=re.IGNORECASE)

    return owner


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
        temp_df = df[[proprietor_col, country_col, source]].dropna(subset=[
                                                                   proprietor_col])

        # Rename columns to common "Proprietor Name" and "Country Incorporated"
        temp_df = temp_df.rename(columns={
            proprietor_col: "owner",
            country_col: "country"
        })

        # Append to the list of owners
        owners_list.append(temp_df)

    # Concatenate all owners into a single DataFrame, remove duplicates, and add a unique ID
    owners_df = pd.concat(
        owners_list, ignore_index=True).drop_duplicates(subset="owner")

    # Add unique ID to each owner
    owners_df["owner_id"] = range(1, len(owners_df) + 1)

    return owners_df


def create_owners_table(df: pd.DataFrame) -> pd.DataFrame:
    """Create the 'Owners' table by unpivoting proprietor and country columns."""
    owners_list = []

    # Loop through each proprietor set (1 to 4) and their corresponding country
    for i in range(1, 5):
        proprietor_col = f"Proprietor Name ({i})"
        country_col = f"Country Incorporated ({i})"
        source = "source"

        # Select the proprietor and country columns, dropping rows with NaN proprietors
        temp_df = df[[proprietor_col, country_col, source]].dropna(subset=[
                                                                   proprietor_col])

        # Rename columns to common "Proprietor Name" and "Country Incorporated"
        temp_df = temp_df.rename(columns={
            proprietor_col: "owner",
            country_col: "country"
        })

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
    """Save a DataFrame to an SQLite database and create indexes."""
    conn = sqlite3.connect(db_file)
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()

    # After saving, call create_indexes to ensure indexes are created for the table
    create_indexes(db_file, table_name)


def create_indexes(db_file, table_name=None):
    """Create indexes only if the target tables exist in the database."""
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    # Check if the specific tables exist
    if table_name:
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cur.fetchone():
            conn.close()
            return

    # Index definitions
    indexes = {
        "owners": [
            "CREATE INDEX IF NOT EXISTS idx_owners ON owners (owner)",
            "CREATE INDEX IF NOT EXISTS idx_owners_owner_id ON owners(owner_id)"
        ],
        "titles_owners": [
            "CREATE INDEX IF NOT EXISTS idx_titles_owners_owner_id ON titles_owners(owner_id)",
            "CREATE INDEX IF NOT EXISTS idx_titles_owners_title_id ON titles_owners(title_id)"
        ],
        "titles": [
            "CREATE INDEX IF NOT EXISTS idx_titles_title_id ON titles(title_id)",
            "CREATE INDEX IF NOT EXISTS idx_titles_title_number ON titles(title_number)"
        ]
    }

    # Apply indexes only if they are relevant to the table_name
    relevant_indexes = indexes.get(table_name, [])
    for index in relevant_indexes:
        cur.execute(index)

    # Commit and close
    conn.commit()
    conn.close()


def get_owners_list(db_file):
    # Connect to the SQLite database and fetch owners list
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT owner FROM owners")
    results = cursor.fetchall()
    conn.close()

    # Extract the owners into a list
    owners_list = [result[0] for result in results]

    # Convert the list to a properly formatted JavaScript array syntax
    owners_js_array = ',\n    '.join(f'"{owner}"' for owner in owners_list)
    js_content = f'let OWNERS = [\n    {owners_js_array}\n];\n'

    # Ensure the instance/owners directory exists
    output_dir = "static"
    os.makedirs(output_dir, exist_ok=True)

    # Write the JavaScript content to a file in the instance/owners directory
    js_file_path = os.path.join(output_dir, "owners.js")
    with open(js_file_path, "w") as js_file:
        js_file.write(js_content)

    return owners_list


def finalize_data_processing():
    # Load and process the datasets
    ocod_df = load_data(
        "instance/temp/ocod.csv", DATASETS_COLUMNS["ocod"], DTYPE_DICT, "OCOD")
    ccod_df = load_data(
        "instance/temp/ccod.csv", DATASETS_COLUMNS["ccod"], DTYPE_DICT, "CCOD")

    # Concatenate and process tables
    combined_data = concatenate(ocod_df, ccod_df)
    titles = create_titles_table(combined_data)
    owners = create_owners_table(combined_data)
    titles_owners = create_titles_owners_table(combined_data, titles, owners)

    # Save to database
    save_to_db(titles, "titles", DATABASE)
    save_to_db(owners, "owners", DATABASE)
    save_to_db(titles_owners, "titles_owners", DATABASE)
    get_owners_list(DATABASE)

    # Clean up
    os.remove("instance/temp/ocod.csv")
    os.remove("instance/temp/ccod.csv")
