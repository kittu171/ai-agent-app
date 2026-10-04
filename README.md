# 🤖 AI Agent Workflow App

A production-style AI Agent Workflow application built with **LangGraph, LangChain, Ollama, FastAPI, and Python**.

This project demonstrates how an AI agent can understand a user's question, select the appropriate tool, execute the tool, handle failures with retry logic, request human approval before tool execution, and generate a final answer.

---

## 🚀 Project Overview

The application follows an agentic workflow:

```text
User Question
      ↓
   FastAPI
      ↓
   AI Agent
      ↓
  Tool Selection
   ↙        ↘
Calculator  Knowledge Search
   ↓            ↓
Human Approval
      ↓
Tool Execution
      ↓
Retry / Fallback
      ↓
Final Answer
```

The main goal of this project is to demonstrate a **stateful AI agent workflow** rather than a simple chatbot.

---

## ✨ Features

* 🧠 AI Agent powered by Ollama
* 🔧 Tool calling
* 🧮 Calculator tool
* 📚 Knowledge/RAG search tool
* 🧑‍💻 Human-in-the-loop approval
* 🔁 Retry mechanism for tool failures
* 🛡️ Fallback handling
* 🧠 Stateful workflow using LangGraph
* 🌐 FastAPI REST API
* 📖 Swagger API documentation
* 🐳 Docker support
* 💾 In-memory checkpointing for workflow state

---

## 🏗️ Architecture

```text
                    ┌─────────────────┐
                    │   User Query    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    FastAPI      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   AI Agent      │
                    │   LangGraph     │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
             ┌─────────────┐   ┌───────────────┐
             │ Calculator  │   │ Knowledge     │
             │    Tool     │   │ Search Tool   │
             └──────┬──────┘   └───────┬───────┘
                    │                  │
                    └────────┬─────────┘
                             ▼
                    ┌─────────────────┐
                    │ Human Approval   │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
                 Approved           Rejected
                    │
                    ▼
              Tool Execution
                    │
                    ▼
             Retry if Failure
                    │
                    ▼
              Final Answer
```

---

## 🛠️ Technologies Used

| Technology   | Purpose                             |
| ------------ | ----------------------------------- |
| Python       | Core programming language           |
| LangGraph    | Agent workflow and state management |
| LangChain    | LLM and tool integration            |
| Ollama       | Local LLM execution                 |
| Llama 3.2    | Language model                      |
| FastAPI      | REST API                            |
| Docker       | Containerization                    |
| ChromaDB     | Vector/knowledge storage            |
| Git & GitHub | Version control                     |

---

## 📁 Project Structure

```text
ai-agent-app/
│
├── agent.py
├── api.py
├── tools.py
├── knowledge_tool.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
└── README.md
```

### `agent.py`

Contains the main AI agent workflow.

Responsibilities:

* Defines the agent state
* Initializes the Ollama LLM
* Binds tools to the LLM
* Handles agent decisions
* Executes the LangGraph workflow
* Implements retry logic
* Implements fallback handling
* Generates the final answer
* Handles human approval flow

---

### `tools.py`

Contains the tools available to the AI agent.

Currently implemented:

#### Calculator

Performs mathematical calculations.

Example:

```text
What is 15 * 20?
```

Result:

```text
300
```

#### Knowledge Search

Used for questions related to:

* Generative AI
* RAG
* Embeddings
* LangGraph
* AI Agents

---

### `knowledge_tool.py`

Contains the knowledge/RAG search functionality used by the agent to retrieve relevant information.

---

### `api.py`

Contains the FastAPI application.

The API exposes endpoints for:

* Asking questions
* Approving tool execution
* Rejecting tool execution

---

## 🔄 Agent Workflow

### 1. User sends a question

Example:

```text
What is 15 * 20?
```

### 2. AI Agent analyzes the question

The agent identifies that this is a mathematical question.

### 3. Agent selects the Calculator tool

```text
calculator
```

### 4. Human approval is requested

The application pauses before executing the tool.

Example response:

```json
{
  "status": "approval_required",
  "thread_id": "test-1",
  "message": "Human approval required before executing the tool."
}
```

### 5. Human approves

The workflow resumes.

### 6. Calculator executes

```text
15 * 20 = 300
```

### 7. Final answer is generated

```text
The final answer is 300.
```

---

## 🧑‍💻 Human-in-the-Loop

This project includes a human approval mechanism before tool execution.

The workflow can be:

```text
Agent selects tool
       ↓
Approval Required
       ↓
   ┌───┴────┐
   ↓        ↓
  YES       NO
   ↓        ↓
Execute   Reject
   ↓
Answer
```

If the human rejects the tool:

```text
Tool execution was rejected by the human.
```

This demonstrates how an AI agent can include human oversight before performing an action.

---

## 🔁 Retry & Fallback

The application includes retry handling for tool failures.

Workflow:

```text
Tool Execution
      ↓
   Success?
   ↙      ↘
 YES       NO
 ↓         ↓
Answer    Retry
            ↓
       Retry Limit
            ↓
        Fallback
```

The agent can retry a failed tool operation up to the configured retry limit.

If the operation still fails:

```text
I couldn't complete the calculation after 2 retries.
```

---

## 🌐 FastAPI API

Start the API server and open:

```text
http://127.0.0.1:8000/docs
```

FastAPI provides an interactive Swagger UI for testing the API.

### Main Endpoints

#### Ask a question

```text
POST /ask
```

Used to send a question to the AI agent.

#### Approve or reject tool execution

```text
POST /approve
```

Used to continue the workflow after human approval.

---

## 📚 Example Queries

### Calculator

```text
What is 25 * 40?
```

Response:

```text
The final answer is 1000.
```

### Knowledge Search

```text
What is RAG?
```

The agent selects the knowledge search tool and generates an answer using the retrieved information.

### Embeddings

```text
What are embeddings?
```

Example response:

```text
Embeddings convert text into numerical vectors so that semantic similarity can be calculated.
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/kittu171/ai-agent-app.git
```

```bash
cd ai-agent-app
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Git Bash:

```bash
source .venv/Scripts/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🦙 Ollama Setup

Install Ollama and make sure the required model is available locally.

Pull the model:

```bash
ollama pull llama3.2
```

Start Ollama:

```bash
ollama serve
```

The application uses:

```text
llama3.2
```

with:

```text
temperature = 0
```

---

## ▶️ Run the Application

### Run the agent directly

```bash
python agent.py
```

### Run the FastAPI server

```bash
uvicorn api:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

---

## 🐳 Docker

Build the Docker image:

```bash
docker build -t ai-agent-app .
```

Run the container:

```bash
docker run --rm -p 8000:8000 -e OLLAMA_HOST=http://host.docker.internal:11434 ai-agent-app
```

Then open:

```text
http://127.0.0.1:8000/docs
```

---

## 🧠 Why LangGraph?

LangGraph is used to represent the agent as a stateful workflow.

Instead of:

```text
Question → Answer
```

this project uses:

```text
Question
   ↓
Agent
   ↓
Tool Selection
   ↓
Tool Execution
   ↓
Retry / Approval
   ↓
Final Answer
```

This makes it possible to implement more advanced agent behavior such as:

* State management
* Conditional routing
* Tool execution
* Human approval
* Retry logic
* Error handling
* Multi-step workflows

---

## 🎯 What This Project Demonstrates

This project demonstrates practical implementation of:

* Generative AI
* AI Agents
* Agentic Workflows
* Tool Calling
* RAG / Knowledge Retrieval
* LangGraph
* LangChain
* Local LLMs
* Human-in-the-loop systems
* Retry and fallback mechanisms
* REST APIs
* Docker containerization

---

## 🚧 Future Improvements

Possible future enhancements:

* Persistent database-backed memory
* More AI tools
* Web search tool
* Weather tool
* Email tool
* Authentication
* Streaming responses
* Production database
* Observability and logging
* Agent evaluation
* Frontend UI
* Cloud deployment

---

## 👩‍💻 Author

**Kittu**

GitHub: [kittu171](https://github.com/kittu171)

---

## 📌 Project Status

**Status: Completed ✅**

This project was built as a practical demonstration of a production-style AI agent workflow using local LLMs, tools, human approval, retry handling, FastAPI, and Docker.
