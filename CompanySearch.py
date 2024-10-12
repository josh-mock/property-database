import tkinter as tk
from tkinter import LabelFrame, ttk, messagebox
import sqlite3
from constants import DATABASE

class CompanySearch:
    def __init__(self, master):
        # Initialize the owners list when the class is created
        self.owners = self.get_owners_list()
        # Initialize the frame within the parent (frame) passed as 'master'
        self.frame = master

        # Frame for search box and label
        self.company_entry_frame = ttk.Frame(self.frame)
        self.company_entry_frame.pack(padx=10, pady=10, side=tk.TOP)

        # Label widget for company name
        self.label = tk.Label(self.company_entry_frame, text="Enter company name")
        self.label.pack(padx=5, pady=5, side=tk.LEFT)

        # Entry widget for user input
        self.entry = tk.Entry(self.company_entry_frame)
        self.entry.pack(pady=5, padx=5, side=tk.LEFT)
        # Bind key release event
        self.entry.bind("<KeyRelease>", self.on_key_release)

        # Search button
        self.search_button = ttk.Button(self.company_entry_frame, text="Search", command=self.perform_search)
        self.search_button.pack(pady=5, padx=5, side=tk.LEFT)

        # Listbox to display suggestions
        self.listbox = tk.Listbox(self.frame)
        self.listbox.pack(fill=tk.X, side=tk.BOTTOM, pady=5)

        self.listbox.bind("<ButtonRelease-1>",
                          self.on_listbox_select)  # Bind click event

    def get_input(self):
        """Method to get the current input from the entry widget."""
        return self.entry.get()

    def get_owners_list(self):
        # Connect to the SQLite database and fetch owners list
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT owner FROM owners")
        results = cursor.fetchall()
        conn.close()

        # Return the list of owners
        return [result[0] for result in results]

    def get_owner_info(self, owner):
        """Fetch owner information from the database."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        query = """
        SELECT
            country,
            source
        FROM
            owners
        WHERE
            owner = ?
        """
        cursor.execute(query, (owner,))
        result = cursor.fetchall()
        conn.close()
        return result

    def get_titles_for_company(self, owner):
        """Fetch titles associated with the owner from the database."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        query = """
        SELECT
            titles.title_number,
            titles.address,
            titles.price
        FROM
            titles
        JOIN
            titles_owners ON titles_owners.title_id = titles.title_id
        WHERE
            titles_owners.owner_id = (
                SELECT owner_id FROM owners WHERE owner = ?
            );
        """
        cursor.execute(query, (owner,))
        result = cursor.fetchall()
        conn.close()
        return result

    def create_result(self, owner, owner_info, titles_info):
        """Create a structured result dictionary."""
        country, source = owner_info[0]

        if country is None and source == "CCOD":
            country = 'the UK'

        titles = [{"title_number": title[0], "address": title[1], "price": title[2]} for title in titles_info]

        result = {
            'owner': owner,
            'country': country,
            'properties': titles
        }

        return result

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

    def perform_search(self):
        """Perform the search and update the display."""
        # Get the input from the entry
        query = self.get_input()

        if not query:
            messagebox.showwarning("Input Error", "Please enter a company name.")
            return

        # remove listbox
        self.hide_listbox()

        # Fetch owner information and titles for the specified owner
        owner_info = self.get_owner_info(query)
        titles_info = self.get_titles_for_company(query)

        if not owner_info:
            messagebox.showinfo("No Results", "No results found for your search.")
            return

        # Create a structured result
        result = self.create_result(query, owner_info, titles_info)

        # Display the results
        self.display_results(result)

    def hide_listbox(self):
        """Clear the search results from the display."""
        for widget in self.frame.winfo_children():
            if isinstance(widget, tk.Listbox):
                widget.pack_forget()  # Remove any existing result frames

    def display_results(self, result):
        # define variables
        owner = result["owner"]
        country = result["country"]
        number_of_titles = len(result["properties"])

        """Display the search results in the frame."""
        # Create a new frame for displaying results
        results_frame = ttk.LabelFrame(self.frame, borderwidth=0)
        results_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Display the owner information
        heading = tk.Label(results_frame, text="Search Results")
        heading.pack(padx=10, pady=10)

        if result["country"] is not None:
            company_info_label = tk.Label(results_frame, text=f"{owner} is incorporated in {country}.")
            company_info_label.pack(padx=10, pady=10)

        count_label = tk.Label(results_frame, text=f"{number_of_titles} results for titles owned by {owner}")
        count_label.pack(padx=10, pady=10)

        # # Create a table (Treeview) for the properties
        # self.create_table(results_frame, result['properties'])

    # def create_table(self, master, data):
    #     """Create a table to display data in the results frame."""
    #     tree = ttk.Treeview(master, columns=("Title Number", "Address", "Price"), show='headings')
    #     tree.heading("Title Number", text="Title Number")
    #     tree.heading("Address", text="Address")
    #     tree.heading("Price", text="Price")
    #     tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    #     for item in data:
    #         tree.insert('', tk.END, values=(item["title_number"], item["address"], item["price"]))






