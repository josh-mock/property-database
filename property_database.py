# COPYRIGHT (C) 2024 JOSHUA MOCK MIT LICENSE
import pandas as pd

class PropertyDatabase:
    # Tables
    owners = pd.read_parquet(r"data/owners.parquet")
    titles = pd.read_parquet(r"data/titles.parquet")
    title_owners = pd.read_parquet(r"data/titles_owners.parquet")

    def __init__(self):
        self.owners = PropertyDatabase.owners
        self.titles = PropertyDatabase.titles
        self.titles_owners = PropertyDatabase.titles_owners

    def perform_title_search(self, title_number=None) -> dict:
        if title_number is None:
            title_number = input("ENTER TITLE_NUMBER: ").upper()

        try:
            titles_owners_joined = pd.merge(self.titles, self.titles_owners, on='title_id')
            final_df = pd.merge(titles_owners_joined, self.owners, on='owner_id')
            filtered_df = final_df[final_df['title_number'] == title_number]

            result = {
            'TITLE_NUMBER': filtered_df['title_number'].iloc[0],
            'ADDRESS': filtered_df['address'].iloc[0],
            'PRICE': filtered_df['price'].iloc[0],
            'OWNERS': filtered_df.apply(lambda row: {'OWNER': row['owner'], 'COUNTRY': row['country']}, axis=1).tolist()}

            return result

        except IndexError:
            print(f"No results for title number '{title_number}'")
            return

    def perform_company_search(self, company=None) -> dict:
        if company is None:
            company = input("ENTER COMPANY NAME: ").upper()
        try:
            titles_owners_joined = pd.merge(self.titles, self.titles_owners, on='title_id')
            final_df = pd.merge(titles_owners_joined, self.owners, on='owner_id')
            filtered_df = final_df[final_df['owner'] == company]

            result = {
                'owner': company,
                'country': filtered_df['country'].iloc[0],
                'properties': filtered_df.apply(lambda row: {
                    'title_number': row['title_number'],
                    'address': row['address'],
                    'price': row['price']
                }, axis=1).tolist()
            }

            return result

        except IndexError:
            print(f"No results for company '{company}'")
            return

if __name__ == "__main__":
    db = PropertyDatabase()
