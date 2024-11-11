import sqlite3


def get_title_info(database, title_number):
    conn = sqlite3.connect(database)
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


def format_title_info(title_number, raw_title_details):
    address, price = raw_title_details[0]
    price = f"GBP {int(price):,}" if price else None
    address_statement = f"{title_number} is located at {address}." if address else None
    price_statement = f"{title_number} was last purchased for {price}." if price else None

    return {"address": address_statement, "price": price_statement}


def get_owners_for_title_number(database, title_number):
    conn = sqlite3.connect(database)
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

def get_owners_from_raw_owner_info(raw_owner_info):
    owners = [{"company": owner[0], "country": owner[1],
                "source": owner[2]} for owner in raw_owner_info]
    for owner in owners:
        if owner["country"] is None and owner["source"] == "CCOD":
            owner["country"] = "UK"
        elif owner["country"] is None and owner["source"] == "OCOD":
            owner["country"] = "No data"

    return owners
