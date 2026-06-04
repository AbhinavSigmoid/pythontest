# 🚀 GenAI Data Engineering Assistant

> *"What if every data engineer had an AI colleague who had read every runbook, every SLA document, every incident report — and could answer any question in seconds?"*

That's exactly what this project builds.

---

## 📋 Table of Contents

1. [The Business Problem](#-the-business-problem)
2. [The Solution — What This System Does](#-the-solution)
3. [The Aha Moment — How It Actually Works](#-the-aha-moment)
4. [Architecture](#-architecture)
5. [Tech Stack](#-tech-stack)
6. [Project Structure](#-project-structure)
7. [Core Concepts Explained](#-core-concepts-explained)
8. [Module-by-Module Breakdown](#-module-by-module-breakdown)
9. [Complete Data Flow](#-complete-data-flow)
10. [Setup & Installation](#-setup--installation)
11. [Running the Project](#-running-the-project)
12. [Knowledge Base — What It Knows](#-knowledge-base--what-it-knows)
13. [Example Conversations](#-example-conversations)
14. [Future Improvements](#-future-improvements)
15. [Key Design Decisions](#-key-design-decisions)

---

## 🔥 The Business Problem

### Imagine You're a Data Engineer at a Large Enterprise

You manage **2 critical pipelines**:
- **Orders Pipeline** — processes 2 million purchase transactions every hour from the Ecommerce platform into Snowflake
- **Customer Pipeline** — loads 500,000 customer records every 2 hours from Salesforce CRM into Snowflake

Every day your team faces questions like:

| Who Asks | What They Ask | Time to Answer (Today) |
|----------|---------------|----------------------|
| New engineer on-call | *"Which tables contain PII data?"* | 20 mins (finding the right doc) |
| Data analyst | *"What's the lineage of gold_customers?"* | 30 mins (asking on Slack, waiting) |
| Compliance officer | *"What's the SLA for orders pipeline?"* | 15 mins (digging through Confluence) |
| Engineering manager | *"What happened in incident INC-2026-001?"* | 10 mins (searching emails) |
| New team member | *"What data quality checks run on orders?"* | 45 mins (reading 5 documents) |

**Total lost time per week: Hours of productivity wasted searching static documents.**

### The Deeper Problem

Organizations have **vast institutional knowledge** trapped in:
- PDF runbooks nobody reads
- `.txt` documentation that gets outdated
- JSON metadata files only engineers know exist
- Incident reports buried in ticket systems
- SLA agreements in email threads

When a production issue strikes at **2:00 AM**, an on-call engineer needs answers in **seconds — not minutes**.

> **The core problem: Knowledge exists. Access to it, at the right moment, is broken.**

---

## 💡 The Solution

**GenAI Data Engineering Assistant** is an enterprise AI knowledge assistant that:

✅ Answers natural language questions about your pipelines, tables, and SLAs  
✅ Shows live pipeline health dashboards  
✅ Knows data lineage chains (Bronze → Silver → Gold)  
✅ Identifies PII-containing tables instantly  
✅ Direct PDF Upload from UI: Save files locally, sync to S3, and auto-index into ChromaDB in one click  
✅ In-App PDF Viewer: Preview and browse extracted content of any indexed PDF runbook directly in the UI  
✅ Auto-indexes new documents dropped into the uploads folder via real-time file watcher  
✅ Backs up every document to AWS S3 automatically  
✅ Cites its sources so you can trust the answer  

**Time to answer any question: Under 3 seconds.**

---

## 🤯 The Aha Moment

Here's the part that makes this project brilliant — the **hybrid intelligence** design:

```
"What is the lineage of gold_customers?"
         │
         ▼
   Router detects "lineage" keyword
         │
         ▼
   Lineage Agent reads lineage.json
         │
         ▼
   CRM → bronze_customers → silver_customers → gold_customers
         ← Instant. Deterministic. Always correct.

"How does the customer pipeline handle data quality?"
         │
         ▼
   Router: no keyword matched
         │
         ▼
   RAG Pipeline activates:
   Query → MiniLM Embedding → ChromaDB search → Top 3 matching doc chunks
         │
         ▼
   Gemini 2.5 Flash: reads chunks, generates answer
         │
         ▼
   "The customer pipeline performs null email validation,
    duplicate customer detection, and country code validation..."
    Sources: customer_pipeline.txt
         ← AI-powered. Context-aware. Source-cited.
```

**Two types of queries. Two perfectly matched handlers. Zero hallucination risk.**

Structured questions get **deterministic JSON lookups** (fast, always right).  
Unstructured questions get **RAG + Gemini** (smart, cited, context-grounded).

> This is the design insight that separates a toy from a production-grade system.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        LAYER 1: USER INTERFACE                      │
│                                                                     │
│   👤 User ──► 🖥️  Streamlit Web App                                 │
│                    ├── 💬 Chat Assistant Tab                        │
│                    └── 📊 Pipeline Health Tab                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │ User Question
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      LAYER 2: AGENT ROUTING                         │
│                                                                     │
│         🔀 Router Agent (agents/router.py)                          │
│                                                                     │
│   "lineage"  ──────────────────► 📍 Lineage Agent                  │
│   "pii"      ──────────────────► 🔐 Metadata Agent                 │
│   "owner"    ──────────────────► 🔐 Metadata Agent                 │
│   "schema"/"column" ───────────► 🔐 Metadata Agent                 │
│   (anything else)  ────────────► 🤖 RAG Chatbot                    │
└─────────────────────────────────────────────────────────────────────┘
         │                                      │
         ▼                                      ▼
┌────────────────────┐              ┌───────────────────────────────┐
│  LAYER 3: AGENTS   │              │     LAYER 4: RAG PIPELINE     │
│                    │              │                               │
│ 🏥 Health Agent    │              │  📄 Retriever                 │
│   pipeline_health  │              │  (MiniLM Embeddings)          │
│   .json            │              │        │                      │
│                    │              │        ▼                      │
│ 📍 Lineage Agent   │              │  🧠 ChromaDB Vector DB        │
│   lineage.json     │              │  (Semantic Search, Top 3)     │
│                    │              │        │                      │
│ 🔐 Metadata Agent  │              │        ▼                      │
│   tables.json      │              │  ✨ Gemini 2.5 Flash LLM      │
│                    │              │  (Answer Generation)          │
│ 📚 Catalog         │              │        │                      │
│   Explorer         │              │        ▼                      │
│   data_catalog     │              │  📝 Answer + Source Citations │
│   .json            │              └───────────────────────────────┘
└────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   LAYER 5: INGESTION & AUTOMATION                   │
│                                                                     │
│  📤 uploads/      👁️  File Watcher    ☁️  AWS S3                   │
│  (PDF dropped) ──► (watchdog) ──────► (boto3 upload)               │
│                        │                                           │
│                        ▼                                           │
│              ⚙️  Auto Indexer                                       │
│    PDF Loader → Chunker(300,50) → MiniLM → ChromaDB               │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      LAYER 6: DATA SOURCES                          │
│                                                                     │
│  📁 docs/              🗂️  metadata/          📤 uploads/           │
│  (TXT documents)       (JSON files)           (PDF drop zone)       │
│  • customer_pipeline   • pipeline_health.json                       │
│  • orders_pipeline     • lineage.json                               │
│  • sla_document        • tables.json                                │
│  • data_catalog        • data_catalog.json                          │
│  • incident_report                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Technology | Version | Role |
|-----------|---------|------|
| **Python** | 3.10+ | Core language |
| **Streamlit** | Latest | Web UI framework |
| **Google Gemini 2.5 Flash** | gemini-2.5-flash | LLM for answer generation |
| **ChromaDB** | Latest | Local persistent vector database |
| **SentenceTransformers** | Latest | Text embedding model |
| **all-MiniLM-L6-v2** | — | 384-dim embedding model (22MB, runs locally) |
| **pypdf** | Latest | PDF text extraction |
| **boto3** | Latest | AWS S3 SDK |
| **watchdog** | Latest | OS-level file system monitoring |
| **python-dotenv** | Latest | Environment variable management |
| **LangChain** | Latest | LLM application utilities |
| **pandas** | Latest | Data manipulation |

---

## 📁 Project Structure

```
pythontest/
│
├── 📂 app/
│   └── streamlit_app.py          # Main web application (entry point)
│
├── 📂 agents/
│   ├── router.py                 # Keyword-based query router
│   ├── health_agent.py           # Pipeline health status agent
│   ├── lineage_agent.py          # Data lineage lookup agent
│   ├── metadata_agent.py         # Table schema & PII agent
│   └── metadata_explorer.py      # Data catalog explorer agent
│
├── 📂 rag/
│   ├── chatbot.py                # Gemini LLM integration + answer generation
│   ├── retriever.py              # ChromaDB semantic search
│   └── vector_store.py           # ChromaDB write operations
│
├── 📂 ingestion/
│   ├── txt_loader.py             # Load .txt documents from folder
│   ├── pdf_loader.py             # Extract text from PDF files
│   ├── chunker.py                # Split text into overlapping chunks
│   └── embeddings.py             # Generate MiniLM vector embeddings
│
├── 📂 scripts/
│   ├── auto_indexer.py           # Full PDF → ChromaDB pipeline
│   ├── file_watcher.py           # Real-time folder monitoring
│   └── s3_uploader.py            # AWS S3 file upload utility
│
├── 📂 docs/                      # Knowledge base documents (indexed into ChromaDB)
│   ├── customer_pipeline.txt
│   ├── orders_pipeline.txt
│   ├── sla_document.txt
│   ├── data_catalog.txt
│   └── incident_report.txt
│
├── 📂 metadata/                  # Structured JSON data (read directly by agents)
│   ├── pipeline_health.json
│   ├── lineage.json
│   ├── tables.json
│   └── data_catalog.json
│
├── 📂 data/
│   └── chroma_db/                # Persisted ChromaDB vector database
│
├── 📂 uploads/                   # Drop PDFs here — auto-indexed!
│
├── requirements.txt
├── sample.pdf
└── README.md
```

---

## 🧠 Core Concepts Explained

Understanding these 5 concepts makes 100% of this code click.

---

### Concept 1 — RAG (Retrieval-Augmented Generation)

**The Problem:** Gemini doesn't know your company's pipelines, SLAs, or incidents. Its training data is general-purpose.

**The Solution:** Before asking the LLM, **retrieve your own documents** and paste them as context.

```
❌ Without RAG:
   User:  "What is the SLA for orders pipeline?"
   Gemini: "I don't have access to your company's SLA documents."

✅ With RAG:
   Step 1 → Search your docs → Found: "SLA: 99.95% successful execution. Max delay: 15 min"
   Step 2 → Prompt Gemini: "Using this context: [doc chunk]. Answer: What is the SLA?"
   Gemini: "The Orders Pipeline SLA is 99.95% availability with a maximum delay of 15 minutes."
```

**Files:** `rag/retriever.py` (Step 1) + `rag/chatbot.py` (Step 2)

---

### Concept 2 — Vector Embeddings

Text like `"pipeline failed"` and `"data ingestion error"` are completely different strings. But they mean almost the same thing.

**Embeddings** convert text into a list of numbers (a vector) where **similar meaning = close numbers**.

```python
"pipeline failed"      → [0.12, -0.45, 0.88, 0.03, ...]  # 384 numbers
"data ingestion error" → [0.10, -0.41, 0.85, 0.05, ...]  # 384 numbers
# These are mathematically CLOSE → semantically similar!

"I love pizza"         → [0.91,  0.72, -0.33, 0.60, ...]
# This is mathematically FAR → semantically unrelated!
```

**Model Used:** `all-MiniLM-L6-v2` — small (22MB), fast, and runs completely offline.

---

### Concept 3 — ChromaDB (Vector Database)

A regular database finds exact matches. ChromaDB finds **semantically similar** matches.

```sql
-- Regular SQL: exact match only
SELECT * FROM docs WHERE text = 'pipeline failed';   -- finds nothing if phrased differently

-- ChromaDB: semantic similarity
collection.query("pipeline issue")
-- Returns: "pipeline failed", "ingestion delay", "job timeout"  ← all related!
```

**Location:** `data/chroma_db/` (persisted to disk, survives restarts)

---

### Concept 4 — Text Chunking

A 10-page PDF cannot fit into one LLM context window. Even if it could, searching it would be imprecise. So we split it into **overlapping pieces**:

```
chunk_size = 300 characters
overlap    = 50 characters

Document:  "...The pipeline runs hourly. It processes 2M records per day.
            SLA target is 99.95%. Owner is the Commerce Analytics Team..."

Chunk 1:  "...The pipeline runs hourly. It processes 2M records per day. SLA..."
Chunk 2:  "...SLA target is 99.95%. Owner is the Commerce Analytics Team..."
            ↑
        50-char overlap ensures boundary content is never lost
```

**Why overlap?** If a sentence spans the boundary between two chunks, the overlap ensures it fully appears in at least one chunk.

---

### Concept 5 — The Medallion Architecture (Bronze → Silver → Gold)

This project tracks data lineage through the **industry-standard medallion architecture**:

```
Source System ──► Bronze Layer ──► Silver Layer ──► Gold Layer
   (Raw)           (As-is)         (Cleaned)        (Business-ready)

CRM (Salesforce) ──► bronze_customers ──► silver_customers ──► gold_customers
Ecommerce        ──► bronze_orders    ──► silver_orders    ──► gold_orders
```

| Layer | What It Contains |
|-------|-----------------|
| **Bronze** | Raw data exactly as received from source system |
| **Silver** | Cleaned, deduplicated, validated data |
| **Gold** | Aggregated, business-ready data for analytics |

---

## 📦 Module-by-Module Breakdown

### 🔵 `ingestion/txt_loader.py` — Document Reader

Scans a folder, reads every `.txt` file, returns structured list:

```python
load_documents("docs/")
# Returns:
[
  {"file_name": "orders_pipeline.txt",   "content": "Orders Pipeline Documentation..."},
  {"file_name": "customer_pipeline.txt", "content": "Customer Pipeline Documentation..."},
  {"file_name": "sla_document.txt",      "content": "Service Level Objectives..."},
  {"file_name": "incident_report.txt",   "content": "Incident Report INC-2026-001..."},
  {"file_name": "data_catalog.txt",      "content": "Enterprise Data Catalog..."}
]
```

---

### 🔵 `ingestion/pdf_loader.py` — PDF Text Extractor

Uses `pypdf` to extract raw text page by page:

```python
load_pdf("sample.pdf")
# Returns: full text string from all pages combined
```

---

### 🔵 `ingestion/chunker.py` — Text Splitter

```python
create_chunks(documents, chunk_size=300, overlap=50)
# Input:  list of document dicts
# Output: list of chunk dicts, each 300 chars with 50-char overlap
```

---

### 🔵 `ingestion/embeddings.py` — Vector Generator

```python
create_embeddings(chunks)
# Input:  list of chunk dicts
# Output: NumPy array of shape (num_chunks, 384)
#         → each chunk becomes a row of 384 float numbers
```

---

### 🟢 `rag/vector_store.py` — ChromaDB Writer

```python
store_chunks(chunks, embeddings)
# Stores each chunk with:
#   - ID:       "chunk_0", "chunk_1", ...
#   - Text:     the chunk content
#   - Embedding: [0.12, -0.45, 0.88, ...]
#   - Metadata: {"source": "orders_pipeline.txt"}
```

---

### 🟢 `rag/retriever.py` — Semantic Search Engine

```python
search_documents("What is the SLA for orders?")
# Step 1: Encode query → [0.09, -0.43, 0.81, ...]
# Step 2: ChromaDB finds 3 most similar stored chunks
# Step 3: Returns:
[
  {"content": "SLA: 99.95% successful execution...", "source": "orders_pipeline.txt"},
  {"content": "Maximum Delay: 15 minutes...",        "source": "sla_document.txt"},
  {"content": "Orders Pipeline runs every hour...",  "source": "orders_pipeline.txt"}
]
```

---

### 🟢 `rag/chatbot.py` — Gemini LLM Interface

```python
ask_question("What data quality checks run on orders?")

# 1. Retrieves top 3 relevant chunks from ChromaDB
# 2. Builds this prompt:
"""
You are a Data Engineering Assistant.
Answer the user's question only using the provided context.

Context:
[chunk 1 text]
[chunk 2 text]
[chunk 3 text]

Question:
What data quality checks run on orders?
"""
# 3. Sends to Gemini 2.5 Flash
# 4. Returns answer + "Sources: orders_pipeline.txt"
```

---

### 🟣 `agents/router.py` — Query Dispatcher

```python
route_query("What is the lineage of gold_orders?")
# → Detects "lineage" + "gold_orders"
# → Calls get_lineage("gold_orders")
# → Returns "Ecommerce -> bronze_orders -> silver_orders -> gold_orders"

route_query("Tell me about the pipeline schedule")
# → No keyword matched
# → Falls back to ask_question() → RAG pipeline
```

---

### 🟣 `agents/health_agent.py` — Health Dashboard

```python
get_pipeline_health()
# Reads metadata/pipeline_health.json
# Returns:
{
  "orders_pipeline":   {"status": "Healthy", "availability": "99.95%", "last_run": "Success", "sla": "Met"},
  "customer_pipeline": {"status": "Healthy", "availability": "99.90%", "last_run": "Success", "sla": "Met"},
  "recent_incident":   {"incident_id": "INC-2026-001", "pipeline": "Orders Pipeline",
                        "status": "Resolved", "impact": "45 minute delay"}
}
```

---

### 🟣 `agents/lineage_agent.py` — Lineage Tracer

```python
get_lineage("gold_customers")
# Reads metadata/lineage.json
# Returns: "CRM -> bronze_customers -> silver_customers -> gold_customers"
```

---

### 🟣 `agents/metadata_agent.py` — Schema & PII Inspector

```python
get_table_info("gold_customers")
# Returns full table dict: owner, PII flag, columns list

get_pii_tables()
# Returns: ["gold_customers"]   ← only tables where contains_pii = true
```

---

### 🔴 `scripts/auto_indexer.py` — Full Ingestion Orchestrator

```python
process_pdf("sample.pdf")
# Runs the complete pipeline:
# load_pdf() → create_chunks() → create_embeddings() → store_chunks()
# Prints progress at each step
```

---

### 🔴 `scripts/file_watcher.py` — Real-Time Automation

```python
# Watches the uploads/ folder continuously using OS file system events
# When a new file appears:
#   1. upload_file(path)  → backs up to AWS S3
#   2. process_pdf(path)  → indexes into ChromaDB
# Zero manual intervention needed
```

---

### 🔴 `scripts/s3_uploader.py` — Cloud Backup

```python
upload_file("uploads/runbook.pdf")
# Uses boto3 to upload to S3 bucket: "sigma-datatech-abhi"
# File is archived in the cloud permanently
```

---

## 🔄 Complete Data Flow

### Flow A — Structured Question (Instant JSON Lookup)

```
User types: "What is the lineage of gold_orders?"
    │
    ▼
streamlit_app.py receives query
    │
    ▼
agents/router.py: query_lower contains "lineage" AND "gold_orders"
    │
    ▼
agents/lineage_agent.py: opens metadata/lineage.json
    │
    ▼
Returns: ["Ecommerce", "bronze_orders", "silver_orders", "gold_orders"]
    │
    ▼
router.py joins: "Ecommerce -> bronze_orders -> silver_orders -> gold_orders"
    │
    ▼
Displayed in Streamlit chat ← Total time: ~50ms
```

### Flow B — Unstructured Question (RAG + Gemini)

```
User types: "How does the customer pipeline handle data quality?"
    │
    ▼
agents/router.py: no keyword matches → calls ask_question()
    │
    ▼
rag/chatbot.py → calls search_documents("How does customer pipeline handle data quality?")
    │
    ▼
rag/retriever.py:
    1. Encodes query → vector [0.09, -0.43, 0.81, ...]
    2. ChromaDB finds top 3 similar chunks:
       - "Null email validation, duplicate customer detection..." (source: customer_pipeline.txt)
       - "Country code validation..." (source: customer_pipeline.txt)
       - "SLA: 99.9% successful execution..." (source: sla_document.txt)
    │
    ▼
rag/chatbot.py:
    Builds prompt with 3 chunks as context
    Calls Gemini 2.5 Flash API
    │
    ▼
Gemini generates:
    "The customer pipeline performs three data quality checks:
     1. Null email validation
     2. Duplicate customer detection
     3. Country code validation
     Sources: customer_pipeline.txt, sla_document.txt"
    │
    ▼
Displayed in Streamlit chat ← Total time: ~2-3 seconds
```

### Flow C — New Document Ingestion (Fully Automated)

```
Engineer drops "new_runbook.pdf" into uploads/ folder
    │
    ▼
scripts/file_watcher.py: OS event fired instantly (watchdog)
    │
    ├──────────────────────────────────────────────────┐
    ▼                                                  ▼
scripts/s3_uploader.py                    scripts/auto_indexer.py
    │                                                  │
boto3.upload_file()                       1. pdf_loader.py → extract all text
    │                                     2. chunker.py → create 300-char chunks
Backed up to AWS S3                       3. embeddings.py → MiniLM vectors
"sigma-datatech-abhi"                     4. vector_store.py → store in ChromaDB
    │                                                  │
    └──────────────────────────────────────────────────┘
    ▼
Knowledge base updated — the new PDF is now searchable!
Next question about its content → Retriever finds it → Gemini answers from it
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.10 or higher
- Google Gemini API key ([get one here](https://aistudio.google.com/))
- AWS account with S3 bucket (for file upload feature)
- AWS credentials configured (`~/.aws/credentials` or environment variables)

### Step 1 — Clone / Navigate to Project

```bash
cd pythontest
```

### Step 2 — Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
# OR
venv\Scripts\activate           # Windows
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Set Up Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

> **Get your Gemini API key:** Visit [Google AI Studio](https://aistudio.google.com/) → Get API Key → Free tier available.

### Step 5 — Index the Knowledge Base

Before running the app, load all documents into ChromaDB:

```bash
python -c "
from ingestion.txt_loader import load_documents
from ingestion.chunker import create_chunks
from ingestion.embeddings import create_embeddings
from rag.vector_store import store_chunks

docs = load_documents('docs/')
chunks = create_chunks(docs)
embeddings = create_embeddings(chunks)
store_chunks(chunks, embeddings)
print('Knowledge base ready!')
"
```

---

## ▶️ Running the Project

### Start the Web App

```bash
# Can be run from the root directory:
streamlit run app/streamlit_app.py

# Or from inside the app/ subdirectory:
cd app
streamlit run streamlit_app.py
```

> **Note on Running Directory**: The project contains dynamic absolute path resolution routines using `BASE_DIR`. Therefore, all file loaders and databases will resolve correctly regardless of whether the app is run from the root folder or the `app/` folder.

Open your browser at: **http://localhost:8501**

---

### Start the File Watcher (Optional — for auto-indexing)

In a separate terminal:

```bash
cd scripts
python file_watcher.py
```

Now drop any PDF into the `uploads/` folder — it will be automatically:
1. Uploaded to AWS S3
2. Indexed into ChromaDB
3. Instantly searchable from the chat

---

### Run Tests

```bash
# Test individual modules
python test_chunker.py
python test_embeddings.py
python test_retriever.py
python test_chatbot.py
python test_router.py
python test_health_agent.py
python test_lineage_agent.py
python test_metadata_agent.py

# Test full pipeline
python test_auto_indexer.py
python test_pdf_rag.py
```

---

## 📚 Knowledge Base — What It Knows

### Documents Indexed in ChromaDB (`docs/`)

| Document | Content | Key Information |
|----------|---------|----------------|
| `customer_pipeline.txt` | Customer pipeline runbook | Source: Salesforce CRM, Destination: Snowflake, Schedule: every 2h, PII fields: email, phone |
| `orders_pipeline.txt` | Orders pipeline runbook | Source: Ecommerce, Destination: Snowflake, Schedule: every 1h, Volume: 2M records/day |
| `sla_document.txt` | Service Level Objectives | Customer: 99.9% / 30min max, Orders: 99.95% / 15min max, Escalation rules |
| `data_catalog.txt` | Enterprise data catalog | All tables, owners, columns, lineage chains |
| `incident_report.txt` | Incident INC-2026-001 | Orders pipeline, DB connection timeout, 45min delay, Resolved |

### Structured Metadata (`metadata/`)

| File | Contents |
|------|---------|
| `pipeline_health.json` | Live health: status, availability %, last run result, SLA compliance |
| `lineage.json` | Bronze→Silver→Gold chains for gold_customers and gold_orders |
| `tables.json` | Schema registry: table name, owner, PII flag, column list |
| `data_catalog.json` | Same catalog in dictionary format (keyed by table name) |

---

## 💬 Example Conversations

```
You: What is the lineage of gold_customers?
Bot: CRM -> bronze_customers -> silver_customers -> gold_customers

You: Which tables contain PII data?
Bot: Tables containing PII:
     gold_customers

You: Who owns the gold_orders table?
Bot: Owner of gold_orders: Commerce Analytics Team

You: What columns does gold_customers have?
Bot: Columns in gold_customers:
     customer_id, first_name, last_name, email, phone_number, city, country

You: What happened in the recent incident?
Bot: The incident INC-2026-001 affected the Orders Pipeline on 15 May 2026.
     Root cause was a database connection timeout, causing a 45-minute processing delay.
     Resolution: Database connection pool was increased. Status: Resolved.
     Sources: incident_report.txt

You: What is the SLA for the orders pipeline?
Bot: The Orders Pipeline SLA target is 99.95% availability with a maximum delay of 15 minutes.
     Severity 1 incidents require immediate escalation.
     Sources: sla_document.txt, orders_pipeline.txt

You: How does the customer pipeline validate data quality?
Bot: The customer pipeline performs three data quality checks:
     1. Null email validation — ensures no records have missing email addresses
     2. Duplicate customer detection — prevents duplicate records from being loaded
     3. Country code validation — ensures country field follows standard codes
     Sources: customer_pipeline.txt
```

---

## 🚀 Future Improvements

This is a production-grade foundation. Here's what could make it even more powerful:

### 🔮 Short-Term (Next Sprint)

| Improvement | Why It Matters |
|-------------|---------------|
| **Add more pipeline docs** | Expand knowledge base to cover all pipelines in the org |
| **Dynamic routing** | Use an LLM to decide which agent to call instead of keyword matching — handles edge cases better |
| **Streaming responses** | Show Gemini's answer word-by-word (like ChatGPT) using `st.write_stream()` |
| **Feedback buttons** | 👍/👎 on each answer — collect data for fine-tuning |
| **Query history persistence** | Save chat history to SQLite/PostgreSQL across sessions |

### 🔮 Medium-Term (Next Quarter)

| Improvement | Why It Matters |
|-------------|---------------|
| **Real-time pipeline health** | Connect to Airflow/dbt APIs instead of static JSON — live status |
| **Multi-modal support** | Accept screenshots of dashboards, error logs images — use vision models |
| **Slack/Teams bot integration** | Answer questions directly in team chat — zero context switching |
| **Fine-tuned embedding model** | Train `all-MiniLM` on your domain vocabulary — better search precision |
| **Re-ranking** | After retrieving top-10 chunks, use a cross-encoder to re-rank for top-3 precision |
| **Metadata filtering** | Pre-filter ChromaDB by pipeline name before semantic search — faster, more precise |

### 🔮 Long-Term (Strategic Vision)

| Improvement | Why It Matters |
|-------------|---------------|
| **Agentic pipelines (LangGraph)** | Multi-step reasoning: "Find all PII tables owned by Data Engineering Team with failed SLAs last week" |
| **Automated incident response** | Detect anomalies → auto-query knowledge base → suggest remediation steps → page on-call |
| **Data quality monitoring integration** | Connect to Great Expectations / dbt tests — answer "Are data quality checks passing?" with real data |
| **Knowledge graph** | Instead of flat vector search, build a graph of tables → pipelines → owners → incidents → SLAs |
| **Multi-tenant support** | Different teams see different subsets of the knowledge base |
| **Auto-documentation generation** | When a new pipeline is created in Airflow, automatically generate its documentation |
| **Proactive alerts** | "SLA breach predicted in 2 hours based on current processing rate" — push to engineers |

### 🔮 Architecture Evolution

```
Current Architecture:
  User → Router → Agent/RAG → Gemini → Answer

Future Architecture (Agentic):
  User → Planner LLM → [Sub-Agent 1: Data Retriever]
                      → [Sub-Agent 2: Metric Calculator]
                      → [Sub-Agent 3: Incident Analyzer]
                      → [Synthesizer LLM] → Comprehensive Answer
```

---

## 🎯 Key Design Decisions

### Why keyword routing instead of LLM-based routing?
**Speed and reliability.** Asking Gemini "which agent should handle this?" adds 2+ seconds of latency and can fail. Keyword matching is deterministic, sub-millisecond, and works 100% of the time for structured queries.

### Why absolute paths over relative paths in file loaders?
**Execution robustness.** Constructing paths dynamically with `BASE_DIR` (e.g. `os.path.join(BASE_DIR, "metadata", "tables.json")`) ensures that file reading, writing, and SQLite/ChromaDB indexing resolve correctly, regardless of the folder path from which the user runs the `streamlit run` command.

### Why theme-mismatch overrides in CSS?
**Visual consistency.** In Streamlit, custom toggle themes are implemented inside Python state variables. However, standard Streamlit widgets (like `st.expander` or default `st.plotly_chart` themes) match the native server-side or client OS themes (which may remain Dark). To avoid issues like white-on-white text in Light Mode, we declare custom CSS rules with `!important` to force styling elements like expander headers, text boxes, and Plotly labels to contrast correctly under both toggled themes.

### Why overlap=50 in chunking?
If you split text at exactly 300 characters, important sentences may be cut in half at a boundary. 50-character overlap ensures that boundary content fully appears in at least one chunk, preserving complete thoughts.

### Why store `file_name` as metadata in ChromaDB?
**Trust and auditability.** Every AI answer in an enterprise setting needs to be traceable. When Gemini says "the SLA is 99.95%", engineers need to know *which document* said that. Source citations build trust in the system.

### Why Gemini 2.5 Flash over GPT-4 or Claude?
**Cost-efficiency and speed.** Flash is optimized for fast, high-quality responses at a fraction of the cost of premium models. For a knowledge retrieval use case, Flash is more than capable. The "intelligence" comes from the retrieved context — not from the LLM's own knowledge.

### Why local ChromaDB over Pinecone/Weaviate?
**Zero infrastructure overhead for a capstone project.** ChromaDB persists to a local folder (`data/chroma_db/`) with no account setup, no API keys, no billing. For production, replace with Pinecone/Weaviate for scale.

### Why `all-MiniLM-L6-v2` over OpenAI embeddings?
**Offline capability and zero cost.** MiniLM runs entirely locally, no API calls needed, handles millions of embeddings for free. OpenAI embeddings cost per token and require internet. For this use case, MiniLM quality is excellent.

---

## 👨‍💻 Author

Built as a **GenAI Capstone Project** demonstrating the integration of:
- **Retrieval-Augmented Generation (RAG)** for enterprise knowledge bases
- **Multi-agent systems** for intelligent query routing
- **Event-driven automation** for zero-touch document ingestion
- **Cloud integration** with AWS S3 for document archival

---

## 📄 License

This project is built for educational and demonstration purposes.

---

*Built with ❤️ using Gemini • ChromaDB • AWS S3 • Streamlit • Python*
