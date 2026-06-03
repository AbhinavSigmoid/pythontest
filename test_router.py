from agents.router import route_query


queries = [

    "Show lineage of gold_customers",

    "Which tables contain PII?",

    "Who owns gold_orders?",

    "What is the SLA of Orders Pipeline?"
]


for query in queries:

    print("\n" + "=" * 50)

    print("QUESTION:")

    print(query)

    print("\nANSWER:")

    print(
        route_query(query)
    )

    print()