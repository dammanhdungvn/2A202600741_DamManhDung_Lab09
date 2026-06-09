import sys
from pathlib import Path

# Add src to pythonpath so we can import app
sys.path.append(str(Path(__file__).parent / "src"))

from app.data_access import ShoppingDataStore, build_data_tools

def main():
    json_path = Path("data/order_customer_mock_data.json")
    if not json_path.exists():
        print(f"File not found: {json_path}")
        return

    print("Initializing ShoppingDataStore...")
    store = ShoppingDataStore(json_path)
    
    print("\n--- Test get_customer_by_id ('C001') ---")
    print(store.get_customer_by_id("C001"))
    
    print("\n--- Test get_orders_by_customer_id ('C001', limit=1) ---")
    print(store.get_orders_by_customer_id("C001", limit=1))
    
    print("\n--- Test get_order_detail_by_order_id ('1971') ---")
    print(store.get_order_detail_by_order_id("1971"))
    
    print("\n--- Test get_vouchers_by_customer_id ('C001', only_active=True) ---")
    print(store.get_vouchers_by_customer_id("C001", only_active=True))

    print("\n--- Test invalid order ID ('9999') ---")
    print(store.get_order_detail_by_order_id("9999"))

    tools = build_data_tools(store)
    print(f"\n--- Built {len(tools)} tools ---")
    for t in tools:
        print(f"- {t.name}: {t.description}")

if __name__ == "__main__":
    main()
