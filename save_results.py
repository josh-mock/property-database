import os
from fpdf import FPDF
from datetime import datetime

def save_title_result_to_pdf(clean_result, project_name):
    pdf = FPDF()
    title_number = clean_result['TITLE_NUMBER']
    address = clean_result['ADDRESS']
    price = clean_result['PRICE']
    pdf.add_page()
    # Title of the PDF

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(w=0, h=10, text=f'RESULTS OF TITLE SEARCH: {title_number}', border=0, align='C')
    pdf.ln()  # Add some space after the title

    now = datetime.now()
    formatted_date = now.strftime("Searched on %d %B %Y at %H:%M")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(w=0, h=10, text=f'{formatted_date}', border=0, align='C')
    pdf.ln()


    title_table_data = (
        ("TITLE NUMBER", "ADDRESS", "PRICE LAST PAID"),
        (title_number, address, price)
    )

    pdf.set_font("Helvetica", "", size=8)

    with pdf.table(text_align="CENTER") as table:
        for data_row in title_table_data:
            row = table.row()
            for datum in data_row:
                row.cell(datum)


    pdf.ln()
    pdf.set_font("Helvetica", "", size=10)
    pdf.cell(w=0, h=10, text=f'{title_number} IS OWNED BY THE FOLLOWING COMPANY/COMPANIES:', border=0, align='C')
    pdf.ln()

    pdf.set_font("Helvetica", "", size=8)

    with pdf.table(text_align="CENTER") as table:
        # Add headers to the table for owner data
        headers = ['OWNER', 'COUNTRY']
        header_row = table.row()
        for header in headers:
            header_row.cell(header)

        # Add the owner data rows
        for owner in clean_result['OWNERS']:
            owner_row = table.row()
            owner_row.cell(owner['OWNER'])
            owner_row.cell(owner['COUNTRY'])

    pdf.ln()
    pdf.set_font("Helvetica", "", size=10)
    pdf.multi_cell(w=0, h=10, text=f'THE PROPERTY MAY HAVE OTHER OWNERS NOT COVERED IN THE CCOD AND/OR OCOD DATABASES', border=0, align='C')

    if not os.path.exists(rf'results/{project_name}'):
        os.makedirs(f'results/{project_name}')

    filename = os.path.join(fr'results/{project_name}', f"{title_number}.pdf")

    pdf.output(filename)

def save_owner_result_to_pdf(company, country, title_information):
    pdf = FPDF()
    pdf.add_page()
    # Title of the PDF

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(w=0, h=10, text=f'RESULTS OF COMPANY SEARCH: {company}', border=0, align='C')
    pdf.ln()  # Add some space after the title

    now = datetime.now()
    formatted_date = now.strftime("Searched on %d %B %Y at %H:%M")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(w=0, h=10, text=f'{formatted_date}', border=0, align='C')
    pdf.ln()

    pdf.set_font("Helvetica", "", 8)
    pdf.multi_cell(w=0, h=10, text=f'{company} INCORPORATED IN {country} OWNS THE FOLLOWING PROPERTY/PROPERTIES:', border=0, align='C')

    pdf.set_font("Helvetica", "", size=8)

    table_data = []
    header = list(title_information[0].keys())
    table_data.append(header)

    for i in range(len(title_information)):
        c = list(title_information[i].values())
        table_data.append(c)

    with pdf.table(text_align="CENTER") as table:
        for data_row in table_data:
            row = table.row()
            for datum in data_row:
                row.cell(datum)

    if not os.path.exists('results'):
        os.makedirs('results')

    # Define the filename with the folder path
    filename = os.path.join('results', f"{datetime.now().strftime('%y%m%d')}_{company}.pdf")

    # Save the PDF to the specified path
    pdf.output(filename)