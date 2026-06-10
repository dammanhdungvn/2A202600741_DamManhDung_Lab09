from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config import Settings
from app.state import ShoppingState
from provider import get_chat_model
from app.data_access import ShoppingDataStore, build_data_tools
from rag.vector_store import ChromaPolicyStore
from rag.embeddings import SentenceTransformerEmbeddings
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
import json
import functools


class ShoppingAssistant:
    """Student scaffold.

    Mục tiêu:
    - Dùng `Settings` để load config.
    - Dùng provider trong `src/provider/`.
    - Dùng embedding loader thật trong `src/rag/embeddings.py`.
    - Tự hoàn thiện phần còn lại: graph, routing, tool calling, RAG search, response synthesis.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings.load()

        # Load model
        self.model = get_chat_model(self.settings)

        # Load dataset & tools
        data_path = Path("data/order_customer_mock_data.json")
        self.data_store = ShoppingDataStore(data_path)
        self.data_tools = build_data_tools(self.data_store)

        # Load RAG
        persist_dir = Path("src/.chroma")
        policy_path = Path("data/policy_mock_vi.md")
        self.embedding_model = SentenceTransformerEmbeddings("all-MiniLM-L6-v2")
        self.policy_store = ChromaPolicyStore(persist_dir, self.embedding_model)
        
        # Build search policy tool
        @tool
        def search_policy(query: str) -> str:
            """Search the store policy using vector search."""
            hits = self.policy_store.search(query, top_k=3)
            if not hits:
                return "No relevant policy found."
            return "\n\n".join([f"Source: {h['citation']}\n{h['content']}" for h in hits])
            
        self.search_policy_tool = search_policy
        
        # Compile LangGraph
        self.graph = build_graph(self.model, self.search_policy_tool, self.data_tools)

    def ask(
        self,
        question: str,
        trace_file: Path | None = None,
        rebuild_index: bool = False,
    ) -> dict[str, Any]:
        if rebuild_index:
            self.policy_store.ensure_index(Path("data/policy_mock_vi.md"))
            
        state = {"question": question, "trace": []}
        final_state = self.graph.invoke(state)
        
        if trace_file:
            trace_file.parent.mkdir(parents=True, exist_ok=True)
            with open(trace_file, "w", encoding="utf-8") as f:
                json.dump(final_state.get("trace", []), f, ensure_ascii=False, indent=2)
                
        return final_state

    def run_batch(
        self,
        test_file: Path,
        output_dir: Path,
        rebuild_index: bool = False,
    ) -> dict[str, Any]:
        if rebuild_index:
            self.policy_store.ensure_index(Path("data/policy_mock_vi.md"))
            
        with open(test_file, "r", encoding="utf-8") as f:
            cases = json.load(f)
            
        summary = {
            "total": len(cases),
            "success": 0,
            "failed": 0,
            "results": []
        }
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, case in enumerate(cases):
            question = case.get("question", "")
            trace_path = output_dir / f"trace_{i+1:03d}.json"
            
            try:
                state = {"question": question, "trace": []}
                final_state = self.graph.invoke(state)
                
                with open(trace_path, "w", encoding="utf-8") as f:
                    json.dump(final_state.get("trace", []), f, ensure_ascii=False, indent=2)
                    
                summary["success"] += 1
                summary["results"].append({
                    "id": i + 1,
                    "question": question,
                    "status": "Success",
                    "route": final_state.get("route", {}).get("status", "unknown"),
                    "trace_file": str(trace_path.name)
                })
            except Exception as e:
                summary["failed"] += 1
                summary["results"].append({
                    "id": i + 1,
                    "question": question,
                    "status": "Error",
                    "error": str(e)
                })
                
        with open(output_dir / "summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
            
        return summary


def build_graph(model: Any, search_tool: Any, data_tools: list[Any]) -> Any:
    builder = StateGraph(ShoppingState)

    # Bind tools to nodes
    bound_supervisor = functools.partial(supervisor_node, model=model)
    bound_policy = functools.partial(worker_1_policy_node, model=model, search_tool=search_tool)
    bound_data = functools.partial(worker_2_data_node, model=model, data_tools=data_tools)
    bound_response = functools.partial(worker_3_response_node, model=model)

    builder.add_node("supervisor", bound_supervisor)
    builder.add_node("worker_1_policy", bound_policy)
    builder.add_node("worker_2_data", bound_data)
    builder.add_node("worker_3_response", bound_response)

    builder.add_edge(START, "supervisor")

    def route_supervisor(state: ShoppingState) -> list[str]:
        route_info = state.get("route", {})
        status = route_info.get("status", "")
        
        if status == "clarification_needed":
            return ["worker_3_response"]
            
        destinations = []
        if route_info.get("needs_policy"):
            destinations.append("worker_1_policy")
        if route_info.get("needs_data"):
            destinations.append("worker_2_data")
            
        if not destinations:
            return ["worker_3_response"]
            
        return destinations

    builder.add_conditional_edges("supervisor", route_supervisor)
    builder.add_edge("worker_1_policy", "worker_3_response")
    builder.add_edge("worker_2_data", "worker_3_response")
    builder.add_edge("worker_3_response", END)

    return builder.compile()


from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from app.prompts import SUPERVISOR_PROMPT, POLICY_WORKER_PROMPT, DATA_WORKER_PROMPT, RESPONSE_WORKER_PROMPT
from app.utils import extract_json_payload

def supervisor_node(state: ShoppingState, model: Any = None) -> ShoppingState:
    question = state.get("question", "")
    messages = [
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=question)
    ]
    response = model.invoke(messages)
    route = extract_json_payload(response.content)
    
    trace_entry = {
        "node": "supervisor",
        "input": question,
        "output": route
    }
    return {"route": route, "trace": [trace_entry]}


def worker_1_policy_node(state: ShoppingState, model: Any = None, search_tool: Any = None) -> ShoppingState:
    question = state.get("question", "")
    messages = [
        SystemMessage(content=POLICY_WORKER_PROMPT),
        HumanMessage(content=question)
    ]
    
    # Bind the tool
    if search_tool:
        model_with_tools = model.bind_tools([search_tool])
    else:
        model_with_tools = model

    # Agent loop: call model, if tool call, execute and call model again
    response = model_with_tools.invoke(messages)
    messages.append(response)
    
    if response.tool_calls and search_tool:
        for tool_call in response.tool_calls:
            if tool_call["name"] == search_tool.name:
                tool_result = search_tool.invoke(tool_call["args"])
                messages.append(ToolMessage(tool_call_id=tool_call["id"], content=str(tool_result), name=search_tool.name))
        
        # Second call after getting tool results
        response = model_with_tools.invoke(messages)

    policy_result = extract_json_payload(response.content)
    
    trace_entry = {
        "node": "worker_1_policy",
        "input": question,
        "output": policy_result
    }
    return {"policy_result": policy_result, "trace": [trace_entry]}


def worker_2_data_node(state: ShoppingState, model: Any = None, data_tools: list[Any] = None) -> ShoppingState:
    question = state.get("question", "")
    messages = [
        SystemMessage(content=DATA_WORKER_PROMPT),
        HumanMessage(content=question)
    ]
    
    if data_tools:
        model_with_tools = model.bind_tools(data_tools)
        tool_map = {tool.name: tool for tool in data_tools}
    else:
        model_with_tools = model
        tool_map = {}

    response = model_with_tools.invoke(messages)
    messages.append(response)
    
    # Handle multiple tool calls
    if response.tool_calls and data_tools:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            if tool_name in tool_map:
                tool_result = tool_map[tool_name].invoke(tool_call["args"])
                messages.append(ToolMessage(tool_call_id=tool_call["id"], content=str(tool_result), name=tool_name))
        
        response = model_with_tools.invoke(messages)

    data_result = extract_json_payload(response.content)
    
    trace_entry = {
        "node": "worker_2_data",
        "input": question,
        "output": data_result
    }
    return {"data_result": data_result, "trace": [trace_entry]}


def worker_3_response_node(state: ShoppingState, model: Any = None) -> ShoppingState:
    question = state.get("question", "")
    route = state.get("route", {})
    policy_result = state.get("policy_result", {})
    data_result = state.get("data_result", {})
    
    context = f"Question: {question}\n\n"
    context += f"Supervisor routing: {route}\n\n"
    context += f"Policy findings: {policy_result}\n\n"
    context += f"Data findings: {data_result}\n\n"
    
    messages = [
        SystemMessage(content=RESPONSE_WORKER_PROMPT),
        HumanMessage(content=context)
    ]
    
    response = model.invoke(messages)
    final_answer = response.content
    
    trace_entry = {
        "node": "worker_3_response",
        "input": context,
        "output": final_answer
    }
    return {"final_answer": final_answer, "trace": [trace_entry]}
