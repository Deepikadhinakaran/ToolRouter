
````markdown
# 🧭 ToolRouter — Intelligent Tool Selection Framework

> A modular, permission-aware tool routing framework that intelligently selects and executes the most appropriate tool for a user query based on relevance, risk, cost, latency, and access permissions.

**Query → Route → Permission Check → Execute → Answer**

---

## 🚀 Overview

Modern AI agents often have access to multiple tools such as calculators, databases, document retrieval systems, and search services. Selecting the correct tool while maintaining security, performance, and access control is a key challenge.

**ToolRouter** addresses this problem by providing a centralized routing layer that evaluates available tools and selects the most suitable one for each incoming query.

The framework combines:

- Intelligent tool selection
- Role-based access control
- Tool/function calling
- RAG-based document retrieval
- Modular tool registration
- Routing score transparency
- Execution latency tracking
- REST API integration
- Interactive web interface

---

## 🎯 Problem Statement

Traditional multi-tool systems may rely primarily on keyword matching or direct tool execution. This can lead to:

- Incorrect tool selection
- Unauthorized tool execution
- Unnecessary computational cost
- Higher response latency
- Difficult-to-maintain tool integrations

ToolRouter introduces a dedicated routing and authorization layer to make tool execution more **reliable, modular, secure, and observable**.

---

## 💡 Solution

ToolRouter evaluates candidate tools using multiple routing factors:

```text
                    User Query
                        │
                        ▼
                Query Analysis
                        │
                        ▼
              Candidate Tool Set
                        │
            ┌───────────┼───────────┐
            ▼           ▼           ▼
        Relevance      Risk       Cost
            │           │           │
            └───────────┼───────────┘
                        ▼
                     Latency
                        │
                        ▼
                 Tool Selection
                        │
                        ▼
                Permission Check
                   │         │
                Granted     Denied
                   │         │
                   ▼         ▼
              Execution   Rejection
                   │
                   ▼
                  Answer
````

This separates **tool selection** from **authorization**, allowing the framework to determine what tool is appropriate before deciding whether the current role is allowed to use it.

---

# ✨ Key Features

### 🧠 Intelligent Tool Routing

Selects the most appropriate tool from multiple candidates based on routing criteria.

### 🔐 Role-Based Access Control

Supports different levels of access:

```text
Guest
Employee
Admin
```

### 🧰 Modular Tool Registry

Tools can be registered and extended without changing the core routing architecture.

### 📚 RAG & Document Search

Supports document-based knowledge retrieval for enterprise policies and project documentation.

### ⚡ Performance Tracking

Measures tool execution latency and exposes it through the API and UI.

### 📊 Routing Transparency

Displays candidate tool scores so routing decisions can be inspected.

### 🔌 REST API

Provides a FastAPI backend for integration with external applications.

### 🖥️ Interactive UI

Provides a Streamlit interface for querying the system and visualizing routing results.

### 🐳 Docker Support

The backend is containerized for deployment.

### 🧪 Automated Testing

Includes Pytest-based testing and GitHub Actions CI.

---

# 🛠️ Technology Stack

| Category         | Technologies         |
| ---------------- | -------------------- |
| Language         | Python               |
| Backend          | FastAPI, Uvicorn     |
| Agentic AI       | LangChain, LangGraph |
| Retrieval        | RAG, Embeddings      |
| Database         | SQLite               |
| Frontend         | Streamlit            |
| Containerization | Docker               |
| Deployment       | Render               |
| Testing          | Pytest               |
| CI/CD            | GitHub Actions       |

---

# 🧰 Supported Tools

## 1. Calculator

Handles mathematical and arithmetic queries.

**Example:**

```text
Calculate 125 * 48
```

→ Routes to `calculator`

---

## 2. Database

Handles structured database-related queries.

**Example:**

```text
Find employee 105
```

→ Routes to `database`

---

## 3. Document Search / RAG

Retrieves information from project and policy documents.

**Example:**

```text
What is the leave policy?
```

→ Routes to `document_search`

Example documents:

```text
company_policy.txt
leave_policy.txt
project_documentation.txt
```

---

## 4. Search

Handles general information-search queries.

**Example:**

```text
Search for information about Python
```

→ Routes to `search`

---

# 🔐 Permission Model

ToolRouter uses role-based access control.

```text
                 User
                   │
                   ▼
                Query
                   │
                   ▼
             Tool Router
                   │
                   ▼
           Selected Tool
                   │
                   ▼
           Permission Check
              /          \
         Allowed        Denied
            │              │
            ▼              ▼
       Execute Tool    Access Denied
```

Authorization is performed **after routing**, ensuring that selecting a tool does not automatically grant permission to execute it.

---

# 🏗️ System Architecture

```text
┌───────────────────────────────────────┐
│             Streamlit UI             │
│                                       │
│  Query • Role • Tool • Permission    │
│  Latency • Answer • Routing Scores   │
└───────────────────┬───────────────────┘
                    │
                    │ HTTP
                    ▼
┌───────────────────────────────────────┐
│             FastAPI Backend           │
│                                       │
│              /chat                    │
└───────────────────┬───────────────────┘
                    │
                    ▼
┌───────────────────────────────────────┐
│             ToolRouter                │
│                                       │
│  Query Analysis                       │
│  Candidate Generation                 │
│  Routing Score                        │
│  Tool Selection                       │
│  Permission Validation                │
└───────────┬───────────┬───────────────┘
            │           │
            ▼           ▼
     ┌────────────┐ ┌───────────────┐
     │   Tools    │ │ Security Layer│
     └─────┬──────┘ └───────────────┘
           │
     ┌─────┼──────────┬─────────────┐
     ▼     ▼          ▼             ▼
 Calculator Database  RAG         Search
```

---

# 🔄 Request Flow

A typical request follows this pipeline:

```text
1. User submits a query
              ↓
2. Query is analyzed
              ↓
3. Candidate tools are identified
              ↓
4. Routing scores are calculated
              ↓
5. Best tool is selected
              ↓
6. User role is validated
              ↓
7. Authorized tool is executed
              ↓
8. Result is returned
              ↓
9. Latency and routing information are exposed
```

---

# 📊 Example

### Input

```json
{
  "query": "What is 25 * 4?",
  "role": "employee"
}
```

### Routing

```text
Candidate Tools
       ↓
Calculator       ← Highest score
Database
Document Search
Search
       ↓
Permission Check
       ↓
Granted
       ↓
Calculator
       ↓
100
```

### Result

```text
Selected Tool : calculator
Permission    : Granted
Answer        : 100
```

---

# 📚 Project Structure

```text
ToolRouter/
│
├── app/
│   ├── __init__.py
│   ├── agent.py
│   ├── main.py
│   ├── registry.py
│   ├── router.py
│   ├── security.py
│   ├── tracing.py
│   │
│   └── tools/
│       ├── __init__.py
│       ├── calculator.py
│       ├── database.py
│       ├── rag.py
│       └── search.py
│
├── data/
│   └── documents/
│       ├── company_policy.txt
│       ├── leave_policy.txt
│       └── project_documentation.txt
│
├── tests/
│   ├── __init__.py
│   ├── evaluate.py
│   └── test_router.py
│
├── ui/
│   └── streamlit_app.py
│
├── .github/
│   └── workflows/
│       └── test.yml
│
├── .env.example
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt
```

---

# 🧪 Testing

The project includes automated tests for routing and tool behavior.

Testing covers:

* Tool selection
* Permission handling
* API behavior
* Error handling
* Routing decisions
* Response generation
* Performance measurement

CI tests are automatically executed through **GitHub Actions**.

---

# ☁️ Deployment

The project uses a separated frontend and backend architecture.

```text
                  Internet
                     │
                     ▼
          ┌─────────────────────┐
          │    Streamlit UI     │
          │      Frontend       │
          └──────────┬──────────┘
                     │
                     │ HTTPS
                     ▼
          ┌─────────────────────┐
          │    FastAPI API      │
          │      Render         │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │     ToolRouter      │
          │    Routing Engine   │
          └─────────────────────┘
```

### Backend

FastAPI backend is containerized using Docker and deployed as a web service.

### Frontend

The Streamlit interface communicates with the deployed FastAPI backend through HTTP requests.

---

# 🔮 Future Enhancements

* LLM-based semantic tool routing
* Advanced embedding-based routing
* Vector database integration
* External search API integration
* Redis-based caching
* JWT/OAuth authentication
* Advanced observability
* Routing accuracy benchmarks
* Cost-aware tool optimization
* Dynamic tool discovery
* Multi-agent orchestration
* Enterprise-scale monitoring

---

# 🎓 Learning Outcomes

This project demonstrates practical experience in:

* Python backend development
* REST API design
* Agentic AI architecture
* Tool/function calling
* RAG systems
* Role-based authorization
* Modular software architecture
* Database integration
* Docker containerization
* Cloud deployment
* Automated testing and CI/CD
* Frontend-backend integration

---

# 🌟 Why ToolRouter?

ToolRouter is designed around a simple principle:

> **Choose the right tool first, verify permission second, and execute safely.**

By combining intelligent routing, authorization, modular tool integration, and observability, ToolRouter provides a foundation for building **secure and scalable multi-tool AI applications**.

---

# 👩‍💻 Author

### Deepika D

**B.Tech — Computer Science and Business Systems**
R.M.K. Engineering College

[GitHub](https://github.com/Deepikadhinakaran)

[LinkedIn](https://linkedin.com/in/deepika-d-4a538628)

---

## ⭐ Project Status

**Active Development**

ToolRouter is continuously being improved with additional routing strategies, tools, security capabilities, and AI integrations.

````

### One important correction before you commit

Your current `streamlit_app.py` says:

```python
API_URL = os.getenv("TOOLROUTER_API_URL", "http://127.0.0.1:8000")
````

If you are deploying the UI publicly, change that default to:

```python
API_URL = os.getenv("TOOLROUTER_API_URL", "https://toolrouter.onrender.com")
```

Also make sure `requirements.txt` contains **`streamlit` and `requests`**.

Then commit:

```cmd
git add README.md ui requirements.txt
git commit -m "Add professional project documentation and Streamlit UI"
git push origin main
```


