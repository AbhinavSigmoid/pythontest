from agents.lineage_agent import get_lineage

from agents.metadata_agent import (
    get_pii_tables,
    get_table_info
)

from rag.chatbot import ask_question


def route_query(query):

    query_lower = query.lower()

    # =====================
    # LINEAGE AGENT
    # =====================

    if "lineage" in query_lower:

        if "gold_customers" in query_lower:

            return get_lineage(
                "gold_customers"
            )

        if "gold_orders" in query_lower:

            return get_lineage(
                "gold_orders"
            )

    # =====================
    # PII AGENT
    # =====================

    if "pii" in query_lower:

        tables = get_pii_tables()

        return (
            "Tables containing PII:\n\n"
            + "\n".join(tables)
        )

    # =====================
    # OWNER LOOKUP
    # =====================

    if "owner" in query_lower:

        if "gold_customers" in query_lower:

            table = get_table_info(
                "gold_customers"
            )

            return (
                f"Owner of gold_customers: "
                f"{table['owner']}"
            )

        if "gold_orders" in query_lower:

            table = get_table_info(
                "gold_orders"
            )

            return (
                f"Owner of gold_orders: "
                f"{table['owner']}"
            )

    # =====================
    # SCHEMA / COLUMNS
    # =====================

    if (
        "schema" in query_lower
        or "column" in query_lower
        or "columns" in query_lower
    ):

        if "gold_customers" in query_lower:

            table = get_table_info(
                "gold_customers"
            )

            return (
                "Columns in gold_customers:\n\n"
                + "\n".join(
                    table["columns"]
                )
            )

        if "gold_orders" in query_lower:

            table = get_table_info(
                "gold_orders"
            )

            return (
                "Columns in gold_orders:\n\n"
                + "\n".join(
                    table["columns"]
                )
            )

    # =====================
    # RAG FALLBACK
    # =====================

    return ask_question(query)