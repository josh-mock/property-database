import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
from constants import DATABASE
import csv
from fpdf import FPDF
from datetime import datetime
from utils import clear_current_window


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
        self.label = tk.Label(self.company_entry_frame,
                              text="Enter company name")
        self.label.pack(padx=5, pady=5, side=tk.LEFT)

        # Entry widget for user input
        self.entry = tk.Entry(self.company_entry_frame)
        self.entry.pack(pady=5, padx=5, side=tk.LEFT)
        # Bind key release event
        self.entry.bind("<KeyRelease>", self.on_key_release)

        # Search button
        self.search_button = ttk.Button(
            self.company_entry_frame, text="Search", command=self.perform_search)
        self.search_button.pack(pady=5, padx=5, side=tk.LEFT)

        # Listbox for autocomplete
        self.listbox = tk.Listbox(self.frame)
        self.listbox.pack(fill=tk.X, side=tk.BOTTOM, pady=5)

        self.listbox.bind("<ButtonRelease-1>",
                          self.on_listbox_select)  # Bind click event

    def get_owner(self):
        """Method to get the current input from the entry widget"""
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
            country = "UK"

        titles = [{"title_number": title[0], "address": title[1],
                   "price": title[2]} for title in titles_info]

        for title in titles:
            if title["price"]:
                title["price"] = f"GBP {int(title["price"]):,}"
            elif title["price"] is None:
                title["price"] = ""

        result = {
            "owner": owner,
            "country": country,
            "properties": titles
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
            # Get the index of the selected item
            selected_index = self.listbox.curselection()
            if selected_index:  # Check if anything is selected
                selected_word = self.listbox.get(
                    selected_index)  # Get the selected item
                self.entry.delete(0, tk.END)  # Clear the entry
                # Insert the selected owner into the entry
                self.entry.insert(0, selected_word)
                self.listbox.delete(0, tk.END)  # Clear the listbox suggestions
        except tk.TclError:
            pass

    def perform_search(self):
        """Perform the search and update the display."""
        # Get the input from the entry
        company = self.get_owner()

        if not company:
            messagebox.showwarning(
                "Input Error", "Please enter a company name.")
            return

        # remove listbox
        self.hide_listbox()

        # Fetch owner information and titles for the specified owner
        owner_info = self.get_owner_info(company)
        if not owner_info:
            messagebox.showinfo(
                "No Results", f"No results found for '{company}'.")
            return

        titles_info = self.get_titles_for_company(company)

        # Create a structured result
        result = self.create_result(company, owner_info, titles_info)

        # Display the results
        self.display_results(result)

    def hide_listbox(self):
        """Clear the search results from the display."""
        for widget in self.frame.winfo_children():
            if isinstance(widget, tk.Listbox):
                widget.pack_forget()

    def display_results(self, result):
        """Display the search results in the frame."""
        # Create a new frame for displaying results
        self.results_frame = ttk.LabelFrame(self.frame, borderwidth=0, width=500)
        self.results_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Display the owner information
        heading = tk.Label(self.results_frame, text="Search Results")
        heading.pack(padx=10, pady=10)

        owner = result["owner"]
        country = result["country"]
        number_of_titles = len(result["properties"])

        if country is not None:
            company_info_label = tk.Label(
                self.results_frame, text=f"{owner} is incorporated in {country}.")
            company_info_label.pack(padx=10, pady=10)

        count_label = tk.Label(
            self.results_frame, text=f"{number_of_titles} results for titles owned by {owner}")
        count_label.pack(padx=10, pady=10)

        # Create a table (Treeview) for the properties
        self.create_table(self.results_frame, result["properties"])

        # Show options to save as PDF or CSV
        button_frame = ttk.Frame(self.results_frame)
        button_frame.pack(pady=10)

        # Create the buttons
        save_as_pdf_button = ttk.Button(
            button_frame, text="PDF", command=lambda: self.save_company_result_as_pdf(result)
        )
        save_as_pdf_button.pack(side="left", padx=5)

        save_as_csv_button = ttk.Button(button_frame, text="CSV", command=lambda: self.save_company_result_as_csv(
            result))
        save_as_csv_button.pack(side="left", padx=5)

        new_search_button = ttk.Button(
            self.results_frame, text="New search", command=self.reset_search
        )
        new_search_button.pack()

    def create_table(self, master, data):
        """Create a table to display data in the results frame."""
        self.tree = ttk.Treeview(master, columns=(
            "Title Number", "Address", "Price"), show="headings")

        # Set column headings
        self.tree.heading("Title Number", text="Title Number")
        self.tree.heading("Address", text="Address")
        self.tree.heading("Price", text="Price")

        # Set column widths
        # Width for Title Number
        self.tree.column("Title Number", width=25, anchor=tk.W)
        # Width for Address
        self.tree.column("Address", width=450, anchor=tk.CENTER)
        # Width for Price
        self.tree.column("Price", width=25, anchor=tk.E)

        self.tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Insert data into the table
        for item in data:
            self.tree.insert("", tk.END, values=(
                item["title_number"], item["address"], item["price"]))

    def save_company_result_as_csv(self, result):
        """Save the result to a CSV file."""

        default_filename = f"{result["owner"]}_search_results.csv"

        # Open a file selection dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_filename,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return

        # Prepare data for CSV
        header = ["Title number", "Address", "price"]

        with open(file_path, mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)

            for title in result["properties"]:
                writer.writerow([
                    title["title_number"],
                    title["address"],
                    title["price"],
                ])

    def save_company_result_as_pdf(self, result):
        def create_company_pdf():
            pdf = FPDF()
            pdf.add_page()  # Add a page before adding content

            owner = result["owner"]
            country = result["country"]
            properties = result["properties"]

            # Set the font for the title and add it
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(w=0, h=10, txt=f"Company Search Results: {
                     owner}", border=0, align="C")
            pdf.ln(10)

            # Add the current date and time
            now = datetime.now()
            formatted_date = now.strftime("Produced on %d %B %Y at %H:%M")
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(w=0, h=10, txt=formatted_date, border=0, align="C")
            pdf.ln(10)  # Add a line break

            # Add property details
            pdf.set_font("Helvetica", "", 10)
            if owner and country:
                display_text = f"{owner} is incorporated in {country}."
            else:
                display_text = "No country of incorporation information available."

            # Use multi_cell to wrap text
            pdf.multi_cell(0, 10, display_text, align="C")
            pdf.ln(10)  # Add a line break

            pdf.set_font("Helvetica", "", size=8)

            with pdf.table(text_align="CENTER") as table:
                # Add headers to the table for owner data
                headers = ["Title Number", "Address", "Price"]
                header_row = table.row()
                for header in headers:
                    header_row.cell(header)

                # Add the owner data rows
                for property in properties:
                    owner_row = table.row()
                    owner_row.cell(property["title_number"])
                    owner_row.cell(property["address"])
                    owner_row.cell(property["price"])

            return pdf

        def save_pdf(pdf, search_term):
            default_filename = f"{search_term}_search_results.pdf"

            # Open a file selection dialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                initialfile=default_filename,
                filetypes=[("PDF files", "*.pdf")])
            if not file_path:
                return

            pdf.output(file_path)  # Save the PDF to the selected path

        pdf = create_company_pdf()
        save_pdf(pdf, result["owner"])

    def reset_search(self):
        clear_current_window(self.frame)  # Clear the current window

        # Re-initialize the search interface
        self.__init__(self.frame)
