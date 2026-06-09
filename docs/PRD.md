# Tài liệu Yêu cầu Sản phẩm (PRD)
**Tên Sản phẩm:** Trợ lý Mua sắm Đa Tác tử (Multi-Agent Shopping Assistant)
**Ngày:** 9 tháng 6, 2026
**Trạng thái:** MVP (Dự án trường học)

## 1. Mục tiêu
Mục tiêu của dự án này là xây dựng một trợ lý mua sắm trực tuyến thông minh sử dụng **Kiến trúc Đa Tác tử (Multi-Agent Architecture)** thông qua **LangGraph**. Trợ lý phải tích hợp một Mô hình Ngôn ngữ Lớn (LLM) thực tế, triển khai Kỹ thuật Sinh văn bản tăng cường truy xuất (Retrieval-Augmented Generation - RAG) sử dụng Cơ sở dữ liệu Vector cục bộ (Chroma) để đọc các chính sách cửa hàng từ dữ liệu phi cấu trúc, và sử dụng các công cụ bên ngoài để tra cứu dữ liệu có cấu trúc về khách hàng, đơn hàng và voucher từ một cơ sở dữ liệu giả lập JSON cục bộ.

## 2. Yêu cầu Chức năng
* **Điều phối (Supervisor Routing)**: Một Tác tử Giám sát (Supervisor Agent) sẽ phân tích câu hỏi đầu vào của người dùng và định tuyến yêu cầu đến (các) tác tử con phù hợp:
  * Định tuyến đến Policy Worker (Tác tử Chính sách) cho các câu hỏi chung về chính sách.
  * Định tuyến đến Data Worker (Tác tử Dữ liệu) cho các truy vấn cụ thể về khách hàng/đơn hàng/voucher.
  * Định tuyến đến cả hai cho các câu hỏi phức tạp yêu cầu kết hợp quy định chính sách với dữ liệu cụ thể của người dùng.
* **Tìm kiếm RAG Chính sách (Worker 1)**: Khả năng đọc và tìm kiếm chính sách cửa hàng từ một tệp Markdown. Phải phân chia dữ liệu (chunking) chính xác theo cấu trúc `H2` -> `H3` -> `Content` và trả về câu trả lời được tóm tắt kèm theo trích dẫn (citations).
* **Công cụ Tra cứu Dữ liệu (Worker 2)**: Sử dụng ít nhất 4 công cụ cụ thể để tra cứu dữ liệu JSON giả lập:
  1. `get_customer_by_id(customer_id)`
  2. `get_orders_by_customer_id(customer_id)`
  3. `get_order_detail_by_order_id(order_id)`
  4. `get_vouchers_by_customer_id(customer_id)`
* **Tổng hợp Phản hồi (Worker 3)**: Tổng hợp thông tin từ các tác tử worker thành một phản hồi cuối cùng hướng tới người dùng, tuân thủ một trong ba định dạng được xác định nghiêm ngặt: `Success` (Thành công - kèm theo Bằng chứng), `Clarification` (Yêu cầu làm rõ), hoặc `Not found` (Không tìm thấy).
* **Quản lý Trạng thái (State Management)**: Hệ thống phải duy trì trạng thái xuyên suốt quá trình thực thi đồ thị, bao gồm câu hỏi ban đầu, quyết định định tuyến, kết quả chính sách, kết quả dữ liệu và câu trả lời cuối cùng.
* **Kiểm thử Hàng loạt (Batch Testing)**: Khả năng chạy các bài kiểm thử hàng loạt thông qua CLI sử dụng tệp đầu vào `data/test.json`, tạo ra các bản ghi (traces) cho mỗi ca kiểm thử và một tệp `summary.json` cuối cùng.

## 3. Yêu cầu Phi chức năng
* **Không phụ thuộc LLM/Nhà cung cấp tùy chỉnh**: Hệ thống phải hỗ trợ các endpoint và khóa API của LLM tùy chỉnh. Cụ thể, hệ thống phải hỗ trợ cấu hình môi trường tùy chỉnh được cung cấp mà không bị phụ thuộc hoàn toàn vào các khóa mặc định được đề cập trong `Guide.md`.
* **Embeddings**: Phải sử dụng cụ thể mô hình `sentence-transformers/all-MiniLM-L6-v2` để tạo embeddings văn bản cục bộ.
* **Cơ sở dữ liệu Vector**: Phải sử dụng `Chroma` cho cơ sở dữ liệu vector cục bộ.
* **Khả năng Truy vết (Traceability)**: Phải tạo và lưu các tệp nhật ký truy vết JSON chi tiết cho mọi truy vấn để tạo điều kiện thuận lợi cho việc gỡ lỗi các lệnh gọi công cụ và quyết định định tuyến.
* **Xử lý Lỗi**: 
  * Xử lý khéo léo việc thiếu định danh thực thể (ví dụ: hỏi về một đơn hàng nhưng không cung cấp `order_id`) bằng cách trả về trạng thái `clarification_needed` (cần làm rõ).
  * Xử lý khéo léo việc tra cứu dữ liệu không tồn tại bằng cách trả về trạng thái `not_found` (không tìm thấy).

## 4. Câu chuyện Người dùng (User Stories)
* **US1**: Là một khách hàng, tôi muốn hỏi các câu hỏi chung về chính sách đổi trả của cửa hàng để tôi biết quyền lợi của mình trước khi mua hàng.
* **US2**: Là một khách hàng, tôi muốn kiểm tra ngày giao hàng dự kiến cho đơn hàng cụ thể của tôi (ví dụ: đơn hàng 1971) để tôi biết khi nào có thể nhận được hàng.
* **US3**: Là một khách hàng, tôi muốn hỏi xem đơn hàng cụ thể của tôi (ví dụ: đơn hàng 1971) có đủ điều kiện để đổi trả không để tôi không phải tự đối chiếu chính sách với trạng thái đơn hàng của mình.
* **US4**: Là một khách hàng, tôi muốn hệ thống yêu cầu tôi cung cấp ID đơn hàng nếu tôi hỏi "Gói hàng của tôi ở đâu?" mà không cung cấp mã vận đơn hoặc mã đơn hàng.
* **US5**: Là một nhà phát triển, tôi muốn chạy kiểm thử hàng loạt 15 câu hỏi được xác định trước để tôi có thể xác minh hệ thống đa tác tử của mình định tuyến và trả lời chính xác mà không cần kiểm thử thủ công.

## 5. Tiêu chí Chấp nhận (Acceptance Criteria)
1. **Thực thi End-to-End**: Quy trình LangGraph biên dịch và chạy thành công từ CLI cho cả câu hỏi đơn lẻ (`--question`) và kiểm thử hàng loạt (`--batch`).
2. **Định tuyến Chính xác**: Node Supervisor nhận diện chính xác ý định và thiết lập các cờ `needs_policy` và/hoặc `needs_data` một cách phù hợp cho tất cả các ca kiểm thử.
3. **Độ chính xác RAG**: Cơ sở dữ liệu Chroma được xây dựng thành công với các đoạn (chunks) tuân thủ nghiêm ngặt cấu trúc `H2 + H3 + Content`. Việc tìm kiếm chính sách trả về các phân đoạn markdown và trích dẫn chính xác.
4. **Thực thi Công cụ**: Data Worker thực thi thành công (các) công cụ chính xác trong số 4 công cụ tra cứu được định nghĩa dựa trên các tham số truy vấn của người dùng.
5. **Tuân thủ Định dạng**: Response Worker xuất ra chuỗi cuối cùng khớp chính xác với các quy tắc định dạng của bài thực hành (ví dụ: Xuất ra `Answer:` và `Evidence:` đối với thành công, hoặc `Status: clarification_needed`).
6. **Nhật ký Truy vết**: Các tệp truy vết JSON được tạo ra một cách đáng tin cậy và chứa đầu ra của supervisor, các lệnh gọi công cụ của worker, các đoạn được truy xuất và câu trả lời cuối cùng.

## 6. Phạm vi MVP (MVP Scope)
Sản phẩm Khả thi Tối thiểu (Minimum Viable Product) cho bài tập này bao gồm:
* Tệp `.env` được cấu hình để sử dụng nhà cung cấp LLM tùy chỉnh.
* Triển khai `src/app/data_access.py` để lập chỉ mục và phục vụ dữ liệu mock JSON.
* Triển khai `src/rag/parser.py` và `src/rag/vector_store.py` để xử lý markdown chính sách và lập chỉ mục Chroma.
* Định nghĩa các prompt cho tác tử trong `src/app/prompts.py`.
* Lắp ráp LangGraph trong `src/app/graph.py` với 1 Supervisor và 3 Workers.
* Các khả năng kiểm thử CLI cơ bản trong `src/app/cli.py`.
* Hỗ trợ 3 loại câu hỏi cốt lõi (Chỉ hỏi Chính sách, Chỉ hỏi Dữ liệu, Hỗn hợp Chính sách+Dữ liệu) và các trường hợp biên (`not_found`, `clarification_needed`).
