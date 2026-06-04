import json
import os
from pathlib import Path


def get_pipeline_health(active_pdf=None):

    BASE_DIR = Path(__file__).resolve().parent.parent

    if active_pdf:
        pdf_basename = os.path.basename(active_pdf)
        custom_file = BASE_DIR / "metadata" / f"pipeline_health_{pdf_basename}.json"
        if custom_file.exists():
            try:
                with open(custom_file, "r") as file:
                    return json.load(file)
            except Exception:
                pass

    try:
        with open(BASE_DIR / "metadata" / "pipeline_health.json", "r") as file:
            data = json.load(file)
    except Exception:
        data = {}

    return data