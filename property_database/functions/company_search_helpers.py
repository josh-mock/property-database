import sqlite3


def get_owner_info(DATABASE, owner):
    """Fetch owner information from the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    query = """
    SELECT
        country,
        source
    FROM
        owners
    WHERE
        owner = ?
    """
    cursor.execute(query, (owner,))
    result = cursor.fetchall()
    conn.close()
    return result


def get_titles_for_company(DATABASE, owner):
    """Fetch titles associated with the owner from the database."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    query = """
    SELECT
        titles.title_number,
        titles.address,
        titles.price
    FROM
        titles
    JOIN
        titles_owners ON titles_owners.title_id = titles.title_id
    WHERE
        titles_owners.owner_id = (
            SELECT owner_id FROM owners WHERE owner = ?
        );
    """
    cursor.execute(query, (owner,))
    result = cursor.fetchall()
    conn.close()

    return result


def format_incorporation_info(owner, owner_info):
    country, source = owner_info[0]

    if country is None and source == "CCOD":
        country = "UK"

    if country is not None:
        return f"{owner} is incorporated in {country}."

    return None


def format_titles(titles_info):
    titles = [{"title_number": title[0], "address": title[1],
               "price": title[2]} for title in titles_info]

    for title in titles:
        if title["price"]:
            title["price"] = f"GBP {int(title["price"]):,}"
        elif title["price"] is None:
            title["price"] = "No data"

    return titles
