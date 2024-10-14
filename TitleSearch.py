import sqlite3
from constants import DATABASE
from tkinter import ttk, filedialog, messagebox
import tkinter as tk
import csv
from fpdf import FPDF
from datetime import datetime
from utils import back_button


class TitleSearch:
    def __init__(self, master):
        self.frame = master

        # Entry box for title number
        self.title_number_frame = tk.LabelFrame(
            self.frame, pady=10, borderwidth=0)
        self.title_number_frame.pack(padx=10, pady=10)

        self.title_number_label = ttk.Label(
            self.title_number_frame, text="Enter Title Number:")
        self.title_number_label.pack(side="left", padx=5, pady=5)

        self.title_number_entry = ttk.Entry(self.title_number_frame, width=30)
        self.title_number_entry.pack(side="left", padx=5, pady=5)

        self.search_button = ttk.Button(
            self.title_number_frame, text="Search", command=self.perform_title_search)
        self.search_button.pack(side="left", padx=5, pady=5)

        self.results_frame = None

    def get_title_number(self):
        return self.title_number_entry.get().upper()

    def get_title_address_price(self, title_number):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        query = """
        SELECT
            address,
            price
        FROM
            titles
        WHERE
            title_number = ?
        """
        cursor.execute(query, (title_number,))
        result = cursor.fetchall()
        conn.close()
        return result

    def get_title_owner_info(self, title_number):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        query = """
        SELECT
            owners.owner,
            owners.country,
            owners.source
        FROM
            owners
        JOIN
            titles_owners ON owners.owner_id = titles_owners.owner_id
        WHERE
            titles_owners.title_id = (
                SELECT title_id FROM titles WHERE title_number = ?
            );
        """
        cursor.execute(query, (title_number,))
        result = cursor.fetchall()
        conn.close()
        return result

    def create_result(self, title_number, title_info, owner_info):
        """Create a structured result dictionary."""
        address, price = title_info[0]

        price = f"GBP {int(price):,}" if price else None

        owners = [{"company": owner[0], "country": owner[1],
                   "source": owner[2]} for owner in owner_info]

        for owner in owners:
            if owner["country"] is None and owner["source"] == "CCOD":
                owner["country"] = "UK"
            elif owner["country"] is None and owner["source"] == "OCOD":
                owner["country"] = ""

        result = {
            'title_number': title_number,
            'address': address,
            'price': price,
            'owners': owners
        }

        return result

    def perform_title_search(self):
        # Get input from entry
        title_number = self.get_title_number()

        if not title_number:
            messagebox.showwarning(
                "Input Error", "Please enter a title number.")
            return

        # Clear any previous search results
        self.clear_previous_search_results()

        title_info = self.get_title_address_price(title_number)

        if not title_info:
            messagebox.showinfo(
                "No Results", f"No results found for '{title_number}'.")
            return

        owner_info = self.get_title_owner_info(title_number)

        result = self.create_result(title_number, title_info, owner_info)

        self.display_results(result)

    def display_results(self, result):
        title_number = result["title_number"]
        address = result["address"]
        price = result["price"]
        owners = result["owners"]

        # Create a frame to hold the result
        self.results_frame = ttk.LabelFrame(
            self.frame, borderwidth=0)
        self.results_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Display the owner information
        heading = tk.Label(self.results_frame, text="Search Results")
        heading.pack(padx=10, pady=10)

        # Construct display text
        display_text = ""
        if address and price:
            display_text = f"{title_number} is located at {
                address}.\n\nThe price last paid for the property was {price}."
        elif address:
            display_text = f"{title_number} is located at {address}."
        elif price:
            display_text = f"The price last paid for the property was {price}."

        company_info_label = tk.Label(
            self.results_frame, text=display_text, wraplength=600)
        company_info_label.pack(padx=10, pady=10)

        # Create the table with owners' information
        self.create_table(self.results_frame, owners)

        # Show options to save as PDF or CSV
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(pady=10)

        # Create the buttons
        save_as_pdf_button = ttk.Button(
            button_frame, text="PDF", command=lambda: self.save_title_result_as_pdf(result)
        )
        save_as_pdf_button.pack(side="left", padx=5)

        save_as_csv_button = ttk.Button(button_frame, text="CSV", command=lambda: self.save_title_result_as_csv(
            result["title_number"], result["owners"]))
        save_as_csv_button.pack(side="left", padx=5)

    def create_table(self, master, owners):
        """Create a table to display data in the results frame."""
        self.tree = ttk.Treeview(master, columns=(
            "Company", "Country"), height=5, show='headings')

        # Set column headings
        self.tree.heading("Company", text="Company")
        self.tree.heading("Country", text="Country")

        # Set column widths
        self.tree.column("Company", width=250, anchor=tk.CENTER)
        self.tree.column("Country", width=100, anchor=tk.CENTER)

        self.tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Insert data into the table
        for owner in owners:
            self.tree.insert('', tk.END, values=(
                owner["company"], owner["country"]))

    def save_title_result_as_csv(self, title_number, owners):
        """Save the result to a CSV file."""
        default_filename = f"{title_number}_search_results.csv"

        # Open a file selection dialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_filename,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return

        # Prepare data for CSV
        header = ["Company", "Country"]

        with open(file_path, mode='w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)

            for owner in owners:
                writer.writerow([
                    owner["company"],
                    owner["country"]
                ])

    def clear_previous_search_results(self):
        """Clear previous results if they exist."""
        if self.results_frame:
            self.results_frame.pack_forget()

    def save_title_result_as_pdf(self, result):
        def create_title_pdf():
            pdf = FPDF()
            pdf.add_page()  # Add a page before adding content

            title_number = result["title_number"]
            address = result["address"]
            price = result["price"]
            owners = result["owners"]

            # Set the font for the title and add it
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(w=0, h=10, txt=f'Title Search Results: {
                     title_number}', border=0, align='C')
            pdf.ln(10)  # Add a line break

            # Add the current date and time
            now = datetime.now()
            formatted_date = now.strftime("Produced on %d %B %Y at %H:%M")
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(w=0, h=10, txt=formatted_date, border=0, align='C')
            pdf.ln(10)  # Add a line break

            # Add property details
            pdf.set_font("Helvetica", "", 10)
            if address and price:
                display_text = f"{title_number} is located at {
                    address}.\n\nThe price last paid for the property was {price}."
            elif address:
                display_text = f"{title_number} is located at {address}."
            elif price:
                display_text = f"The price last paid for the property was {
                    price}."
            else:
                display_text = "No address or price information available."

            # Use multi_cell to wrap text
            pdf.multi_cell(0, 10, display_text, align='C')
            pdf.ln(10)  # Add a line break

            # Add owners' information as a table
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(90, 10, "Owner", 1, 0, 'C')
            pdf.cell(90, 10, "Country", 1, 1, 'C')

            pdf.set_font("Helvetica", "", 8)
            for owner in owners:
                pdf.cell(90, 10, owner["company"], 1, 0, 'C')
                pdf.cell(90, 10, owner["country"], 1, 1, 'C')

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

        pdf = create_title_pdf()
        save_pdf(pdf, result["title_number"])
