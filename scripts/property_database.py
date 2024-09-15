# COPYRIGHT (C) 2024 JOSHUA MOCK MIT LICENSE
import pandas as pd
import sys
from tabulate import tabulate
import textwrap
from scripts.save_to_pdf import save_title_result_to_pdf, save_owner_result_to_pdf

def wrap_text(text, width=30):
    return "\n".join(textwrap.wrap(text, width))

class PropertyDatabase:
    # Constants
    OWNERS = pd.read_parquet(r"data/owners.parquet")
    TITLES = pd.read_parquet(r"data/titles.parquet")
    TITLES_OWNERS = pd.read_parquet(r"data/titles_owners.parquet")

    def __init__(self):
        self.owners = PropertyDatabase.OWNERS
        self.titles = PropertyDatabase.TITLES
        self.titles_owners = PropertyDatabase.TITLES_OWNERS

    def title_search(self, title_number=None):
        if title_number is None:
            title_number = input("ENTER TITLE NUMBER: ").upper()

        def get_title_data():
            result = self.titles[self.titles["title_number"] == title_number]
            if result.empty:
                sys.exit(f"No results for {title_number}.")
            return result

        def get_address(result: pd.DataFrame) -> str:
            address = result["address"].values[0]
            return wrap_text(address.upper(), width=60) if not pd.isna(address) else "No data"

        def get_price(result: pd.DataFrame) -> str:
            price = result["price"].values[0]
            return f"GBP {price:,.0f}" if not pd.isna(price) else "No data"

        def get_title_id(result: pd.DataFrame) -> str:
            return result["title_id"].values[0]

        def format_title_data_output(result, title_number: int) -> None:
            address = get_address(result)
            price = get_price(result)
            table = [[title_number, address, price]]
            headers = ["TITLE NUMBER", "PROPERTY ADDRESS", "PRICE PAID"]
            print(tabulate(table, headers=headers, tablefmt="simple_grid"))
            return (address, price)

        def get_owner_data(title_id: int) -> pd.DataFrame:
            owner_data = self.titles_owners[self.titles_owners["title_id"] == title_id]
            owner_ids = owner_data["owner_id"].unique()
            return self.owners[self.owners["owner_id"].isin(owner_ids)]

        def get_owner_name(owner: pd.Series, owner_data: pd.DataFrame) -> str:
            return owner_data.loc[owner.name, "owner"]

        def get_owner_country(owner: pd.Series, owner_data: pd.DataFrame) -> str:
            source = owner_data.loc[owner.name, "source"]
            country = owner_data.loc[owner.name, "country"]
            if source == "CCOD":
                return "UK"
            elif pd.notna(country):
                return country
            else:
                return "No data"

        def format_owner_data_output(result):
            owners_list = []
            title_id = get_title_id(result)
            owner_data = get_owner_data(title_id)
            for _, owner in owner_data.iterrows():
                name = get_owner_name(owner, owner_data)
                country = get_owner_country(owner, owner_data)
                owners_list.append([name, country])
            table = owners_list
            headers = ["OWNER", "COUNTRY OF INCORPORATION"]
            print(tabulate(table, headers=headers, tablefmt="simple_grid"))
            return owners_list

        print(f"\n~SEARCH RESULTS FOR TITLE NUMBER {title_number}~\n")
        result = get_title_data()
        address, price = format_title_data_output(result, title_number)
        print(f"\nTITLE NUMBER {title_number} IS OWNED BY THE FOLLOWING COMPANY/COMPANIES:\n")
        owners_list = format_owner_data_output(result)
        header = ["OWNER", "COUNTRY OF INCORPORATION"]
        # Insert the header row at position 0
        owners_list.insert(0, header)
        print(f"\nTHE PROPERTY MAY HAVE OTHER OWNERS NOT COVERED IN THE CCOD AND/OR OCOD DATABASES\n")
        save_title_result_to_pdf(title_number, address, price, owners_list)
        print("\nSEARCH RESULT SAVED AS PDF.")


    def company_search(self, company=None):
        if company is None:
            company = input("ENTER COMPANY NAME: ").upper()
        def get_company_data():
            result = self.owners[self.owners["owner"] == company]
            if result.empty:
                sys.exit(f"No results for company {company}.")
            return result

        def get_owner_country(owner_data: pd.DataFrame) -> str:
            source = owner_data["source"].values[0]
            country = owner_data["country"].values[0]
            if source == "CCOD":
                return "UK"
            elif pd.notna(country):
                return country
            else:
                return "No data"

        def get_owner_id(owner_data: pd.DataFrame):
            return owner_data["owner_id"].values[0]

        def get_title_ids(owner_id: int) -> list:
            subset = self.titles_owners[self.titles_owners["owner_id"] == owner_id]
            return subset["title_id"].values

        def get_title_information(title_ids: list) -> str:
            titles = self.titles_owners[self.titles_owners["title_id"].isin(title_ids)]
            info = self.titles[self.titles["title_id"].isin(title_ids)]
            titles_with_info = titles.merge(info, on="title_id", how="inner")
            complete_info = titles_with_info.merge(self.owners, on="owner_id", how="inner")
            result = complete_info[complete_info["title_id"].isin(title_ids)]
            titles_owned = result[["title_number", "address", "price"]].rename(columns={"title_number": "TITLE NUMBER", "address": "ADDRESS", "price": "PRICE"})
            raw = titles_owned.to_dict(orient="records")

            def get_price(price: float) -> str:
                return f"GBP {price:,.0f}" if not pd.isna(price) else "No data"

            def get_address(address: str) -> str:
                return wrap_text(address.upper(), width=60) if not pd.isna(address) else "No data"

            for title in raw:
                title["ADDRESS"] = get_address(title["ADDRESS"])
                title["PRICE"] = get_price(title["PRICE"])

            print(tabulate(raw, headers="keys", tablefmt="simple_grid", showindex=False))
            return raw

        owner_data = get_company_data()
        country = get_owner_country(owner_data)
        owner_id = get_owner_id(owner_data)
        title_ids = get_title_ids(owner_id)


        print(f"\n\n~SEARCH RESULTS FOR {company}~\n")
        print(f"\n{company} IS INCORPORATED IN {country}\n")
        print("\nTHE COMPANY OWNS THE FOLLOWING PROPERTIES:\n")
        title_information = get_title_information(title_ids)
        save_owner_result_to_pdf(company, country, title_information)
        print("\nSEARCH RESULT SAVED AS PDF.")
if __name__ == "__main__":
    db = PropertyDatabase()
