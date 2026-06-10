import os
import sys
from pathlib import Path

# Add src to PYTHONPATH so tests can import app and rag
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from app.data_access import ShoppingDataStore, build_data_tools
from rag.embeddings import SentenceTransformerEmbeddings
from rag.vector_store import ChromaPolicyStore

def test_data_store():
    data_path = Path("data/order_customer_mock_data.json")
    store = ShoppingDataStore(data_path)
    
    # 1. Test get_customer_by_id
    res1 = store.get_customer_by_id("C001")
    assert res1["status"] == "ok"
    assert res1["customer"]["customer_name"] == "Nguyen Thu Anh"
    
    # 2. Test get_orders_by_customer_id
    res2 = store.get_orders_by_customer_id("C002")
    assert res2["status"] == "ok"
    assert len(res2["orders"]) > 0
    
    # 3. Test get_order_detail_by_order_id
    res3 = store.get_order_detail_by_order_id("1971")
    assert res3["status"] == "ok"
    assert res3["order"]["order_id"] == "1971"
    
    # 4. Test get_vouchers_by_customer_id
    res4 = store.get_vouchers_by_customer_id("C003", only_active=True)
    assert res4["status"] == "ok"
    assert len(res4["vouchers"]) == 2

    # 5. Test LangChain tools
    tools = build_data_tools(store)
    assert len(tools) == 4
    tool_names = [t.name for t in tools]
    assert "get_customer_by_id" in tool_names


def test_rag_engine():
    persist_dir = Path("src/.chroma")
    policy_path = Path("data/policy_mock_vi.md")
    
    embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    policy_store = ChromaPolicyStore(persist_dir, embedding_model)
    
    # Ensure index exists
    policy_store.ensure_index(policy_path)
    
    # Search for known policy
    results = policy_store.search("thời gian giao hàng", top_k=2)
    assert len(results) > 0
    assert "giao hàng" in results[0]["content"].lower()
