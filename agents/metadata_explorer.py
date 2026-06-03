import json


def get_metadata():

    with open(
        "metadata/data_catalog.json",
        "r"
    ) as file:

        data = json.load(file)

    return data