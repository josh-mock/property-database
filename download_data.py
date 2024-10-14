from tkinter import messagebox, ttk
from constants import DATASETS_COLUMNS, DTYPE_DICT, DATABASE
from download_data_utils import get_raw_data, load_data, concatenate, create_titles_table, create_owners_table, create_titles_owners_table, save_to_db
from home_utils import make_label
import os
import threading


def download_data(root, api_entry, month_combobox, year_combobox):

    # Create and display the progress bar
    pb = ttk.Progressbar(
        root,
        orient='horizontal',
        mode='indeterminate',
        length=280)
    pb.pack(pady=20)
    pb.start()  # Start the progress bar

    def download_task():
        try:
            progress_label = make_label(root, text="Downloading datasets")

            response = get_raw_data(api_entry, month_combobox, year_combobox)

            if response == 1:
                return

            progress_label.destroy()

            progress_label = make_label(root, text="Cleaning data")

            ocod_df = load_data(
                "ocod.csv", DATASETS_COLUMNS["ocod"], DTYPE_DICT, "OCOD")
            ccod_df = load_data(
                "ccod.csv", DATASETS_COLUMNS["ccod"], DTYPE_DICT, "CCOD")

            progress_label.destroy()

            progress_label = make_label(root, text="Combining datasets")

            combined_data = concatenate(ocod_df, ccod_df)

            titles = create_titles_table(combined_data)

            owners = create_owners_table(combined_data)

            titles_owners = create_titles_owners_table(combined_data, titles, owners)

            progress_label.destroy()

            progress_label = make_label(root, "Creating database")

            # Save the tables to an SQLite .db file
            save_to_db(titles, "titles", DATABASE)
            save_to_db(owners, "owners", DATABASE)
            save_to_db(titles_owners, "titles_owners", DATABASE)

            progress_label.destroy()

            progress_label = make_label(root, "Cleaning up")

            os.remove("ocod.csv")
            os.remove("ccod.csv")

            progress_label.destroy()

            # Stop the progress bar and remove it from the UI
            pb.stop()
            pb.pack_forget()

            messagebox.showinfo(title="Success", message="Download completed")

        except Exception as e:
            pb.stop()
            pb.pack_forget()
            progress_label.destroy()
            messagebox.showinfo(title="Error", message=f"Error downloading data: {e}")

    # Run the download task in a separate thread to avoid blocking the UI
    threading.Thread(target=download_task).start()
