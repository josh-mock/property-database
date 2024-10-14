import sqlite3
from constants import DATABASE
from tkinter import ttk
import tkinter as tk


def get_title_number(title_number_entry):
    return title_number_entry.get().upper()


def get_title_address_price(title_number):
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


def get_title_owner_info(title_number):
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


def create_result(title_number, title_info, owner_info):
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


def display_result(result, master):
    title_number = result["title_number"]
    address = result["address"]
    price = result["price"]
    owners = result["owners"]

    # Create a frame to hold the result
    results_frame = ttk.LabelFrame(
        master, text="Search Results", borderwidth=0)
    results_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Construct display text
    if address and price:
        display_text = f"{title_number} is located at {
            address}.\n\nThe price last paid for the property was {price}."
    elif address:
        display_text = f"{title_number} is located at {address}."
    elif price:
        display_text = f"The price last paid for the property was {price}."

    company_info_label = tk.Label(
        results_frame, text=display_text, wraplength=600)
    company_info_label.pack(padx=10, pady=10)

    # Create the table with owners' information
    create_table(results_frame, owners)


def create_table(master, owners):
    """Create a table to display data in the results frame."""
    tree = ttk.Treeview(master, columns=(
        "Company", "Country"), show='headings')

    # Set column headings
    tree.heading("Company", text="Company")
    tree.heading("Country", text="Country")

    # Set column widths
    tree.column("Company", width=250, anchor=tk.CENTER)
    tree.column("Country", width=100, anchor=tk.W)

    tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Insert data into the table
    for owner in owners:
        tree.insert('', tk.END, values=(owner["company"], owner["country"]))
