# COPYRIGHT (C) 2024 JOSHUA MOCK MIT LICENSE
import pandas as pd
from property_database import PropertyDatabase

def menu(database: pd.DataFrame):
    menu_options = ('t', 'c', 'x')

    while True:
        print("\n** MENU **")
        print("t = search by title number")
        print("c = search by company name")
        print("x = exit")

        print()
        user_input = input("Enter an option: ").lower()

        if user_input in menu_options:
            if user_input == "t":
                database.title_search()
                menu(database)

            elif user_input == "c":
                database.company_search()
                menu(database)

            elif user_input == "x":
                exit("Bye!")

        else:
            print("\nOPTION NOT AVAILABLE")

def main():
    database = PropertyDatabase()
    menu(database)

if __name__ == "__main__":
    main()
