import tkinter as tk
from tkinter import ttk
from tkinter import *
import sqlite3


class CompanySearchEntry:
    def __init__(self, master):
        # Initialize the frame within the parent (frame) passed as 'master'
        self.frame = master

        # Initialize the owners list when the class is created
        self.owners = self.get_owners_list()

        # Frame for search box and label
        company_entry_frame = LabelFrame(self.frame, pady=10, borderwidth=0)
        company_entry_frame.pack(padx=10, pady=10, side=tk.TOP)

        # Label widget for company name
        self.label = tk.Label(company_entry_frame, text="Enter company name")
        self.label.pack(padx=5, pady=5, side=tk.LEFT)

        # Entry widget for user input
        self.entry = tk.Entry(company_entry_frame)
        self.entry.pack(pady=5, padx=5, side=tk.RIGHT)
        self.entry.bind("<KeyRelease>", self.on_key_release)  # Bind key release event

        # Listbox to display suggestions
        self.listbox = tk.Listbox(self.frame)
        self.listbox.pack(fill=tk.X, side=tk.BOTTOM, pady=5)

        self.listbox.bind("<ButtonRelease-1>", self.on_listbox_select)  # Bind click event


    def get_owners_list(self):
        # Connect to the SQLite database and fetch owners list
        conn = sqlite3.connect('data/land_property_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT owner FROM owners")
        results = cursor.fetchall()
        conn.close()

        # Return the list of owners
        return [result[0] for result in results]

    def on_key_release(self, event):
        # Clear the current suggestions
        self.listbox.delete(0, tk.END)

        # Get the text from the entry
        typed_text = self.entry.get()

        if typed_text:  # Only if there is text
            for owner in self.owners:
                if owner.lower().startswith(typed_text.lower()):  # Match case-insensitively
                    self.listbox.insert(tk.END, owner)  # Add matching owner to listbox

    def on_listbox_select(self, event):
        # Get the selected owner from the listbox and set it to the entry
        selected_word = self.listbox.get(self.listbox.curselection())
        self.entry.delete(0, tk.END)  # Clear the entry
        self.entry.insert(0, selected_word)  # Insert the selected owner
        self.listbox.delete(0, tk.END)  # Clear the listbox suggestions


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


