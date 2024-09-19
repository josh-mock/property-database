from property_database import PropertyDatabase
from save_results import save_title_result_to_pdf, save_company_result_to_pdf, save_fuzzy_result_to_txt
from tabulate import tabulate
import numpy as np
import textwrap

def menu(database: PropertyDatabase):
    menu_options = ('t', 'c', 'x', 'f')
    project_name = input("\nENTER PROJECT NAME: ").lower()

    while True:
        print("\n** MENU **")
        print("t = search by title number")
        print("c = search by company name")
        print("f = search for company names (fuzzy search)")
        print("x = exit")

        user_input = input("Enter an option: ").lower()

        if user_input in menu_options:
            if user_input == "t":
                title_search(database, project_name, title_number=None)

            elif user_input == "c":
                company_search(database, project_name, company=None)

            elif user_input == "f":
                fuzzy_search(database, project_name, search_term=None)

            elif user_input == "x":
                print("Bye!")
                break

        else:
            print("\nOPTION NOT AVAILABLE")


def title_search(database, project_name, title_number=None):
    if title_number is None:
        title_number = input("ENTER TITLE NUMBER: ").upper()

    result = database.perform_title_search(title_number)
    if result != 0:
        clean_result = clean_title_search_result(result)
        print_title_search_result(clean_result)
        save_title_result_to_pdf(clean_result, project_name)
        print("\nRESULT SAVED AS A PDF.\n")
    else:
        print(f"\nNo results for title_number '{title_number}'.")


def company_search(database, project_name, company=None):
    if company is None:
        company = input("ENTER COMPANY NAME: ").upper()

    result = database.perform_company_search(company)
    if result == 0:
        print(f"\nNo results for company {company}.")
    else:
        clean_result = clean_company_search_result(result)
        print_company_search_result(result)
        save_company_result_to_pdf(clean_result, project_name)

def fuzzy_search(database, project_name, search_term=None):
    if search_term is None:
        search_term = input("ENTER SEARCH TERM: ").upper()

    results = database.perform_fuzzy_search(search_term)
    if len(results) == 0:
        print(f"No results for company names containing search term '{search_term}'.")

    else:
        print(f"{len(results)} results for company names containing search term '{search_term}'.")
        save_fuzzy_result_to_txt(project_name, search_term, results)


def print_title_search_result(clean_result):
    print(f"\nSEARCH RESULTS FOR TITLE NUMBER {clean_result["TITLE_NUMBER"]}\n")
    print(tabulate([["TITLE NUMBER","ADDRESS","PRICE LAST PAID"],[clean_result["TITLE_NUMBER"], clean_result["ADDRESS"], clean_result['PRICE']]], headers="firstrow", tablefmt="simple_grid"))
    print(f"\nTITLE NUMBER {clean_result["TITLE_NUMBER"]} IS OWNED BY THE FOLLOWING COMPANY/COMPANIES:\n")
    print(tabulate(clean_result['OWNERS'], headers="keys", tablefmt="simple_grid"))
    print(f"\nTHE PROPERTY MAY HAVE OTHER OWNERS NOT COVERED IN THE CCOD AND/OR OCOD DATABASES\n")


def clean_title_search_result(result: dict) -> dict:
    # Check if 'PRICE' is NaN and replace with 'No data'
    if np.isnan(result['PRICE']):
        result['PRICE'] = 'NO DATA'
    else:
        # Format PRICE as GBP with thousands separator and no decimal points
        result['PRICE'] = f"GBP {int(result['PRICE']):,}"

    # Check if address is None and replace with 'No data'
    if result['ADDRESS'] is None:
        result['ADDRESS'] = 'NO DATA'
    else:
        # Wrap text
        result['ADDRESS'] = "\n".join(textwrap.wrap(result['ADDRESS'], width=60))

    # Format country
    for owner in result['OWNERS']:
        if owner['COUNTRY'] is None and owner['SOURCE'] == "CCOD":
            owner['COUNTRY'] = 'UK'
        elif owner['COUNTRY'] is None and owner['SOURCE'] == "OCOD":
            owner['COUNTRY'] = 'NO DATA'

        owner.pop('SOURCE', None)

    return result


def print_company_search_result(cleaned_result):
    print(f"\nSEARCH RESULTS FOR COMPANY {cleaned_result['COMPANY']}\n")
    if cleaned_result['COUNTRY'] != "NO DATA":
        print(f"\n{cleaned_result['COMPANY']} IS INCORPORATED IN {cleaned_result['COUNTRY']}\n")
    print("\nTHE COMPANY OWNS THE FOLLOWING PROPERTIES:\n")
    print(tabulate(cleaned_result['PROPERTIES'], headers="keys", tablefmt="simple_grid"))


def clean_company_search_result(result: dict) -> dict:
    # Format country
    if result['COUNTRY'] is None and result['SOURCE'] == "CCOD":
        result['COUNTRY'] = 'UK'
    elif result['COUNTRY'] is None and result['SOURCE'] == "OCOD":
        result['COUNTRY'] = 'NO DATA'

    result.pop('SOURCE', None)

    # Check if 'PRICE' is NaN and replace with 'No data'
    for property in result['PROPERTIES']:
        if np.isnan(property['PRICE LAST PAID']):
            property['PRICE LAST PAID'] = 'NO DATA'
        else:
            # Format PRICE as GBP with thousands separator and no decimal points
            property['PRICE LAST PAID'] = f"GBP {int(property['PRICE LAST PAID']):,}"

        # Check if address is None and replace with 'No data'
        if property['ADDRESS'] is None:
            property['ADDRESS'] = 'NO DATA'
        else:
            # Wrap text
            property['ADDRESS'] = "\n".join(textwrap.wrap(property['ADDRESS'], width=60))

    return result


def main():
    menu(PropertyDatabase())

if __name__ == "__main__":
    main()
