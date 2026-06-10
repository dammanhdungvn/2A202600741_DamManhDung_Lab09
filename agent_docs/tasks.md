# Danh sách Phân chia Task (Task Breakdown)

File này định nghĩa các task có độ lớn vừa phải, giúp AI Agent có thể hoàn thành từng bước một cách an toàn, dễ kiểm tra (verify) và tránh ôm đồm quá nhiều thay đổi cùng lúc.

## Task 1: Khởi tạo Môi trường & Triển khai Data Lookup (Worker 2 Foundation)
- **Mục tiêu:** Quản lý môi trường bằng `python3 -m venv` và hoàn thiện logic đọc/truy vấn mock data JSON.
- **Công việc chi tiết:**
  1. Tạo virtual environment bằng `python3 -m venv .venv` và cài đặt các thư viện trong `src/requirements.txt` bằng `pip install -r src/requirements.txt`.
  2. Tại `src/app/data_access.py`: 
     - Hoàn thiện `ShoppingDataStore.__init__` để đọc `order_customer_mock_data.json` và xây dựng các in-memory indexes (ví dụ: dict tra cứu nhanh).
     - Viết code cho 4 hàm tra cứu: `get_customer_by_id`, `get_orders_by_customer_id`, `get_order_detail_by_order_id`, `get_vouchers_by_customer_id`.
     - Cập nhật `build_data_tools` bọc 4 hàm trên bằng `@tool` decorator của Langchain.
- **Tiêu chí hoàn thành (Verify):** Khởi tạo thành công `ShoppingDataStore` trong một script test tạm thời và query thử ra kết quả đúng.

## Task 2: Triển khai RAG Engine (Worker 1 Foundation)
- **Mục tiêu:** Xử lý file markdown và nạp vào Chroma vector database.
- **Công việc chi tiết:**
  1. Tại `src/rag/parser.py`: Xây dựng hàm `parse_policy_markdown` chia nội dung file markdown theo quy tắc phân cấp `H2 -> H3 -> Content`.
  2. Tại `src/rag/vector_store.py`:
     - Khởi tạo kết nối tới Chroma sử dụng `PersistentClient` lưu tại `src/.chroma/`.
     - Viết hàm `rebuild()` gọi `SentenceTransformerEmbeddings` để nhúng các chunks và lưu vào Chroma.
     - Viết hàm `search()` truy vấn bằng vector embeddings, trả về các đoạn policy liên quan nhất kèm trích dẫn (citation) và điểm số distance.
- **Tiêu chí hoàn thành (Verify):** Chạy hàm rebuild không lỗi. Thực hiện một truy vấn `search("trả hàng")` và in ra kết quả.

## Task 3: Kỹ nghệ Prompt & Xây dựng các LangGraph Nodes
- **Mục tiêu:** Định nghĩa System Prompts và viết logic cơ bản cho các node xử lý của đồ thị đa tác tử.
- **Công việc chi tiết:**
  1. Tại `src/app/prompts.py`: Hoàn thiện System Prompts định dạng trả về JSON cho `Supervisor`, `Policy Worker`, `Data Worker` và `Response Worker`. Chú ý bắt các case `not_found` và `clarification_needed`.
  2. Tại `src/app/graph.py`: Hoàn thành thân hàm cho `supervisor_node` (gọi LLM và trả về JSON routing intent), `worker_1_policy_node` (sử dụng RAG), `worker_2_data_node` (sử dụng `@tool`), và `worker_3_response_node` (tổng hợp thông tin).
- **Tiêu chí hoàn thành (Verify):** Code không bị lỗi cú pháp, kiểm tra hàm `extract_json_payload` (trong `utils.py`) parse đúng các output mock từ LLM.

## Task 4: Liên kết LangGraph & Thực thi Câu hỏi đơn (CLI Integration)
- **Mục tiêu:** Đóng gói các Nodes thành một StateGraph hoàn chỉnh và cho phép chạy từ dòng lệnh (CLI).
- **Công việc chi tiết:**
  1. Tại `src/app/graph.py`: Viết hàm `build_graph()` khai báo `StateGraph(ShoppingState)`, định nghĩa các `add_node` và viết hàm logic cho `add_conditional_edges` điều hướng luồng từ Supervisor tới các nhánh thích hợp.
  2. Tại `src/app/graph.py` (Class `ShoppingAssistant`): Viết hàm `ask()` khởi tạo đồ thị, gọi `invoke` với State ban đầu và xuất file trace JSON ra `artifacts/traces/` nếu yêu cầu.
  3. Tại `src/app/cli.py`: Hoàn thiện xử lý parameter `--question` cho lệnh CLI.
- **Tiêu chí hoàn thành (Verify):** Chạy `uv run python -m app.cli --question "Đơn hàng 1971 có được hoàn trả không?"` trả ra kết quả chuẩn format (Success + Evidence).

## Task 5: Xử lý Hàng loạt & Xuất báo cáo (Batch Processing)
- **Mục tiêu:** Kiểm tra độ tin cậy của toàn hệ thống với tập dữ liệu test.
- **Công việc chi tiết:**
  1. Tại `src/app/graph.py` (Class `ShoppingAssistant`): Viết hàm `run_batch()` đọc `data/test.json`. Vòng lặp gọi `ask()` cho từng câu hỏi, lưu trace file rời cho mỗi case.
  2. Sinh ra file tổng hợp `summary.json` liệt kê tỷ lệ thành công, các route đã thực thi và status.
  3. Tại `src/app/cli.py`: Hoàn thiện xử lý parameter `--batch`.
- **Tiêu chí hoàn thành (Verify):** Lệnh `uv run python -m app.cli --batch` chạy ra hàng loạt logs, thư mục trace ghi nhận đúng 15 files và file `summary.json` có đủ thông tin.

## Task 6: Hoàn thiện & Refactor (Test Automation)
- **Mục tiêu:** Chuyển đổi các script test thủ công sang bộ test tự động vững chắc.
- **Công việc chi tiết:**
  1. Khi bước sang Phase 4, 5 (Hoàn thiện & Refactor): Chúng ta nên gom các file `test_*.py` này bỏ vào một thư mục `tests/`.
  2. Cài đặt `pytest`.
  3. Chuyển các hàm `print()` thành các câu lệnh `assert` để hình thành bộ test tự động vững chắc.
- **Tiêu chí hoàn thành (Verify):** Cấu trúc lại thư mục thành công và lệnh `pytest tests/` chạy pass toàn bộ các test cases.
