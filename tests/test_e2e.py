import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from app.graph import ShoppingAssistant

def test_shopping_assistant_ask():
    assistant = ShoppingAssistant()
    
    # Test a simple query
    result = assistant.ask(
        question="Đơn hàng 1971 có được hoàn trả không?",
        rebuild_index=False
    )
    
    assert "route" in result
    assert "final_answer" in result
    
    # Check trace
    trace = result.get("trace", [])
    assert len(trace) > 0
    
    # Since it needs policy and data, trace should include multiple nodes
    nodes_visited = [step["node"] for step in trace]
    assert "supervisor" in nodes_visited
    assert "worker_3_response" in nodes_visited
