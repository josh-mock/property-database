import tkinter as tk
import datetime
from tkinter import ttk
from CompanySearch import CompanySearch
from download_data import download_data
from TitleSearch import TitleSearch
from constants import WINDOW_WIDTH, WINDOW_HEIGHT



def download_data_window():
    # Clear the current window content
    clear_current_window(root)

    # Entry frame for api entry
    api_entry_frame = ttk.Frame(root, borderwidth=0)
    api_entry_frame.pack(padx=10, pady=10)

    api_label = ttk.Label(api_entry_frame, text="Enter API Key:")
    api_label.pack(side="left", padx=5, pady=5)  # Place label on the left side

    api_entry = ttk.Entry(api_entry_frame, show="*", width=30)
    api_entry.pack(side="left", padx=5, pady=5)

    # Dropdown for dataset date
    date_entry_frame = ttk.Frame(root, pady=10, borderwidth=0)
    date_entry_frame.pack(padx=10, pady=10)

    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]

    # Dropdown for years 2018 onwards
    years = [str(year)
             for year in range(2018, (datetime.datetime.now().year)+1)]

    date_label = ttk.Label(
        date_entry_frame, text="Enter dataset publication date:")
    date_label.pack(side="left", padx=5, pady=5)

    month_combobox = ttk.Combobox(date_entry_frame, values=months, width=12)
    month_combobox.pack(side="left", padx=5, pady=5)

    year_combobox = ttk.Combobox(date_entry_frame, values=years, width=12)
    year_combobox.pack(side="left", padx=5, pady=5)

    buttons_frame = ttk.Frame(root, pady=10, borderwidth=0)
    buttons_frame.pack(padx=10, pady=10)

    # Create buttons below the entry and dropdowns
    downlaod_data_button = ttk.Button(buttons_frame, text="Download Data", command=lambda: download_data(
        root, api_entry, month_combobox, year_combobox))
    downlaod_data_button.pack(pady=10)

    back_button(buttons_frame, show_menu)


def open_company_search_window():
    # Clear the current window content
    clear_current_window(root)

    # Create a frame for company search entry
    company_search_frame = ttk.Frame(root, borderwidth=0)
    company_search_frame.pack(padx=10, pady=10, fill="x")

    CompanySearch(company_search_frame)

    # Force window to update
    root.update_idletasks()  # Update all pending tasks
    root.update()  # Force a full window redraw

    # Back button to return to the menu
    back_button(root, show_menu)


def open_title_search_window():
    clear_current_window(root)

    title_search_frame = ttk.Frame(root, borderwidth=0)
    title_search_frame.pack(padx=10, pady=10)

    TitleSearch(title_search_frame)

    back_button(root, show_menu)


def center_window(window, width, height):
    # Get the screen dimensions
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate the x and y coordinates for the Tk window
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # Set the geometry of the window
    window.geometry(f"{width}x{height}+{x}+{y}")


def clear_current_window(root):
    for widget in root.winfo_children():
        widget.destroy()


def back_button(root, command):
    # Create a reusable back button
    back_button = ttk.Button(root, text="Back to Menu", command=command)
    back_button.pack()
    return back_button


def make_label(master, text):
    label = ttk.Label(master, text=text)
    label.pack()
    return label

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
        button.pack(pady=10)


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
