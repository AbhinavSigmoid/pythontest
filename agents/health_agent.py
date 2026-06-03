import json


def get_pipeline_health():

    with open(
        "metadata/pipeline_health.json",
        "r"
    ) as file:

        data = json.load(file)

    return data