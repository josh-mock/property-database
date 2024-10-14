import tkinter as tk
import datetime
from tkinter import ttk
from tkinter import *
from utils import clear_current_window, center_window, back_button
from CompanySearch import CompanySearch
from TitleSearch import TitleSearch
from DownloadData import DownloadData
from constants import WINDOW_WIDTH, WINDOW_HEIGHT


def show_menu():
    # Clear the current window content
    clear_current_window(root)

    # Create menu buttons
    options = [
        {"text": "Download dataset", "command": download_data_window},
        {"text": "Search by company name", "command": open_company_search_window},
        {"text": "Search by title number", "command": open_title_search_window},
        {"text": "Quit", "command": root.destroy}
    ]

    for option in options:
        button = ttk.Button(
            root, text=option["text"], command=option["command"])
        button.pack(anchor="center", pady=10)


def download_data_window():
    # Clear the current window content
    clear_current_window(root)
    download_data = DownloadData
    back_button(root, show_menu)


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
    back_button(root, show_menu)


def open_title_search_window():
    # Clear the current window content
    clear_current_window(root)

    title_search_frame = ttk.LabelFrame(root, borderwidth=0)
    title_search_frame.pack(padx=10, pady=10)

    title_search = TitleSearch(title_search_frame)

    back_button(root, show_menu)


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
