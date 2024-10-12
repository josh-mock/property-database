import tkinter as tk
import datetime
from tkinter import ttk
from tkinter import *
from home_utils import clear_current_window, center_window
from CompanySearch import CompanySearch
from download_data import download_data


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


def show_menu():
    # Clear the current window content
    clear_current_window(root)

    # Create menu buttons
    options = [
        {"text": "Download dataset", "command": open_download_data},
        {"text": "Search by company name", "command": open_company_search_window},
        {"text": "Search by title number", "command": open_title_search_window},
        {"text": "Quit", "command": root.destroy}
    ]

    for option in options:
        button = ttk.Button(root, text=option["text"], command=option["command"])
        button.pack(anchor="center", pady=10)


def open_download_data():
    # Clear the current window content
    clear_current_window(root)

    # entry box for api key
    api_entry_frame = LabelFrame(root, pady=10, borderwidth=0)
    api_entry_frame.pack(padx=10, pady=10)  # pack the frame into the root window

    api_label = ttk.Label(api_entry_frame, text="Enter API Key:")
    api_label.pack(side="left", padx=5, pady=5)  # Place label on the left side

    api_entry = ttk.Entry(api_entry_frame, show="*", width=30)
    api_entry.pack(side="left", padx=5, pady=5)  # Place entry to the right of the label

    # Dropdown for dataset date
    date_entry_frame = LabelFrame(root, pady=10, borderwidth=0)
    date_entry_frame.pack(padx=10, pady=10)  # pack the frame into the root window

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December']

    years = [str(year) for year in range(2018, (datetime.datetime.now().year)+1)]  # Dropdown for years 2017 onwards

    date_label = ttk.Label(date_entry_frame, text="Enter dataset publication date:")
    date_label.pack(side="left", padx=5, pady=5)

    month_combobox = ttk.Combobox(date_entry_frame, values=months, width=12)
    month_combobox.pack(side="left", padx=5, pady=5)

    year_combobox = ttk.Combobox(date_entry_frame, values=years, width=12)
    year_combobox.pack(side="left", padx=5, pady=5)

    buttons_frame = LabelFrame(root, pady=10, borderwidth=0)
    buttons_frame.pack(padx=10, pady=10)  # pack the frame into the root window

    # Create buttons below the entry and dropdowns
    downlaod_data_button = ttk.Button(buttons_frame, text="Download Data", command=lambda: download_data(api_entry, month_combobox, year_combobox))
    downlaod_data_button.pack()

    back_button = ttk.Button(root, text="Back to Menu", command=show_menu)
    back_button.pack()


def open_company_search_window():
    # Clear the current window content
    clear_current_window(root)

    # Create a frame for company search entry
    company_entry_frame = ttk.LabelFrame(root, borderwidth=0)
    company_entry_frame.pack(padx=10, pady=10)

    # Replace ttk.Entry with the custom AutocompleteEntry
    company_entry = CompanySearch(company_entry_frame)

    # Force window to update to avoid needing to move it
    root.update_idletasks()  # Update all pending tasks
    root.update()  # Force a full window redraw

    # Back button to return to the menu
    back_button = ttk.Button(root, text="Back to Menu", command=show_menu)
    back_button.pack(pady=10)


def open_title_search_window():
    # Clear the current window content
    clear_current_window(root)

    # entry box for title number
    title_number_frame = LabelFrame(root, pady=10, borderwidth=0)
    title_number_frame.pack(padx=10, pady=10)

    title_number_label = ttk.Label(title_number_frame, text="Enter Title Number:")
    title_number_label.pack(side="left", padx=5, pady=5)

    title_number_entry = ttk.Entry(title_number_frame, width=30)
    title_number_entry.pack(side="left", padx=5, pady=5)  # Place entry to the right of the label

    search_button = ttk.Button(root, text="Search", command=lambda: None)
    search_button.pack(pady=10)

    back_button = ttk.Button(root, text="Back to Menu", command=show_menu)
    back_button.pack(pady=10)

# Create the main window
root = tk.Tk()

# Center the window
center_window(root, WINDOW_WIDTH, WINDOW_HEIGHT)

# Set the title of the window
root.title("UK Property Company Search")

# Show the main menu initially
show_menu()

# Run the application
root.mainloop()
