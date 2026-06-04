import json


def update_metadata():

    # Data Catalog

    with open(
        "metadata/tables.json",
        "r"
    ) as file:

        tables = json.load(file)

    payments_table = {
        "table_name": "gold_payments",
        "owner": "Payments Engineering Team",
        "contains_pii": False,
        "columns": [
            "payment_id",
            "customer_id",
            "amount"
        ]
    }

    if not any(
        t["table_name"] == "gold_payments"
        for t in tables
    ):
        tables.append(
            payments_table
        )

    with open(
        "metadata/tables.json",
        "w"
    ) as file:

        json.dump(
            tables,
            file,
            indent=4
        )

    # Lineage

    with open(
        "metadata/lineage.json",
        "r"
    ) as file:

        lineage = json.load(file)

    lineage["gold_payments"] = [
        "bronze_payments",
        "silver_payments",
        "gold_payments"
    ]

    with open(
        "metadata/lineage.json",
        "w"
    ) as file:

        json.dump(
            lineage,
            file,
            indent=4
        )

    # Pipeline Health

    with open(
        "metadata/pipeline_health.json",
        "r"
    ) as file:

        health = json.load(file)

    health["payments_pipeline"] = {
        "availability": "99.98%",
        "last_run": "Successful",
        "sla": "10 Minutes"
    }

    with open(
        "metadata/pipeline_health.json",
        "w"
    ) as file:

        json.dump(
            health,
            file,
            indent=4
        )