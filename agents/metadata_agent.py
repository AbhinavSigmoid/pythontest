import json


def get_table_info(table_name):

    with open(
        "metadata/tables.json",
        "r"
    ) as file:

        tables = json.load(file)

    for table in tables:

        if table["table_name"] == table_name:

            return table

    return None


def get_pii_tables():

    with open(
        "metadata/tables.json",
        "r"
    ) as file:

        tables = json.load(file)

    pii_tables = []

    for table in tables:

        if table["contains_pii"]:

            pii_tables.append(
                table["table_name"]
            )

    return pii_tables