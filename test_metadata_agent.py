from agents.metadata_agent import (
    get_table_info,
    get_pii_tables
)

print()

print("PII Tables:")

print(
    get_pii_tables()
)

print()

print(
    get_table_info(
        "gold_customers"
    )
)