# Technical Specification & Presentation Prep: GenAI Data Engineering Assistant

This document details the system architecture, core technology stack, data ingestion pipelines, metadata schemas, and potential presentation Q&As for the **GenAI Data Engineering Assistant** project.

---

## 1. System Architecture

The application consists of two main loops: **Data Ingestion (S3 & RAG Sync)** and **Query Execution (Agentic Router)**.

```mermaid
graph TD
    %% Ingestion Loop
    subgraph Ingestion Loop (Watchdog & RAG Sync)
        A[Local uploads/ Folder] -->|New File Event| B[Watchdog File Watcher]
        B -->|boto3 upload| C[AWS S3 Bucket: sigma-datatech-abhi]
        B -->|load_pdf| D[pypdf Parser]
        D -->|create_chunks| E[LangChain Chunker]
        E -->|create_embeddings| F[SentenceTransformer: all-MiniLM-L6-v2]
        F -->|store_chunks| G[Local ChromaDB: data/chroma_db]
    end

    %% Query Execution Loop
    subgraph Query Execution (Agentic Router)
        H[User Query] -->|Streamlit Chat UI| I[Agentic Router]
        I -->|lineage keyword| J[Lineage Agent: lineage.json]
        I -->|pii keyword| K[PII Agent: tables.json]
        I -->|owner/schema keywords| L[Metadata Agent: tables.json]
        I -->|General/Semantic Query| M[RAG Assistant]
        M -->|Vector Search| G
        G -->|Context Extraction| N[Gemini 2.5 Flash LLM]
        N -->|Generate Answer| O[Final Output response]
        J --> O
        K --> O
        L --> O
    end
```

---

## 2. Core Technology Stack

| Component | Technology / Library | Role & Functionality |
| :--- | :--- | :--- |
| **Frontend UI** | `streamlit` | Premium conversational chat interface with dynamic Light/Dark theme modes, data catalog explorers, system health monitors, and lineage visualizations. |
| **Ingestion Watcher** | `watchdog` | Asynchronously monitors the `uploads/` folder for newly added documentation/PDFs. |
| **Cloud Storage** | `boto3` (AWS S3) | Automatically uploads new files to the S3 Bucket `sigma-datatech-abhi` to ensure durable backups. |
| **Document Parser** | `pypdf` | Extracts text from PDF files inside the `uploads/` folder. |
| **Embeddings Generator** | `sentence-transformers` | Converts parsed text chunks into 384-dimensional vector embeddings using the local **`all-MiniLM-L6-v2`** model. |
| **Vector Database** | `chromadb` | A persistent local vector store located at `data/chroma_db` that stores text chunks and embeddings for semantic RAG search. |
| **Generative AI LLM** | `google-generativeai` | Utilizes **`gemini-2.5-flash`** to synthesize answers to general queries based exclusively on the retrieved vector document context. |
| **Agentic Router** | Python Custom Logic | Redirects analytical metadata queries to specialized local metadata/lineage agents, falling back to the semantic RAG model. |

---

## 3. Data Schemas & Metadata

The assistant uses local JSON files under the `metadata/` directory to store structured data pipeline assets:

### 3.1. Data Catalog Metadata (`metadata/tables.json`)
Stores information about cataloged database tables, ownership, columns, and PII status.
```json
[
    {
        "table_name": "users_data",
        "owner": "data_engineering_team",
        "contains_pii": true,
        "columns": ["user_id", "first_name", "last_name", "email", "phone", "created_at"]
    }
]
```

### 3.2. Data Lineage Metadata (`metadata/lineage.json`)
Maps upstream tables, transformation paths, and AI-generated insights.
```json
{
    "monthly_revenue": {
        "flow": ["Silver_Fact_Sales", "Gold_Monthly_Revenue"],
        "insights": "This table provides an executive-level summary of monthly sales performance. It aggregates the fact_sales table by month..."
    }
}
```

### 3.3. Pipeline Health Metadata (`metadata/pipeline_health.json`)
Tracks availability percentages, last runs, SLA statuses, and incident logs.
```json
{
    "monthly_executive_etl": {
        "status": "Healthy",
        "availability": "99.95%",
        "last_run": "Success",
        "sla": "Met"
    }
}
```

---

## 4. Presentation Q&A Prep (Trainer Cheat Sheet)

These are the most common technical questions a trainer or evaluator is likely to ask during your capstone presentation, along with their structured answers:

### Q1: What is RAG, and how is it implemented in this architecture?
* **Answer**: RAG stands for **Retrieval-Augmented Generation**. Instead of relying solely on the pre-trained knowledge of the LLM, we retrieve relevant context from our local document vector store (`ChromaDB`) and pass it along with the user's query to the LLM (`Gemini 2.5 Flash`). The LLM is instructed to answer the query *only* using the provided context, which eliminates hallucinations.

### Q2: Why did you choose the `all-MiniLM-L6-v2` model for embeddings, and what are its dimensions?
* **Answer**: `all-MiniLM-L6-v2` is an extremely fast and efficient local embedding model from Sentence-Transformers. It generates **384-dimensional** embeddings, providing an optimal balance between retrieval accuracy, small footprint, and low-latency local execution.

### Q3: How does the file watcher (Watchdog) connect to AWS S3?
* **Answer**: We run a background Python script using the `watchdog` library. It schedules an observer on the `uploads/` folder. When a `FileCreatedEvent` occurs (e.g., when a user uploads a PDF), it invokes the `boto3` client to upload the file to our AWS S3 bucket (`sigma-datatech-abhi`) and triggers the auto-indexing pipeline to chunk, embed, and store the file in ChromaDB.

### Q4: Explain how the Agentic Router works. Why not send everything to RAG?
* **Answer**: Sending structural queries (like *"What columns are in users_data?"* or *"Who owns the products table?"*) to semantic RAG can be inaccurate since vector search is designed for semantic matching rather than exact metadata lookups. 
The **Agentic Router** is an orchestrator that analyzes the query keywords:
- If a query contains schema/column/owner keywords, it routes to the **Metadata Agent** which reads the physical schema in `tables.json`.
- If a query contains lineage keywords, it routes to the **Lineage Agent** which reads `lineage.json`.
- It falls back to **RAG** only for semantic questions, ensuring 100% accuracy for structural database lookups.

### Q5: How is persistent storage handled for the vector database?
* **Answer**: We use ChromaDB's `PersistentClient` pointing to a local directory path (`data/chroma_db`). This ensures that vector embeddings and metadata index files are saved directly to disk and do not disappear when the application restarts.

### Q6: How does the UI theme switcher handle styling dynamically?
* **Answer**: We store the theme state (`Light` or `Dark`) inside Streamlit's `st.session_state`. Depending on the state, a set of corresponding color hex codes are loaded and dynamically injected as CSS variables into the app's HTML container. This updates all custom elements (metrics, cards, inputs, lineage nodes, and bottom containers) to match the selected theme.
