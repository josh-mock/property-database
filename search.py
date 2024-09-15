from scripts.property_database import PropertyDatabase

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
                database.title_search()

            elif user_input == "c":
                database.company_search()

            elif user_input == "x":
                print("Bye!")
                break

        else:
            print("\nOPTION NOT AVAILABLE")

def main():
    menu(PropertyDatabase())

if __name__ == "__main__":
    main()
