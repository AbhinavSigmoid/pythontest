# 🚀 GenAI Data Engineering Assistant

## Overview

GenAI Data Engineering Assistant is an AI-powered platform designed to help data engineers quickly access information about pipelines, datasets, lineage, metadata, incidents, and operational documentation.

Instead of manually searching through documents, runbooks, and metadata files, users can ask questions in natural language and receive instant answers.

The system combines document search, metadata exploration, lineage tracking, and pipeline monitoring in a single interface.

---

# Business Problem

Data engineering teams often store important information across multiple locations:

- Pipeline documentation
- Runbooks
- Incident reports
- SLA documents
- Metadata files
- Data catalogs

Finding the right information can take significant time, especially during production incidents.

This project centralizes that knowledge and makes it accessible through a conversational AI interface.

---

# Solution

The GenAI Data Engineering Assistant provides:

- AI-powered question answering
- Data lineage exploration
- Metadata discovery
- Pipeline health monitoring
- Automated document ingestion
- AWS S3 backup
- GitHub repository ingestion
- Interactive enterprise dashboard

---

# Key Features

## 🤖 AI Assistant

Ask questions in natural language about:

- Pipelines
- Incidents
- SLAs
- Documentation
- Data quality
- Operational processes

## 📊 Pipeline Health

View:

- Pipeline status
- Availability metrics
- SLA compliance
- Recent incidents

## 📋 Data Catalog

Explore:

- Available tables
- Owners
- Columns
- PII information

## 🔄 Lineage Explorer

Visualize:

- Source systems
- Bronze layer
- Silver layer
- Gold layer

## 📥 Pipeline Ingestion

Provide a GitHub repository URL and the system can:

- Analyze repository structure
- Extract metadata
- Generate lineage information
- Build searchable knowledge
- Update platform insights

## 📂 Document Upload

Upload PDFs and documentation.

The platform automatically:

- Detects new files
- Uploads them to AWS S3
- Processes content
- Updates the knowledge base

---

# Architecture

```text
User
 │
 ▼
Streamlit Application
 │
 ▼
Router
 │
 ├── Metadata Agent
 ├── Lineage Agent
 ├── Health Agent
 └── AI Assistant
          │
          ▼
      Knowledge Base
          │
          ▼
      Gemini AI
```

---

# Technology Stack

- Python
- Streamlit
- Google Gemini
- ChromaDB
- Sentence Transformers
- AWS S3
- Watchdog
- Pandas
- LangChain

---

# Project Structure

```text
app/
agents/
rag/
ingestion/
scripts/
metadata/
docs/
data/
uploads/
```

---

# Setup

## Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

## Run Application

```bash
streamlit run app/streamlit_app.py
```

---

# Usage

1. Launch the Streamlit application.
2. Explore the dashboard.
3. Ask questions through the AI Assistant.
4. View pipeline health metrics.
5. Explore lineage and metadata.
6. Upload documents for automatic ingestion.
7. Ingest GitHub repositories for automated analysis.

---

# Future Enhancements

- Live Airflow integration
- Real-time monitoring
- Slack and Teams integration
- Advanced repository analysis
- Cloud-native vector database
- Automated incident recommendations

---

# Benefits

- Faster access to information
- Reduced operational effort
- Improved visibility into data assets
- Better incident response
- Centralized knowledge management

---

Built using Streamlit, Gemini, ChromaDB, and AWS.
