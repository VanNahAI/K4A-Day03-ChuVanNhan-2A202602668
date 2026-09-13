# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Chu Văn Nhân  
> **Mã Sinh Viên / Mã Học viên:** 2A202602668  
> **Chủ đề Lựa chọn:** Gợi ý 1.1: Trợ lý Học vụ & Tra cứu Lịch thi VinUni (VinUni Academic & Advisory Assistant)  

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | **4** / 5 | Bài toán yêu cầu chia nhỏ nhiều bước suy luận logic nối tiếp nhau. Ví dụ ở TC04: Để đặt lịch tư vấn, Agent phải chia nhỏ thành 2 chặng: Chặng 1 tra cứu hồ sơ để nhận diện chính xác Cố vấn học tập (Advisor) của sinh viên, Chặng 2 sử dụng tên Cố vấn đó để tiến hành đặt lịch hẹn tư vấn. |
| **2. Tool Interaction** | **5** / 5 | Hệ thống bắt buộc phải kết nối với MCP Server qua giao thức JSON-RPC 2.0 để đọc dữ liệu hồ sơ học vụ (`academic_query`) và ghi nhận lịch hẹn vào hệ thống (`schedule_appointment`). LLM đơn thuần không có dữ liệu thực tế và sẽ gặp ảo giác (Hallucination) nếu thiếu Tool. |
| **3. Dynamic Decision** | **4** / 5 | Quyết định hành động ở bước tiếp theo phụ thuộc trực tiếp vào kết quả quan sát (Observation) từ MCP Server. Nếu mã sinh viên trả về `NOT_FOUND` (như TC05), Agent quyết định ngưng quy trình và phản hồi cảnh báo; nếu trả về `SUCCESS`, Agent mới tiếp tục trích xuất trường dữ liệu cần thiết để thực thi bước kế tiếp. |
| **4. Long Horizon Goal** | **4** / 5 | Agent phải ghi nhớ và duy trì mục tiêu của người dùng xuyên suốt toàn bộ vòng lặp ReAct (`Thought -> Action -> Observation -> Final Answer`), đảm bảo sau khi hoàn tất các thao tác trung gian vẫn quay lại trả lời trọn vẹn yêu cầu ban đầu cho sinh viên. |
| **TỔNG ĐIỂM AGENTIC FIT** | **17 / 20** | *Tổng điểm 17/20 (> 12/20): Bài toán hoàn toàn phù hợp và phát huy tối đa sức mạnh của kiến trúc ReAct Agentic System.* |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dưới đây là đoạn trích xuất minh chứng chuỗi suy luận ReAct đa bước (**TC04: Multi-step Reasoning**) trích từ tệp log [`docs/trace_waterfall.json`](trace_waterfall.json) thực thi 100% trên Live LLM API (**Google Gemini 3.6 Flash**) kết nối với **MCP Server**:

```json
[
  {
    "step": 1,
    "query": "Hãy tra cứu thông tin học vụ của sinh viên SV2026001 để biết ai là cố vấn học tập, sau đó đặt lịch hẹn tư vấn với cố vấn đó vào lúc 09:00 ngày 20/09/2026.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "academic_query",
    "arguments": {
      "student_id": "SV2026001"
    },
    "observation": {
      "status": "SUCCESS",
      "student_id": "SV2026001",
      "data": {
        "full_name": "Nguyễn Văn An",
        "class": "AI-K4",
        "gpa": 3.85,
        "email": "an.nv@vinuni.edu.vn",
        "status": "Đang học",
        "advisor": "PGS.TS Nguyễn Văn A"
      }
    },
    "latency_ms": 1968.43
  },
  {
    "step": 2,
    "query": "Hãy tra cứu thông tin học vụ của sinh viên SV2026001 để biết ai là cố vấn học tập, sau đó đặt lịch hẹn tư vấn với cố vấn đó vào lúc 09:00 ngày 20/09/2026.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "schedule_appointment",
    "arguments": {
      "student_id": "SV2026001",
      "advisor_name": "PGS.TS Nguyễn Văn A",
      "datetime_str": "09:00 20/09/2026"
    },
    "observation": {
      "status": "SUCCESS",
      "booking_id": "BK-SV2026001-99",
      "student_id": "SV2026001",
      "datetime": "09:00 20/09/2026",
      "advisor": "PGS.TS Nguyễn Văn A",
      "message": "Đặt lịch thành công cho sinh viên SV2026001 với PGS.TS Nguyễn Văn A vào lúc 09:00 20/09/2026."
    },
    "latency_ms": 2408.17
  },
  {
    "step": 3,
    "query": "Hãy tra cứu thông tin học vụ của sinh viên SV2026001 để biết ai là cố vấn học tập, sau đó đặt lịch hẹn tư vấn với cố vấn đó vào lúc 09:00 ngày 20/09/2026.",
    "action_type": "FINAL_ANSWER",
    "thought": "Gemini phản hồi trực tiếp bằng văn bản (không cần gọi công cụ).",
    "output": "**Kết quả thực hiện yêu cầu:**\n\n1. **Thông tin tra cứu học vụ:**\n   - **Mã sinh viên:** SV2026001\n   - **Họ và tên:** Nguyễn Văn An\n   - **Lớp:** AI-K4\n   - **Cố vấn học tập (Advisor):** PGS.TS Nguyễn Văn A\n\n2. **Đặt lịch hẹn tư vấn học vụ:**\n   - **Mã đặt lịch:** BK-SV2026001-99\n   - **Người tiếp nhận:** PGS.TS Nguyễn Văn A\n   - **Thời gian:** 09:00 ngày 20/09/2026\n   - **Trạng thái:** Đặt lịch thành công.\n\nLịch hẹn tư vấn học vụ của bạn đã được ghi nhận vào hệ thống. Bạn vui lòng có mặt đúng giờ để buổi làm việc diễn ra hiệu quả nhất!",
    "latency_ms": 3143.19
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (**Google Gemini 3.6 Flash**).
- **Tổng số Test Cases đã chạy thành công:** **5 / 5** test cases (TC01 $\rightarrow$ TC05 bao phủ đầy đủ Direct Query, Single Tool, Booking, Multi-step ReAct và Edge Case).
- **Số lượt gọi Tool qua MCP Server chính xác:** **5** lượt gọi qua MCP Server JSON-RPC (TC02: 1, TC03: 1, TC04: 2, TC05: 1).
- **Kết quả đẩy Repo nộp bài:** [x] Đã Commit toàn bộ mã nguồn sạch sẽ, sẵn sàng Push lên GitHub cá nhân (`K4-DAY03-ChuVanNhan-2A202602668`).

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!

