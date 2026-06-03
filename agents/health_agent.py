import json


def get_pipeline_health():

    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parent.parent

    with open(BASE_DIR / "metadata" / "pipeline_health.json", "r") as file:
        data = json.load(file)

    return data