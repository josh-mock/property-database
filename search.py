from property_database import PropertyDatabase
from tabulate import tabulate
import textwrap

def menu(database: PropertyDatabase):
    menu_options = ('t', 'c', 'x')

    while True:
        print("\n** MENU **")
        print("t = search by title number")
        print("c = search by company name")
        print("x = exit")

        user_input = input("Enter an option: ").lower()

        if user_input in menu_options:
            if user_input == "t":
                title_number = input("ENTER TITLE NUMBER: ").upper()
                result = database.perform_title_search(title_number)
                print_title_search_result(result)

            elif user_input == "c":
                company = input("ENTER COMPANY NAME: ").upper()
                result = database.perform_company_search(company)
                print_company_search_result(result)

            elif user_input == "x":
                print("Bye!")
                break

        else:
            print("\nOPTION NOT AVAILABLE")

def print_title_search_result(title_number, result):
    if result == 0:
        print(f"\nNo results for title_number '{title_number}'.")
    else:
        print(f"\nSEARCH RESULTS FOR TITLE NUMBER {result["TITLE_NUMBER"]}\n")
        print(tabulate([["TITLE NUMBER","ADDRESS","PRICE LAST PAID"],[result["TITLE_NUMBER"], "\n".join(textwrap.wrap(result['ADDRESS'], width=60)), result['PRICE']]], headers="firstrow", tablefmt="simple_grid"))
        print(f"\nTITLE NUMBER {result["TITLE_NUMBER"]} IS OWNED BY THE FOLLOWING COMPANY/COMPANIES:\n")
        print(tabulate(result['OWNERS'], headers="keys", tablefmt="simple_grid"))
        print(f"\nTHE PROPERTY MAY HAVE OTHER OWNERS NOT COVERED IN THE CCOD AND/OR OCOD DATABASES\n")

def print_company_search_result(company, result):
    if result == 0:
        print(f"\nNo results for company {company}.")

    else:
        print(f"\nSEARCH RESULTS FOR COMPANY {result['COMPANY']}\n")
        print(f"\n{result['COMPANY']} IS INCORPORATED IN {result['COUNTRY']}\n")
        print("\nTHE COMPANY OWNS THE FOLLOWING PROPERTIES:\n")

        # Wrap the addresses for each property
        for property_dict in result['PROPERTIES']:
            property_dict['ADDRESS'] = "\n".join(textwrap.wrap(property_dict['ADDRESS'], width=60))

        # Display the properties in a table
        print(tabulate(result['PROPERTIES'], headers="keys", tablefmt="simple_grid"))



def main():
    menu(PropertyDatabase())

if __name__ == "__main__":
    main()
