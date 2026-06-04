from agents.lineage_agent import get_lineage

from agents.metadata_agent import (
    get_pii_tables,
    get_table_info
)

from rag.chatbot import ask_question


def route_query(query):

    query_lower = query.lower()

    # Load table names dynamically from metadata/tables.json
    try:
        import json
        with open("metadata/tables.json", "r") as file:
            tables_data = json.load(file)
            table_names = [t["table_name"] for t in tables_data]
    except Exception:
        table_names = []

    # =====================
    # LINEAGE AGENT
    # =====================

    if "lineage" in query_lower:
        for t_name in table_names:
            if t_name.lower() in query_lower:
                return get_lineage(t_name)

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

    if "owner" in query_lower or "owns" in query_lower:
        for t_name in table_names:
            if t_name.lower() in query_lower:
                table = get_table_info(t_name)
                if table:
                    return f"Owner of {t_name}: {table['owner']}"

    # =====================
    # SCHEMA / COLUMNS
    # =====================

    if (
        "schema" in query_lower
        or "column" in query_lower
        or "columns" in query_lower
    ):
        for t_name in table_names:
            if t_name.lower() in query_lower:
                table = get_table_info(t_name)
                if table:
                    return (
                        f"Columns in {t_name}:\n\n"
                        + "\n".join(table["columns"])
                    )

    # =====================
    # RAG FALLBACK
    # =====================

    return ask_question(query)