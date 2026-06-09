# Product Requirements
- **Supervisor Routing**: Dynamically route user intent to Policy, Data, or both workers.
- **RAG Policy Worker**: Chunk markdown (H2 -> H3 -> Content), store in Chroma, search using `sentence-transformers`, and summarize with citations.
- **Data Lookup Worker**: Expose 4 distinct tools (`get_customer_by_id`, `get_orders_by_customer_id`, `get_order_detail_by_order_id`, `get_vouchers_by_customer_id`) to query JSON data.
- **Response Worker**: Format final output as `Success`, `Clarification`, or `Not found`.
- **Batch Testing & Tracing**: Run 15 pre-defined questions via CLI and export detailed JSON traces.
