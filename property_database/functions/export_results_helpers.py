from fpdf import FPDF
import os
import shutil
import csv


def reset(file_directory):
    if os.path.exists(file_directory):
        shutil.rmtree(file_directory)
        os.makedirs(file_directory, exist_ok=True)


def create_file_names(query, file_directory):
    os.makedirs(file_directory, exist_ok=True)
    return (fr"{file_directory}/{query}.pdf", fr"{file_directory}/{query}.csv")


def create_pdf(company, incorporation_statement, number_of_properties, titles, filename):
    pdf = FPDF()
    pdf.add_page()  # Add a page before adding content

    # Set the font for the title and add it
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(w=0, h=10, txt=f"Company Search Results: {
        company}", border=0, align="C")
    pdf.ln(10)
    # Add property details
    pdf.set_font("Helvetica", "", 10)
    if incorporation_statement:
        # Use multi_cell to wrap text
        pdf.multi_cell(0, 10, incorporation_statement, align="C")
        pdf.ln(10)  # Add a line break

    pdf.multi_cell(0, 10, number_of_properties, align="C")
    pdf.ln(10)  # Add a line break
    pdf.set_font("Helvetica", "", size=8)

    with pdf.table(text_align="CENTER") as table:
        # Add headers to the table for owner data
        headers = ["Title Number", "Address", "Price"]
        header_row = table.row()
        for header in headers:
            header_row.cell(header)

        # Add the owner data rows
        for title in titles:
            owner_row = table.row()
            owner_row.cell(title["title_number"])
            owner_row.cell(title["address"])
            owner_row.cell(title["price"])

    return pdf.output(filename)


def create_csv(titles, filename):

    # Prepare data for CSV
    header = ["Title number", "Address", "price"]

    with open(filename, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)

        for title in titles:
            writer.writerow([
                title["title_number"],
                title["address"],
                title["price"],
            ])


def export_result_as_files(company, incorporation_statement, number_of_properties, titles, file_directory):
    output_pdf_file_name, output_csv_file_name = create_file_names(
        company, file_directory)
    create_pdf(company, incorporation_statement,
               number_of_properties, titles, output_pdf_file_name)
    create_csv(titles, output_csv_file_name)


def find_file_by_extension(directory, extension):
    # List all files in the specified directory
    for filename in os.listdir(directory):
        # Check if the file has the specified extension (e.g., .pdf or .csv)
        if filename.endswith(extension):
            file_path = os.path.join(directory, filename)
            return file_path  # Return the full path of the file

    # If no file with the given extension is found, return None
    return None


def create_titles_result_pdf(title_number, formatted_title_details, owners, filename):
    pdf = FPDF()
    pdf.add_page()  # Add a page before adding content

    # Set the font for the title and add it
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(w=0, h=10, txt=f"Title Search Results: {
        title_number}", border=0, align="C")
    pdf.ln(10)
    # Add property details
    pdf.set_font("Helvetica", "", 10)
    if formatted_title_details:
        # Use multi_cell to wrap text
        if formatted_title_details["address"]:
            pdf.multi_cell(
                0, 10, text=formatted_title_details["address"], align="C")
            pdf.ln(10)  # Add a line break
        if formatted_title_details["price"]:
            pdf.multi_cell(
                0, 10, text=formatted_title_details["price"], align="C")
            pdf.ln(10)  # Add a line break

    pdf.set_font("Helvetica", "", size=8)

    with pdf.table(text_align="CENTER") as table:
        # Add headers to the table for owner data
        headers = ["Title Number", "Address", "Price"]
        header_row = table.row()
        for header in headers:
            header_row.cell(header)

        # Add the owner data rows
        for owner in owners:
            owner_row = table.row()
            owner_row.cell(owner["company"])
            owner_row.cell(owner["country"])
    return pdf.output(filename)


def create_titles_result_csv(owners, filename):

    # Prepare data for CSV
    header = ["Title number", "Address", "price"]

    with open(filename, mode="w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)

        for owner in owners:
            writer.writerow([
                owner["company"],
                owner["country"]
            ])


def export_title_search_result_as_files(title_number, formatted_title_details, owners, file_directory):
    output_pdf_file_name, output_csv_file_name = create_file_names(
        title_number, file_directory)
    create_titles_result_pdf(
        title_number, formatted_title_details, owners, output_pdf_file_name)
    create_titles_result_csv(owners, output_csv_file_name)
