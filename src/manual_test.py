import sys
import os
from pathlib import Path

# Đảm bảo có thể import các module từ thư mục src
sys.path.append(os.path.dirname(__file__))

from app.data_access import ShoppingDataStore, build_data_tools
from rag.vector_store import ChromaPolicyStore
from rag.embeddings import SentenceTransformerEmbeddings

def test_task1():
    print("="*50)
    print("TESTING TASK 1 (Data Lookup - Worker 2 Foundation)")
    print("="*50)
    
    # Chỉnh lại đường dẫn tới file mock data
    data_path = Path(__file__).parent.parent / "data" / "order_customer_mock_data.json"
    
    if not data_path.exists():
        print(f"Error: Không tìm thấy file {data_path}")
        return
        
    store = ShoppingDataStore(data_path)
    
    # 1. Test get_customer_by_id
    print("\n1. Get Customer by ID (C001):")
    res = store.get_customer_by_id("C001")
    print(res)
    
    # 2. Test get_orders_by_customer_id
    print("\n2. Get Orders by Customer ID (C002):")
    res = store.get_orders_by_customer_id("C002")
    print(f"Tìm thấy {len(res.get('orders', []))} orders. Trạng thái: {res['status']}")
    
    # 3. Test get_order_detail_by_order_id
    print("\n3. Get Order Detail by Order ID (1971):")
    res = store.get_order_detail_by_order_id("1971")
    print(res)
    
    # 4. Test get_vouchers_by_customer_id
    print("\n4. Get Vouchers by Customer ID (C003, only_active=True):")
    res = store.get_vouchers_by_customer_id("C003", only_active=True)
    print(res)

    # 5. Test @tool LangChain
    print("\n5. Testing LangChain Tools:")
    tools = build_data_tools(store)
    for t in tools:
        print(f"- {t.name}: {t.description}")
        if t.name == "get_customer_by_id":
            # Test thử gọi tool
            print(f"  => Invoke {t.name}('C001'):", t.invoke({"customer_id": "C001"}))


def test_task2():
    print("\n\n" + "="*50)
    print("TESTING TASK 2 (RAG Engine - Worker 1 Foundation)")
    print("="*50)
    
    persist_dir = Path(__file__).parent / ".chroma"
    policy_path = Path(__file__).parent.parent / "data" / "policy_mock_vi.md"
    
    if not policy_path.exists():
        print(f"Error: Không tìm thấy file {policy_path}")
        return
        
    print("Đang khởi tạo Embedding model (có thể mất chút thời gian lần đầu)...")
    embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    
    print("Đang khởi tạo Chroma DB...")
    policy_store = ChromaPolicyStore(persist_dir, embedding_model)
    
    print("\n1. Rebuilding / Loading Index:")
    policy_store.ensure_index(policy_path)
    
    print("\n2. Searching policy (Query: 'trả hàng'):")
    results = policy_store.search("trả hàng")
    
    if not results:
        print("Không tìm thấy kết quả nào.")
    else:
        for idx, hit in enumerate(results):
            print(f"\n--- Hit {idx+1} ---")
            print(f"Citation: {hit['citation']}")
            print(f"Distance: {hit['distance']}")
            print(f"Content preview: {hit['content'][:150]}...")

if __name__ == "__main__":
    test_task1()
    test_task2()
