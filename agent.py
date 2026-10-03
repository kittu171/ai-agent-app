from typing import TypedDict, Annotated

from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage,HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

from tools import calculator, knowledge_search


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    retry_count: int
    approval_status: str


llm = ChatOllama(
    model="llama3.2",
    temperature=0
)


tools = [
    calculator,
    knowledge_search
]

llm_with_tools = llm.bind_tools(tools)


def agent_node(state: AgentState):

    system_message = SystemMessage(
        content="""
You are an AI agent.

You have two tools:

1. calculator

Use it for mathematical calculations.

2. knowledge_search

Use it for questions about Generative AI, RAG,
embeddings, LangGraph, and AI agents.

Choose the correct tool when needed.
"""
    )

    response = llm_with_tools.invoke(
            [system_message] + state["messages"]
        )

    print("\n--- AGENT NODE ---")
    print("Tool Calls:", response.tool_calls)
    print("Model Response:", response.content)

    return {
        "messages": [response]
    }


tool_node = ToolNode(tools)

def approval_node(state: AgentState):

    approval = interrupt(
        {
            "message": "Human approval required before executing the tool."
        }
    )

    if approval == "approve":
        return {
            "approval_status": "approved"
        }

    return {
        "approval_status": "rejected",
        "messages": [
            SystemMessage(
                content="Tool execution was rejected by the human."
            )
        ]
    }

def retry_node(state: AgentState):

    retry_count = state.get("retry_count", 0) + 1

    print("\n--- RETRY ---")
    print("Retry Count:", retry_count)

    messages = state["messages"]

    # Find the last AI message that contains a tool call
    last_ai_message = None

    for message in reversed(messages):

        if isinstance(message, AIMessage) and message.tool_calls:
            last_ai_message = message
            break

    if last_ai_message is None:
        return {
            "retry_count": retry_count
        }

    tool_call = last_ai_message.tool_calls[0]

    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    tool_call_id = tool_call["id"]

    # Retry the SAME tool directly
    for tool in tools:

        if tool.name == tool_name:

            try:

                result = tool.invoke(tool_args)

            except Exception as e:

                result = f"TOOL_ERROR: {str(e)}"

            print("\n--- RETRIED TOOL RESULT ---")
            print("Tool:", tool_name)
            print("Result:", result)

            return {
                "retry_count": retry_count,
                "messages": [
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call_id,
                        name=tool_name
                    )
                ]
            }

    return {
        "retry_count": retry_count,
        "messages": [
            ToolMessage(
                content="TOOL_ERROR: Tool not found.",
                tool_call_id=tool_call_id,
                name=tool_name
            )
        ]
    }


def should_retry(state: AgentState):

    messages = state["messages"]

    for message in reversed(messages):

        if isinstance(message, ToolMessage):

            if "CALCULATION_ERROR" in message.content:

                if state.get("retry_count", 0) < 2:
                    return "retry"

                return "fallback"

            return "success"

    return "success"

def final_answer_node(state: AgentState):

    messages = state["messages"]

    tool_result = ""
    tool_name = ""
    user_question = ""

    # Get latest tool result
    for message in reversed(messages):

        if isinstance(message, ToolMessage):
            tool_result = message.content
            tool_name = message.name
            break

    # Get latest user question
    for message in reversed(messages):

        if isinstance(message, HumanMessage):
            user_question = message.content
            break

    print("\n--- TOOL RESULT ---")
    print("Tool:", tool_name)
    print("Result:", tool_result)

    prompt = f"""
You are the final answer generator.

Answer the user's question using ONLY the tool result.

Rules:
1. Answer the user's exact question.
2. Use only the tool result.
3. Do not use outside knowledge.
4. Do not repeat unrelated information.
5. Keep the answer concise.

6. If the tool is "calculator" and the result is valid,
   return the calculator result as the final answer.

7. If the tool result contains an error,
   clearly report that the calculation could not be completed.

8. Only say "I could not find this information" when
   the tool result genuinely does not contain an answer.

Tool Name:
{tool_name}

Tool Result:
{tool_result}

User Question:
{user_question}

Final Answer:
"""

    if "CALCULATION_ERROR" in tool_result or "TOOL_ERROR" in tool_result:

        return {
            "messages": [
                SystemMessage(
                    content="I couldn't complete the calculation after 2 retries."
                )
            ]
        }

    response = llm.invoke(prompt)

    return {
        "messages": [
            SystemMessage(content=response.content.strip())
        ]
    }

graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)
graph.add_node("approval", approval_node)
graph.add_node("tools", tool_node)
graph.add_node("retry", retry_node)
graph.add_node("final_answer", final_answer_node)

graph.add_edge(START, "agent")

graph.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "approval",
        "__end__": END
    }
)
def approval_route(state: AgentState):
    if state.get("approval_status") == "approved":
        return "tools"

    return "rejected"

graph.add_conditional_edges(
    "approval",
    approval_route,
    {
        "tools": "tools",
        "rejected": END
    }
)

graph.add_conditional_edges(
    "tools",
    should_retry,
    {
        "retry": "retry",
        "success": "final_answer",
        "fallback": "final_answer"
    }
)

graph.add_conditional_edges(
    "retry",
    should_retry,
    {
        "retry": "retry",
        "success": "final_answer",
        "fallback": "final_answer"
    }
)

graph.add_edge("final_answer", END)

memory = MemorySaver()

agent = graph.compile(
    checkpointer=memory
)


if __name__ == "__main__":        

    conversation = []

    print("AI Agent started.")
    print("Type 'exit' to stop.\n")

    while True:

        question = input("You: ").strip()

        if question.lower() == "exit":
            print("\nAgent stopped.")
            break

        if not question:
            continue

        config = {
            "configurable": {
                "thread_id": "agent-session"
            }
        }

        result = agent.invoke(        
            {
                "messages": conversation + [
                    HumanMessage(content=question)
                ],
                "retry_count": 0
            },
            config=config
        )

        if "__interrupt__" in result:        

            print("\n⚠️ Human approval required.")
            print("Approve tool execution? (yes/no)")

            approval = input("Approval: ").strip().lower()

            if approval == "yes":

                result = agent.invoke(
                    Command(resume="approve"),
                    config=config
                )

            else:

                result = agent.invoke(
                    Command(resume="reject"),
                    config=config
                )

        final_message = result["messages"][-1]

        conversation = result["messages"]

        print("\nAgent:", final_message.content)
        print()