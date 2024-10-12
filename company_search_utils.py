import tkinter as tk
from tkinter import LabelFrame
import sqlite3
import threading

class CompanySearchEntry:
    def __init__(self, master):
        # Initialize the owners list when the class is created
        self.owners = self.get_owners_list()
        # Initialize the frame within the parent (frame) passed as 'master'
        self.frame = master

        # Frame for search box and label
        company_entry_frame = LabelFrame(self.frame, pady=10, borderwidth=0)
        company_entry_frame.pack(padx=10, pady=10, side=tk.TOP)

        # Label widget for company name
        self.label = tk.Label(company_entry_frame, text="Enter company name")
        self.label.pack(padx=5, pady=5, side=tk.LEFT)

        # Entry widget for user input
        self.entry = tk.Entry(company_entry_frame)
        self.entry.pack(pady=5, padx=5, side=tk.RIGHT)
        # Bind key release event
        self.entry.bind("<KeyRelease>", self.on_key_release)

        # Listbox to display suggestions
        self.listbox = tk.Listbox(self.frame)
        self.listbox.pack(fill=tk.X, side=tk.BOTTOM, pady=5)

        self.listbox.bind("<ButtonRelease-1>",
                          self.on_listbox_select)  # Bind click event

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
                    # Add matching owner to listbox
                    self.listbox.insert(tk.END, owner)

    def on_listbox_select(self, event):
        # Get the currently selected item
        try:
            selected_index = self.listbox.curselection()  # Get the index of the selected item
            if selected_index:  # Check if anything is selected
                selected_word = self.listbox.get(selected_index)  # Get the selected item
                self.entry.delete(0, tk.END)  # Clear the entry
                self.entry.insert(0, selected_word)  # Insert the selected owner into the entry
                self.listbox.delete(0, tk.END)  # Clear the listbox suggestions
        except tk.TclError:
            pass
