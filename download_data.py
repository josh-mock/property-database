from tkinter import messagebox
from constants import DATASETS_COLUMNS, DTYPE_DICT, DATABASE
from download_data_utils import get_raw_data, load_data, concatenate, create_titles_table, create_owners_table, create_titles_owners_table, save_to_db
import os


def download_data(api_entry, month_combobox, year_combobox):
    get_raw_data(api_entry, month_combobox, year_combobox)

    ocod_df = load_data("ocod.csv", DATASETS_COLUMNS["ocod"], DTYPE_DICT, "OCOD")
    ccod_df = load_data("ccod.csv", DATASETS_COLUMNS["ccod"], DTYPE_DICT, "CCOD")

    combined_data = concatenate(ocod_df, ccod_df)

    titles = create_titles_table(combined_data)

    owners = create_owners_table(combined_data)

    titles_owners = create_titles_owners_table(combined_data, titles, owners)

    # Save the tables to an SQLite .db file
    save_to_db(titles, "titles", DATABASE)
    save_to_db(owners, "owners", DATABASE)
    save_to_db(titles_owners, "titles_owners", DATABASE)

    os.remove("ocod.csv")
    os.remove("ccod.csv")

    messagebox.showinfo(title="Success", message="Download completed")
