from title_search_utils import get_title_number, get_title_address_price, get_title_owner_info, create_result, display_result
from tkinter import messagebox


def perform_title_search(title_number_entry, root):
    title_number = get_title_number(title_number_entry)

    if not title_number:
        messagebox.showwarning("Input Error", "Please enter a title number.")
        return

    title_info = get_title_address_price(title_number)

    if not title_info:
        messagebox.showinfo(
            "No Results", f"No results found for '{title_number}'.")
        return

    owner_info = get_title_owner_info(title_number)

    result = create_result(title_number, title_info, owner_info)

    display_result(result, root)
