# 🤖 Multi-Agent AI System for Business Automation

A production-grade multi-agent AI architecture enabling autonomous task execution through coordinated AI agents, powered by **LangGraph**, **LangChain**, **RAG**, and **FastAPI**.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2-purple)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## 🏗️ Architecture

```
                          ┌─────────────────┐
                          │   FastAPI Client │
                          └────────┬────────┘
                                   │
                          ┌────────▼────────┐
                          │   Supervisor     │
                          │   (Router Agent) │
                          └────────┬────────┘
                    ┌──────────────┼──────────────┐
              ┌─────▼─────┐ ┌─────▼─────┐ ┌──────▼──────┐
              │  Research  │ │ Reasoning │ │    Task     │
              │   Agent    │ │   Agent   │ │  Executor   │
              └─────┬──────┘ └───────────┘ └──────┬──────┘
                    │                              │
         ┌──────┐  ▼                       ┌──────▼──────┐
         │ RAG  │◄─┤                       │ DB │Cal│API │
         │Vector│  │                       └─────────────┘
         │  DB  │  │
         └──────┘  ▼
              ┌─────────────┐
              │Communication│
              │    Agent     │
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │    Email     │
              └─────────────┘
```

### Agents

| Agent | Role | Tools |
|-------|------|-------|
| **Supervisor** | Routes tasks to specialists | Structured output routing |
| **Research** | Web search & knowledge retrieval | `web_search`, `knowledge_base_search` |
| **Reasoning** | Analysis & strategic thinking | `knowledge_base_search` |
| **Task Executor** | Database, scheduling, APIs | `query_database`, `schedule_meeting`, `call_api` |
| **Communication** | Email drafting & notifications | `send_email` |

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- OpenAI API key

### 1. Clone & Install

```bash
git clone <repo-url>
cd multi-agent-bizz-ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run

```bash
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000/docs** for the interactive API documentation.

## 🐳 Docker Deployment

```bash
cp .env.example .env
# Edit .env with your keys
docker-compose up --build
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/chat` | Send a message to the multi-agent system |
| `POST` | `/api/v1/documents/upload` | Upload a document to the knowledge base |
| `GET` | `/api/v1/documents` | List ingested documents |
| `GET` | `/api/v1/agents/status` | View available agents and tools |

### Example Chat Request

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the active customers and their order totals?"}'
```

### Example Response

```json
{
  "answer": "Based on the database query, here are the active customers...",
  "session_id": "abc-123",
  "agents_used": ["supervisor", "task_executor"],
  "steps": []
}
```

## 🧪 Testing

```bash
pytest tests/ -v
```

## 🛠️ Tech Stack

| Technology | Purpose |
|-----------|---------|
| **LangGraph** | Multi-agent workflow orchestration |
| **LangChain** | LLM tooling, chains, and agent framework |
| **ChromaDB** | Vector database for RAG |
| **OpenAI** | LLM and embedding models |
| **FastAPI** | REST API framework |
| **Docker** | Containerized deployment |
| **Pydantic** | Data validation and settings |

## 📁 Project Structure

```
app/
├── agents/           # Specialised AI agents
│   ├── base.py       # Agent factory
│   ├── supervisor.py # Router agent
│   ├── research.py   # Research specialist
│   ├── reasoning.py  # Analytical reasoning
│   ├── task_executor.py  # Task execution
│   └── communication.py  # Communications
├── api/              # FastAPI routes & dependencies
├── graph/            # LangGraph workflow definition
├── llm/              # LLM provider abstraction
├── models/           # State & Pydantic schemas
├── rag/              # RAG pipeline (ingest, vectorstore, retrieve)
├── tools/            # External tool integrations
└── main.py           # Application entry point
```

## 📄 License

Apache 2.0 — see [LICENSE](LICENSE) for details.