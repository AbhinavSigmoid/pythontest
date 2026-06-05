import sys
import os
import json
import google.generativeai as genai

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
from ingestion.pdf_loader import load_pdf
from ingestion.chunker import create_chunks
from ingestion.embeddings import create_embeddings
from rag.vector_store import store_chunks


def extract_and_update_metadata(file_path, pdf_text):
    """
    Extracts structured schemas, lineage flows, health stats, and incidents from PDF text using Gemini
    and merges them into PDF-specific JSON configuration files in metadata/
    """
    from dotenv import load_dotenv
    load_dotenv(override=True)
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for key in st.secrets.keys():
                os.environ[key] = str(st.secrets[key])
    except Exception:
        pass
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY is not set. Skipping metadata extraction.")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
    Analyze the following text extracted from a Data Engineering pipeline document.
    Extract all database tables, lineage flows, pipeline health statistics, and any reported incidents mentioned in the document.

    You must output a single JSON object with the following structure:
    {{
      "tables": [
        {{
          "table_name": "string (snake_case)",
          "owner": "string",
          "contains_pii": boolean,
          "columns": ["string"]
        }}
      ],
      "lineage": {{
        "table_name_here": {{
          "flow": ["source_or_bronze_node", "silver_node", "gold_node"],
          "insights": "Description of the flow and transformations"
        }}
      }},
      "pipeline_health": {{
        "pipeline_name_here": {{
          "status": "Healthy" or "Degraded" or "Failed",
          "availability": "percentage string (e.g. 99.95%)",
          "last_run": "Success" or "Failed" or timestamp string,
          "sla": "Met" or "Breached"
        }}
      }},
      "recent_incident": {{
        "incident_id": "string (e.g. INC-YYYY-NNN)",
        "pipeline": "pipeline_name_here",
        "status": "Resolved" or "Active",
        "impact": "Detailed description of what was impacted and when"
      }}
    }}

    If any section (such as pipeline_health or lineage) is not mentioned or cannot be inferred from the document, return an empty list/object or null for that specific key. Do not generate placeholder details if they are not in the document.

    Document Text:
    {pdf_text}
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        extracted = json.loads(response.text.strip())
        print(f"Extracted metadata: {json.dumps(extracted, indent=2)}")
    except Exception as e:
        print(f"Error calling Gemini or parsing JSON: {e}")
        return

    # Update metadata files
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    metadata_dir = os.path.join(base_dir, "metadata")
    os.makedirs(metadata_dir, exist_ok=True)

    pdf_basename = os.path.basename(file_path)

    # 1. Update tables_{pdf_basename}.json
    tables_file = os.path.join(metadata_dir, "tables.json")
    if os.path.exists(tables_file):
        try:
            with open(tables_file, "r") as f:
                existing_tables = json.load(f)
        except Exception:
            existing_tables = []
    else:
        existing_tables = []

    new_tables = extracted.get("tables", [])
    if isinstance(new_tables, list):
        for nt in new_tables:
            if not isinstance(nt, dict) or "table_name" not in nt:
                continue
            # Check if table already exists
            found = False
            for i, et in enumerate(existing_tables):
                if et.get("table_name") == nt["table_name"]:
                    existing_tables[i] = nt
                    found = True
                    break
            if not found:
                existing_tables.append(nt)
        try:
            with open(tables_file, "w") as f:
                json.dump(existing_tables, f, indent=4)
            print(f"Successfully updated {tables_file}")
        except Exception as e:
            print(f"Error writing {tables_file}: {e}")

    # 2. Update lineage_{pdf_basename}.json
    lineage_file = os.path.join(metadata_dir, "lineage.json")
    if os.path.exists(lineage_file):
        try:
            with open(lineage_file, "r") as f:
                existing_lineage = json.load(f)
        except Exception:
            existing_lineage = {}
    else:
        existing_lineage = {}

    new_lineage = extracted.get("lineage", {})

    if isinstance(new_lineage, dict):

        for table_name, lineage_info in new_lineage.items():

            if isinstance(lineage_info, dict):

                existing_lineage[table_name] = (
                    lineage_info.get(
                        "flow",
                        []
                    )
                )

            else:

                existing_lineage[table_name] = (
                    lineage_info
            )
    if isinstance(new_lineage, dict):
        for k, v in new_lineage.items():
            existing_lineage[k] = v
        try:
            with open(lineage_file, "w") as f:
                json.dump(existing_lineage, f, indent=4)
            print(f"Successfully updated {lineage_file}")
        except Exception as e:
            print(f"Error writing {lineage_file}: {e}")

    # 3. Update pipeline_health_{pdf_basename}.json
    health_file = os.path.join(metadata_dir, "pipeline_health.json")
    if os.path.exists(health_file):
        try:
            with open(health_file, "r") as f:
                existing_health = json.load(f)
        except Exception:
            existing_health = {}
    else:
        existing_health = {}

    new_health = extracted.get("pipeline_health", {})
    if isinstance(new_health, dict):
        for k, v in new_health.items():
            existing_health[k] = v

    new_incident = extracted.get("recent_incident")
    if new_incident and isinstance(new_incident, dict):
        existing_health["recent_incident"] = new_incident

    if new_health or new_incident:
        try:
            with open(health_file, "w") as f:
                json.dump(existing_health, f, indent=4)
            print(f"Successfully updated {health_file}")
        except Exception as e:
            print(f"Error writing {health_file}: {e}")


def process_pdf(file_path):
    print("\nProcessing PDF...\n")

    text = load_pdf(file_path)

    document = {
        "file_name": file_path,
        "content": text
    }

    documents = [document]

    chunks = create_chunks(documents)

    print(
        f"Created {len(chunks)} chunks"
    )

    embeddings = create_embeddings(
        chunks
    )

    print(
        f"Created {len(embeddings)} embeddings"
    )

    store_chunks(
        chunks,
        embeddings
    )

    print(
        "\nStored in ChromaDB\n"
    )

    # Automatically extract structured metadata and update JSONs
    try:
        extract_and_update_metadata(file_path, text)
        print("\nMetadata synced from PDF successfully.\n")
    except Exception as e:
        print(f"\nFailed to sync metadata from PDF: {e}\n")