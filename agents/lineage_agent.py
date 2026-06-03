import json


def get_lineage(table_name):

    with open(
        "metadata/lineage.json",
        "r"
    ) as file:

        lineage_data = json.load(file)

    if table_name not in lineage_data:

        return f"No lineage found for {table_name}"

    lineage = lineage_data[table_name]

    return " -> ".join(lineage)