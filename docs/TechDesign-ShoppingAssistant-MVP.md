# Tài liệu Thiết kế Kỹ thuật (Technical Design Document)
**Tên Sản phẩm:** Trợ lý Mua sắm Đa Tác tử (Multi-Agent Shopping Assistant)
**Dựa trên:** PRD (`docs/PRD.md`)
**Ngôn ngữ:** Tiếng Việt

---

## 1. Kiến trúc Đề xuất (Recommended Architecture)
Hệ thống sử dụng **Kiến trúc Đa Tác tử (Multi-Agent Architecture)** được điều phối bởi **LangGraph**. Luồng dữ liệu (State) sẽ chạy qua các Node (Tác tử) với chức năng chuyên biệt:

*   **State**: Một `TypedDict` lưu trữ toàn bộ ngữ cảnh thực thi: `question`, `route`, `policy_result`, `data_result`, `final_answer`, `trace`.
*   **Supervisor Node**: Đóng vai trò là Bộ định tuyến (Router). Nhận câu hỏi, gọi LLM để phân tích ý định và thiết lập cờ `needs_policy` và/hoặc `needs_data`. Nếu thiếu ID quan trọng, trả về yêu cầu `clarification_needed`.
*   **Worker 1 (Policy/RAG Node)**: Được kích hoạt khi `needs_policy = True`. Sử dụng công cụ RAG để tìm kiếm các phân đoạn chính sách phù hợp từ Chroma DB, tóm tắt và trích xuất `citations`.
*   **Worker 2 (Data Node)**: Được kích hoạt khi `needs_data = True`. Sử dụng các công cụ tra cứu (`@tool`) để truy vấn cơ sở dữ liệu JSON In-memory. Trả về dữ liệu thô hoặc trạng thái `not_found`.
*   **Worker 3 (Response Node)**: Là điểm đến cuối cùng sau khi các Worker hoàn tất. Node này tổng hợp các kết quả từ `policy_result` và `data_result` để sinh ra phản hồi ngôn ngữ tự nhiên theo 1 trong 3 định dạng: `Success`, `Clarification` hoặc `Not found`.

---

## 2. Lược đồ Cơ sở Dữ liệu (Database Schema)

Vì đây là dự án cấu trúc dữ liệu mô phỏng cục bộ (mock local data), hệ thống sử dụng 2 loại cơ sở dữ liệu:

### 2.1. Vector Database (Chroma)
Lưu trữ thông tin chính sách dạng phi cấu trúc.
*   **`id`**: String (Mã định danh duy nhất cho chunk)
*   **`document`**: String (Văn bản Markdown đã được nối từ `H2 + H3 + Content`)
*   **`embedding`**: Array[Float] (Vector nhúng sinh ra từ `sentence-transformers/all-MiniLM-L6-v2`)
*   **`metadata`**: Object chứa thông tin truy vết:
    *   `section_h2`: String
    *   `section_h3`: String
    *   `citation`: String (Ví dụ: "Chính sách đổi trả > Điều kiện chung")

### 2.2. In-memory Mock JSON DB (`data_access.py`)
Đọc từ tệp `order_customer_mock_data.json` và lập chỉ mục (index) thông qua Python Dictionary:
*   **Customers (`customer_by_id`)**: `customer_id`, `customer_name`, `tier`, `max_voucher_per_month`, `vouchers_used_this_month`, `remaining_voucher_quota_this_month`, `total_orders`, `total_spent`, `latest_order_id`
*   **Orders (`order_by_id`, `orders_by_customer_id`)**: `order_id`, `customer_id`, `order_status`, `estimated_delivery`, `eligible_for_return_until`, `can_return_now`, `voucher_code`, `items`
*   **Vouchers (`vouchers_by_customer_id`)**: `voucher_code`, `customer_id`, `voucher_type`, `discount_value`, `status`, `remaining_uses`

---

## 3. Các "Endpoint" API (API Endpoints / Tools)

Thay vì API HTTP truyền thống, hệ thống giao tiếp thông qua các **LLM Tools** nội bộ và **Giao diện dòng lệnh (CLI)**.

### 3.1. Các Công cụ Tác tử (Agent Tools)
*   `get_customer_by_id(customer_id: str)`: Trả về thông tin hồ sơ khách hàng.
*   `get_orders_by_customer_id(customer_id: str, limit: int = 10)`: Trả về lịch sử mua hàng của người dùng.
*   `get_order_detail_by_order_id(order_id: str)`: Trả về trạng thái chi tiết của một đơn hàng.
*   `get_vouchers_by_customer_id(customer_id: str, only_active: bool = False)`: Trả về danh sách voucher kèm trạng thái khả dụng.
*   `search_policy(query: str, top_k: int = 4)`: Gửi truy vấn ngữ nghĩa tới Chroma DB và lấy về các chính sách liên quan nhất.

### 3.2. CLI "Endpoints"
*   **Truy vấn đơn**: `python -m app.cli --question "Câu hỏi của người dùng" [--trace-file path/to/save.json]`
*   **Chạy thử nghiệm hàng loạt**: `python -m app.cli --batch --test-file data/test.json`

---

## 4. Cấu trúc Thư mục (Folder Structure)

```text
.
├── data/
│   ├── policy_mock_vi.md        # File gốc Markdown chính sách
│   ├── order_customer_mock_data.json # Mock DB
│   ├── test.json                # Bộ câu hỏi test case
│   └── README.md
├── docs/
│   ├── PRD.md                   # Product Requirements Document
│   └── TechDesign-ShoppingAssistant-MVP.md # Tài liệu này
├── src/
│   ├── app/
│   │   ├── cli.py               # Giao diện dòng lệnh chính
│   │   ├── config.py            # Quản lý Settings và biến môi trường
│   │   ├── data_access.py       # Logic xử lý mock JSON DB và tạo Tools
│   │   ├── graph.py             # Khởi tạo và thiết lập luồng LangGraph
│   │   ├── prompts.py           # Lưu trữ các system prompts cho Tác tử
│   │   ├── state.py             # Định nghĩa TypedDict cho ShoppingState
│   │   └── utils.py             # Các hàm tiện ích (parse JSON, datetime...)
│   ├── provider/
│   │   └── custom.py            # Cấu hình Custom LLM Provider
│   ├── rag/
│   │   ├── embeddings.py        # Wrapper cho SentenceTransformers
│   │   ├── parser.py            # Xử lý cắt (chunking) Markdown 
│   │   └── vector_store.py      # Thao tác với Chroma DB
│   ├── artifacts/traces/        # Thư mục chứa trace JSON xuất ra
│   └── .chroma/                 # Thư mục lưu trữ CSDL vector (Persistent)
├── .env                         # Cấu hình môi trường (Không commit)
├── requirements.txt             # Các thư viện phụ thuộc
└── README.md
```

---

## 5. Technology Stack (Công nghệ & Thư viện)

*   **Ngôn ngữ Lập trình**: Python 3.11+
*   **Framework Orchestration**: `langgraph`, `langchain-core`
*   **Mô hình Ngôn ngữ (LLM)**: Hỗ trợ Custom Provider qua `langchain-openai` (sử dụng base_url và key custom cho model Deepseek theo `.env`).
*   **Tạo Embeddings**: Thư viện `sentence-transformers` (Model: `all-MiniLM-L6-v2`)
*   **Cơ sở dữ liệu Vector**: `chromadb`
*   **Quản lý Môi trường**: `python-dotenv`

---

## 6. Các giai đoạn Phát triển (Development Phases)

*   **Giai đoạn 1: Thiết lập & Nền tảng Dữ liệu (Worker 2)**
    *   Cấu hình `.env` với endpoint LLM tuỳ chỉnh.
    *   Hoàn thành `src/app/data_access.py`: Đọc file JSON, lập các indexes trong bộ nhớ.
    *   Định nghĩa 4 Tool Methods và bọc bởi `@tool` decorator.
*   **Giai đoạn 2: Công cụ RAG (Worker 1)**
    *   Hoàn thiện hàm parse Markdown trong `src/rag/parser.py` đảm bảo cấu trúc `H2 -> H3 -> Content`.
    *   Viết logic lưu và tìm kiếm vector trong `src/rag/vector_store.py` sử dụng Chroma PersistentClient.
*   **Giai đoạn 3: Kỹ nghệ Prompt (Prompt Engineering)**
    *   Viết lại các System Prompts chặt chẽ trong `src/app/prompts.py` cho 4 tác tử, ép LLM tuân thủ nghiêm ngặt định dạng JSON đầu ra và bắt được các trường hợp cần làm rõ (`clarification`).
*   **Giai đoạn 4: Điều phối bằng Đồ thị (Graph Orchestration)**
    *   Kết nối toàn bộ các nút trong `src/app/graph.py` thông qua `StateGraph`.
    *   Viết hàm Router để phân luồng các `conditional_edges` từ Supervisor tới các Worker và tụ lại tại Response Worker.
*   **Giai đoạn 5: Tích hợp CLI & Kiểm thử Đơn (Single Testing)**
    *   Hoàn tất `cli.py` để biên dịch Graph và xử lý tham số `--question`.
    *   Khắc phục các lỗi (bug) khi truyền dữ liệu giữa các node.
*   **Giai đoạn 6: Xử lý Hàng loạt & Truy vết (Batch & Tracing)**
    *   Triển khai `--batch` với file `data/test.json`.
    *   Đảm bảo cơ chế lưu file trace cho mỗi lượt chạy vào `artifacts/traces` hoạt động trơn tru. Tạo file tổng hợp `summary.json`. Kiểm tra đối chiếu Acceptance Criteria.
