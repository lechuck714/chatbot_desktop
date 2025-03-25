# 🚀 Comprehensive Chatbot Desktop Application (GPT-4o Assistant)
## 📖 Project Overview
The GPT-4o Assistant is a sophisticated desktop chatbot application leveraging advanced GPT-based AI technology, structured agent interactions, embedding services, semantic search with vector databases, and a rich user-interface built with Python’s Flet framework. It is designed for robust, contextually-rich user interactions involving document parsing, dataset interrogation, web scraping, and general-purpose conversational agents.
## 🎯 Key Objectives
The GPT-4o Assistant aims to:
- Provide dynamic interactions through intelligent agents: Document Agent (`DocAgent`), Data Agent (`DataAgent`), Web Agent (`WebAgent`), and a General Agent (`GeneralAgent`).
- Integrate AI language models (GPT-4-turbo, GPT-3.5-turbo) for advanced conversational understanding.
- Utilize semantic embeddings (OpenAI’s ADA model) and vector services (Chroma DB) for efficient context retrieval.
- Enable intuitive interaction via a responsive GUI built on Python's Flet framework.
- Offer comprehensive file support (PDF, DOCX, CSV, Excel, TXT) and robust PDF-exporting capabilities for conversation archiving.

## 🗃️ Project Architecture and Core Components
### 📁 Directory Structure Overview
``` 
chatbot_desktop/
├── config/
│   └── config.py                     # API client configuration (OpenAI)
├── core/
│   ├── agents/
│   │   ├── base_agent.py             # Base class defining agent behaviors
│   │   ├── doc_agent.py              # Agent specialized in document interrogation
│   │   ├── data_agent.py             # Agent handling structured data queries
│   │   ├── web_agent.py              # Agent for fetching and interpreting web pages
│   │   └── general_agent.py          # General-purpose fallback conversational agent
│   └── agent_manager.py              # Central agent management & routing
│
├── services/
│   ├── ai_service.py                 # GPT model API interactions and prompts
│   ├── embedding_service.py          # Text embedding generation with OpenAI
│   └── vector_service.py             # Vector database (Chroma DB) semantic searching
│
├── storage/
│   ├── blackboard.py                 # Shared memory structure for agent coordination
│   └── file_handler.py               # Multi-format file parsing (TXT, PDF, DOCX, CSV, XLSX)
│
├── utils/
│   ├── chunker.py                    # Document segmentation for embeddings
│   └── hybrid_numeric_semantic.py    # Advanced semantic numeric analysis utilities
│
├── ui/
│   └── flet_app.py                   # User interface application built with Flet
│
├── temp/                             # Temporary storage for exports (PDF history, cache)
├── vector_db/                        # Persistent storage location for Chroma DB embeddings
├── requirements.txt                  # Python dependencies
└── README.md                         # Project documentation (this file)
```
## 🤖 Detailed Agent System
The project articulates a sophisticated agent-driven architecture, supported by:
### 1. **Agent Manager (`agent_manager.py`)**
- Central routing of queries based on current active context (Document, Data, Web).
- Agents can be automatically switched depending on content loaded (document or dataframe), or explicitly via UI interaction.

### 2. **Intelligent Agents**

| Agent | Responsibility & Handling |
| --- | --- |
| **DocAgent** | Parses and manages textual documents; uses embeddings & vector search (Chroma DB) for semantic queries (`vector_service.py`). |
| **DataAgent** | Manages structured data (DataFrames), offers summaries, statistics & visualizations generated dynamically through pandas and matplotlib. |
| **WebAgent** | Fetches and analyzes web content, intelligently summarizing the fetched resources via GPT-based interpretation (`ai_service.py`). |
| **GeneralAgent** | Provides a flexible conversational fallback capable of general-purpose interactions, ensuring fluid conversations when specialized agents are inactive. |
### 3. **Agent Communication & Memory (`Blackboard`)**
- A centralized global state (`blackboard.py`) enabling effective inter-agent memory sharing:
    - Stores history of interactions, file contexts, structured data, website contents, and intermediate analysis results.

## 📐 Embedding & Vector Services
- **Text Embeddings:**
    - Powered via OpenAI (`embedding_service.py`), using `'text-embedding-ada-002'`.

- **Semantic Search (Chroma DB):**
    - Managed through `vector_service.py`, enabling rapid semantic search and similarity detection on document chunks stored persistently.

## 🗄️ File Handling & Document Management
- Robust multi-format file parsing (`file_handler.py`):
    - Text files (`.txt`)
    - PDF files parsing with `pdfplumber`
    - DOCX documents parsing with `python-docx`
    - CSV & Excel files parsing with pandas (`dataframes`)

- Chunking documents into segments appropriate for embedding and semantic search (`chunker.py`).

## 🖥️ Front-end Application (`flet_app.py` - Flet framework)
- Interactive GUI application powered by the modern, lightweight Python GUI toolkit "Flet".
- Offers conversation management, input/output display, PDF export functionality, file loading, agent switching, and app-wide settings management like theme toggling.

## 🔧 Configuration (`settings.py & config.py`)
- Manages OpenAI API keys and default embedding models securely through environment variables.

## 📊 Advanced Utility Modules
- **Hybrid Semantic & Numeric Analysis (`hybrid_numeric_semantic.py`):**
    - Allows for more sophisticated numerical data operations or hybrid semantic/numerical analytical capabilities.

## ✅ Key Functional Highlights
- AI-driven conversational agents with multi-domain specificity.
- Rich embedding-derived semantic search capabilities.
- Document and structured data integration for context enrichment.
- Elegant user-interface with comprehensive interactive controls.
- Persistent vector DB for scalable information retrieval.
- Robust conversation archiving & exporting as PDF.

## 🛠️ Setup & Installation (brief example)
``` bash
git clone https://github.com/lechuck714/chatbot_desktop.git
cd chatbot_desktop
pip install -r requirements.txt
```
Ensure `OPENAI_API_KEY` environment variable is set correctly before running:
``` bash
export OPENAI_API_KEY='your-key-here'
```
Launch with:
``` bash
python ui/flet_app.py
```
## 🚧 Roadmap & Future Enhancements
1. Enhanced file-type support and richer preprocessing pipelines.
2. Extended UI features (real-time visualization, richer interactive widgets).
3. Scalable cloud deployment options.
4. Expanded agent capabilities and context-handling enhancements.

## 📋 Conclusion
This **GPT-4o Assistant** combines powerful GPT-based conversational AI, structured intelligent agents, and state-of-the-art semantic search techniques into a cohesive desktop tool, offering users intuitive and insightful interactions across document analyses, structured datasets interrogation, real-time web data parsing, and general-purpose conversations.
