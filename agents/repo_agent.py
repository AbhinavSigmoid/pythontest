import os
import sys
import shutil
import subprocess
import json
import chromadb
from dotenv import load_dotenv
import google.generativeai as genai

# Ensure root directory is in python path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from ingestion.chunker import create_chunks
from ingestion.embeddings import create_embeddings

CLONED_REPO_DIR = os.path.join(BASE_DIR, "data", "cloned_repo")
METADATA_DIR = os.path.join(BASE_DIR, "metadata")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

def backup_default_metadata():
    """Backup the original metadata files if they haven't been backed up already."""
    for filename in ["tables.json", "lineage.json", "pipeline_health.json"]:
        source = os.path.join(METADATA_DIR, filename)
        backup = os.path.join(METADATA_DIR, filename.replace(".json", "_default.json"))
        if os.path.exists(source) and not os.path.exists(backup):
            shutil.copy2(source, backup)

def restore_default_metadata():
    """Restore the default metadata files and re-index the default docs folder."""
    # Restore metadata
    for filename in ["tables.json", "lineage.json", "pipeline_health.json"]:
        backup = os.path.join(METADATA_DIR, filename.replace(".json", "_default.json"))
        source = os.path.join(METADATA_DIR, filename)
        if os.path.exists(backup):
            shutil.copy2(backup, source)

    # Clean up Mermaid diagram
    arch_file = os.path.join(METADATA_DIR, "architecture_mermaid.txt")
    if os.path.exists(arch_file):
        try:
            os.remove(arch_file)
        except Exception:
            pass

    # Clean up cloned repository
    if os.path.exists(CLONED_REPO_DIR):
        shutil.rmtree(CLONED_REPO_DIR, ignore_errors=True)

    # Re-index original docs folder into ChromaDB
    reindex_default_docs()

def reindex_default_docs():
    """Index the original docs folder back into ChromaDB."""
    documents = []
    if os.path.exists(DOCS_DIR):
        for file_name in os.listdir(DOCS_DIR):
            if file_name.endswith(".txt"):
                file_path = os.path.join(DOCS_DIR, file_name)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                        content = file.read()
                        documents.append({
                            "file_name": file_name,
                            "content": content
                        })
                except Exception as e:
                    print(f"Error reading default doc {file_name}: {e}")

    if documents:
        chunks = create_chunks(documents)
        if chunks:
            embeddings = create_embeddings(chunks)
            client = chromadb.PersistentClient(path=os.path.join(BASE_DIR, "data", "chroma_db"))
            try:
                client.delete_collection(name="de_documents")
            except Exception:
                pass
            collection = client.get_or_create_collection(name="de_documents")
            
            ids = [f"chunk_{i}" for i in range(len(chunks))]
            docs_list = [c["chunk"] for c in chunks]
            metadatas = [{"source": c["file_name"]} for c in chunks]
            
            collection.add(
                ids=ids,
                documents=docs_list,
                embeddings=embeddings.tolist(),
                metadatas=metadatas
            )
            print("Default docs re-indexed successfully.")

def ingest_github_repo(repo_url):
    """Clone, index, and analyze a GitHub repository."""
    # 1. Backup default metadata
    backup_default_metadata()

    # 2. Clean and clone repo
    if os.path.exists(CLONED_REPO_DIR):
        shutil.rmtree(CLONED_REPO_DIR, ignore_errors=True)
    
    os.makedirs(CLONED_REPO_DIR, exist_ok=True)
    
    try:
        # Clone repo
        subprocess.run(["git", "clone", repo_url, CLONED_REPO_DIR], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Failed to clone repository: {e.stderr.decode().strip() if e.stderr else str(e)}")

    # 3. Read files for indexing and metadata extraction
    documents = []
    sql_files = []
    py_files = []
    other_files = []

    for root, dirs, files in os.walk(CLONED_REPO_DIR):
        if ".git" in root or "__pycache__" in root or ".venv" in root or "node_modules" in root:
            continue
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in ['.py', '.sql', '.md', '.txt', '.json', '.yml', '.yaml']:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, CLONED_REPO_DIR)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        doc_item = {"file_name": rel_path, "content": content}
                        documents.append(doc_item)
                        
                        if ext == '.sql':
                            sql_files.append(doc_item)
                        elif ext == '.py':
                            py_files.append(doc_item)
                        else:
                            other_files.append(doc_item)
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")

    if not documents:
        raise Exception("No indexable code or documents found in the repository.")

    # 4. RAG indexing to ChromaDB
    chunks = create_chunks(documents)
    if chunks:
        embeddings = create_embeddings(chunks)
        client = chromadb.PersistentClient(path=os.path.join(BASE_DIR, "data", "chroma_db"))
        try:
            client.delete_collection(name="de_documents")
        except Exception:
            pass
        collection = client.get_or_create_collection(name="de_documents")
        
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        docs_list = [c["chunk"] for c in chunks]
        metadatas = [{"source": c["file_name"]} for c in chunks]
        
        collection.add(
            ids=ids,
            documents=docs_list,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

    # 5. Metadata extraction using Gemini AI
    analysis_success = False
    load_dotenv(override=True)
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            for key in st.secrets.keys():
                os.environ[key] = str(st.secrets[key])
    except Exception:
        pass
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            # Build file summaries
            file_summaries = []
            # Prioritize SQL, schema config and python models
            prioritized = sql_files + py_files + [f for f in other_files if f["file_name"].endswith(('.json', '.yml', '.yaml'))]
            # Take top 30 files to avoid context exhaustion
            for item in prioritized[:30]:
                content_preview = item["content"]
                if len(content_preview) > 3000:
                    content_preview = content_preview[:3000] + "\n... [TRUNCATED] ..."
                file_summaries.append(f"File: {item['file_name']}\nContent:\n{content_preview}\n")
            
            summary_str = "\n======================\n".join(file_summaries)
            
            prompt = f"""
You are an expert Data Engineering Agent. Your task is to analyze the source code and configurations of a data engineering repository and output metadata to populate our dashboard.

Based on the files provided below, analyze:
1. **Pipeline Health**: Identify active data pipelines or sync scripts. Estimate their uptime availability, last run status (Success/Failed), SLA status (Met/Missed), and detail a potential mock/recent incident related to them.
2. **Data Catalog**: List key tables or data collections generated/used in the repo. For each table, determine its owner (team name), columns, and check if it contains any personally identifiable information (PII).
3. **Data Lineage**: Map out transformation paths showing how tables flow from raw/bronze ingestion layers to intermediate/silver or serving/gold layers. Do NOT include code files, scripts, or path names (e.g. 'clean.py', 'load_data.sql') in the flows. Instead, identify logical database tables, staging steps, or datasets (e.g. 'Raw_API', 'bronze_transactions', 'silver_transactions', 'gold_transactions') that represent the flow of data.
4. **Architecture Diagram**: Create a valid Mermaid.js flowchart (starting with graph TD) representing the end-to-end data flow and system architecture of this repository (connecting ingestion scripts, files/sources, intermediate storage/processing, and final tables).

Analyze the repository files:
{summary_str}

Please generate a single JSON object containing exactly four root keys: "pipeline_health", "tables", "lineage", and "architecture_mermaid".
The schema of the JSON object MUST match the following format exactly:

{{
  "pipeline_health": {{
    "pipeline_id_1": {{
      "status": "Healthy" | "Degraded" | "Failed",
      "availability": "99.95%",
      "last_run": "Success" | "Failed",
      "sla": "Met" | "Missed"
    }},
    "recent_incident": {{
      "incident_id": "INC-2026-001",
      "pipeline": "Pipeline Name",
      "status": "Resolved" | "Investigating" | "Active",
      "impact": "Incident details description"
    }}
  }},
  "tables": [
    {{
      "table_name": "name_of_table",
      "owner": "Responsible Team",
      "contains_pii": true | false,
      "columns": ["column1", "column2"]
    }}
  ],
  "lineage": {{
    "table_name": {{
      "flow": ["SourceSystem", "bronze_table", "silver_table", "table_name"],
      "insights": "Detailed explanation of what transformations occur, what fields are added or filtered, and the general purpose of this pipeline."
    }}
  }},
  "architecture_mermaid": "graph TD\\n  A[Source System] --> B[Ingestion Pipeline]\\n  B --> C(Database Table)"
}}

Make sure you do not output any markdown formatting, backticks, or explanation. Output ONLY the raw JSON string.
"""
            response = model.generate_content(prompt)
            json_text = response.text.strip()
            
            # Clean response if LLM added markdown backticks
            if json_text.startswith("```"):
                lines = json_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                json_text = "\n".join(lines).strip()
            
            extracted_metadata = json.loads(json_text)
            
            # Validate root keys
            if "pipeline_health" in extracted_metadata and "tables" in extracted_metadata and "lineage" in extracted_metadata:
                # Save metadata
                with open(os.path.join(METADATA_DIR, "pipeline_health.json"), "w") as f:
                    json.dump(extracted_metadata["pipeline_health"], f, indent=4)
                with open(os.path.join(METADATA_DIR, "tables.json"), "w") as f:
                    json.dump(extracted_metadata["tables"], f, indent=4)
                with open(os.path.join(METADATA_DIR, "lineage.json"), "w") as f:
                    json.dump(extracted_metadata["lineage"], f, indent=4)
                
                # Save Mermaid diagram
                mermaid_code = extracted_metadata.get("architecture_mermaid", "")
                if mermaid_code:
                    with open(os.path.join(METADATA_DIR, "architecture_mermaid.txt"), "w") as f:
                        f.write(mermaid_code)
                
                analysis_success = True
                print("Gemini analysis completed and written successfully.")
        except Exception as ex:
            print(f"Failed to extract metadata using Gemini AI: {ex}. Proceeding to fallback analyzer.")

    # 6. Fallback Rule-Based Analyzer if Gemini failed or is not configured
    if not analysis_success:
        generate_fallback_metadata(repo_url, documents)

def generate_fallback_metadata(repo_url, documents):
    """Fallback metadata generator that parses file lists to mock appropriate pipelines, tables, lineages, and architecture."""
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    
    # 1. Identify tables based on SQL file names or references
    tables = []
    lineage = {}
    pipelines = {}
    
    # Detect tables
    for doc in documents:
        file_name = doc["file_name"]
        if file_name.endswith(".sql"):
            table_name = os.path.basename(file_name).replace(".sql", "")
            # Clean up names
            if table_name:
                tables.append({
                    "table_name": table_name,
                    "owner": "Ingested Dev Team",
                    "contains_pii": "customer" in table_name or "user" in table_name or "pii" in table_name,
                    "columns": ["id", "created_at", "updated_at", "status"]
                })
                lineage[table_name] = {
                    "flow": ["Source_DB", f"bronze_{table_name}", f"silver_{table_name}", table_name],
                    "insights": f"Transforms raw database records from Source_DB through bronze ingestion and silver sanitization layers, producing the final clean `{table_name}` table."
                }
    
    # Defaults if no tables found
    if not tables:
        tables = [
            {
                "table_name": "custom_users",
                "owner": "Core Data Team",
                "contains_pii": True,
                "columns": ["user_id", "email_address", "signup_date", "country"]
            },
            {
                "table_name": "custom_transactions",
                "owner": "Finance Team",
                "contains_pii": False,
                "columns": ["transaction_id", "user_id", "amount", "currency", "timestamp"]
            }
        ]
        lineage = {
            "custom_users": {
                "flow": ["Production_DB", "users_bronze", "custom_users"],
                "insights": "Extracts raw user records from Production_DB, applies PII hashing, and structures user details in the final `custom_users` dataset."
            },
            "custom_transactions": {
                "flow": ["Stripe_API", "transactions_bronze", "transactions_silver", "custom_transactions"],
                "insights": "Ingests payment events from Stripe_API, aggregates them in the staging layers, and loads financial summaries into `custom_transactions`."
            }
        }

    # Detect pipelines
    for doc in documents:
        file_name = doc["file_name"]
        if "dag" in file_name.lower() or "pipeline" in file_name.lower() or file_name.endswith(".py"):
            p_name = os.path.basename(file_name).replace(".py", "")
            if len(pipelines) < 3 and p_name:
                pipelines[f"{p_name}_pipeline"] = {
                    "status": "Healthy",
                    "availability": "99.92%",
                    "last_run": "Success",
                    "sla": "Met"
                }
                
    if not pipelines:
        pipelines = {
            "cloned_repo_pipeline": {
                "status": "Healthy",
                "availability": "99.98%",
                "last_run": "Success",
                "sla": "Met"
            }
        }
        
    pipelines["recent_incident"] = {
        "incident_id": "INC-CLONE-001",
        "pipeline": list(pipelines.keys())[0].replace("_", " ").title(),
        "status": "Resolved",
        "impact": "Minor metadata ingestion sync lag"
    }

    # Generate fallback Mermaid diagram
    mermaid_code = "graph TD\n"
    mermaid_code += f"  subgraph {repo_name} Repository System\n"
    # Pipelines
    for p_key in pipelines:
        if p_key != "recent_incident":
            p_title = p_key.replace("_", " ").title()
            mermaid_code += f"    {p_key}[{p_title} Ingestion] -->|Processes & Syncs| IngestionLayer[Ingestion Processing Layer]\n"
    # Tables
    for t in tables:
        t_name = t["table_name"]
        mermaid_code += f"    IngestionLayer --> {t_name}_db[({t_name} Table)]\n"
    mermaid_code += "  end\n"

    # Save to files
    with open(os.path.join(METADATA_DIR, "pipeline_health.json"), "w") as f:
        json.dump(pipelines, f, indent=4)
    with open(os.path.join(METADATA_DIR, "tables.json"), "w") as f:
        json.dump(tables, f, indent=4)
    with open(os.path.join(METADATA_DIR, "lineage.json"), "w") as f:
        json.dump(lineage, f, indent=4)
    with open(os.path.join(METADATA_DIR, "architecture_mermaid.txt"), "w") as f:
        f.write(mermaid_code)

    print("Fallback metadata generated successfully.")
