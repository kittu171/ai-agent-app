from fastapi import FastAPI
from pydantic import BaseModel

from agent import agent
from langchain_core.messages import HumanMessage
from langgraph.types import Command


app = FastAPI(
    title="AI Agent API",
    description="LangGraph AI Agent with Tools, Retry, Guardrails and HITL",
    version="1.0.0"
)


class AskRequest(BaseModel):
    question: str
    thread_id: str = "api-session"


class ApprovalRequest(BaseModel):
    thread_id: str = "api-session"
    approval: str


@app.get("/health")
def health():

    return {
        "status": "ok"
    }


@app.post("/ask")
def ask(request: AskRequest):

    question = request.question.strip()

    # Input Guardrail
    if not question:

        return {
            "error": "Question cannot be empty."
        }

    if len(question) > 500:

        return {
            "error": "Question is too long. Maximum 500 characters allowed."
        }

    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    result = agent.invoke(
        {
            "messages": [
                HumanMessage(content=question)
            ],
            "retry_count": 0
        },
        config=config
    )

    if "__interrupt__" in result:

        return {
            "status": "approval_required",
            "thread_id": request.thread_id,
            "message": "Human approval required before executing the tool."
        }

    final_message = result["messages"][-1]

    return {
        "status": "completed",
        "question": question,
        "answer": final_message.content
    }


@app.post("/approve")
def approve(request: ApprovalRequest):

    approval = request.approval.strip().lower()

    if approval not in ["yes", "no"]:
        return {
            "error": "Approval must be 'yes' or 'no'."
        }

    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    if approval == "yes":

        result = agent.invoke(
            Command(resume="approve"),
            config=config
        )

        final_message = result["messages"][-1]

        return {
            "status": "completed",
            "answer": final_message.content
        }

    result = agent.invoke(
        Command(resume="reject"),
        config=config
    )

    return {
        "status": "rejected",
        "answer": "Tool execution was rejected by the human."
    }