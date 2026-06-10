from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config import Settings
from app.state import ShoppingState


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

        # TODO 1:
        # - load chat model từ provider tương ứng
        # - load dataset order/customer
        # - load vector store cho policy
        # - build worker tools
        # - compile LangGraph

        self.graph = None

    def ask(
        self,
        question: str,
        trace_file: Path | None = None,
        rebuild_index: bool = False,
    ) -> dict[str, Any]:
        # TODO 2:
        # - nếu rebuild_index=True thì rebuild Chroma collection
        # - invoke graph với state ban đầu
        # - lưu trace ra JSON nếu trace_file được cung cấp
        # - trả về payload gồm route, policy_result, data_result, final_answer, trace
        raise NotImplementedError("Student TODO: implement ask()")

    def run_batch(
        self,
        test_file: Path,
        output_dir: Path,
        rebuild_index: bool = False,
    ) -> dict[str, Any]:
        # TODO 3:
        # - đọc data/test.json hoặc file test được truyền từ CLI
        # - chạy từng câu qua ask()
        # - lưu trace riêng cho từng case
        # - sinh summary.json
        raise NotImplementedError("Student TODO: implement run_batch()")


def build_graph() -> Any:
    # TODO 4:
    # - định nghĩa StateGraph(ShoppingState)
    # - add các node: supervisor, worker_1_policy, worker_2_data, worker_3_response
    # - add conditional edges cho routing
    raise NotImplementedError("Student TODO: compile the LangGraph workflow")


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
