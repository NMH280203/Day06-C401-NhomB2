# SPEC Sản phẩm - FoodChat AI

Bản tài liệu đặc tả sản phẩm (SPEC) này được hoàn thiện dựa trên khảo sát thực tế (Evidence Pack) và cấu trúc triển khai thực tế của dự án FoodChat AI (nhóm B2 - Track Food / Super-app).

---

## 1. Bằng chứng (Evidence Pack)

Quyết định sản phẩm của nhóm không dựa trên phỏng đoán, mà xuất phát từ các quan sát thực tế sau:

### Trải nghiệm trực tiếp (Self-use)
* **Quan sát 1 (Intent trước, quán sau):** Khi người dùng muốn tìm đồ "healthy" hoặc "ăn nhẹ", việc tìm kiếm từ khóa trên GrabFood thường trả về danh sách các quán ăn ngẫu nhiên với mức giá lệch ngân sách, thay vì lọc ra món ăn phù hợp với cảm giác bữa ăn trước. Người dùng nghĩ về **Món ăn/Cảm giác ăn trước**, sau đó mới chọn **Quán**.
* **Quan sát 2 (Định vị linh hoạt):** Khi người dùng nói "ăn gần công ty" hoặc "ăn gần Bitexco", họ kỳ vọng hệ thống hiểu địa danh bằng text thay vì bắt buộc phải kích hoạt GPS thiết bị.

### Nguồn đánh giá bên ngoài (Social & Review Evidence)
* **Quote 1 (Sự lưỡng lự - Choice Paralysis):** *"Không biết ăn gì, mở app xem mãi không quyết được."* (Nguồn: Threads [_nhwqynf](https://www.threads.com/@_nhwqynf/post/DZHo21vAX1a) và [lucif.th](https://www.threads.com/@lucif.th/post/DXZSBkVkTCB)).
* **Quote 2 (Lọc sai ngữ cảnh):** *"Tìm healthy toàn món đắt / không đúng ý."* (Nguồn: Đánh giá GrabFood công khai).
* **Quote 3 (Vi phạm chế độ ăn):** *"Gợi ý không đúng ăn chay / dị ứng."* (Nguồn: Phản hồi nhóm ăn chay trên mạng xã hội).
* **Quote 4 (Nhu cầu về địa điểm):** *"Gần X"* là một phần tự nhiên trong câu chat của người dùng (Nguồn: Threads [riwhiunyyyy](https://www.threads.com/@riwhiunyyyy/post/DWQPEiDEYlV)).
* **Hình ảnh chứng minh:** Bằng chứng thực tế về luồng chọn món rồi mới tới quán đã được lưu giữ tại [bangChungMonToQuan.jpg](file:///d:/user/Desktop/Github/Day06-C401-NhomB2/spec/02/bangChungMonToQuan.jpg).

### Khảo sát đối thủ và các mô hình tương tự
* **GrabFood / ShopeeFood:** Rất mạnh về gợi ý theo lịch sử đơn cũ (repeat order), nhưng yếu trong việc nhận diện **intent của buổi ăn hiện tại** (mood, budget đột xuất).
* **Chatbot thông thường (ChatGPT/Claude):** Khả năng hiểu ngôn ngữ tự nhiên tốt nhưng dễ bị **hallucination (ảo tưởng)** về giá cả và sự tồn tại của quán ăn nếu không liên kết với catalog thực tế.
* **Spotify (Mô hình tương tự):** Gợi ý nhạc theo tâm trạng/mood thay vì chỉ tìm theo tên ca sĩ. Chúng tôi áp dụng triết lý này: **Ngữ cảnh bữa ăn (mood, budget, dietary) sẽ dẫn dắt việc khám phá món ăn**.

---

## 2. Lát cắt để build (Build Slice)

> **Lát cắt kiểm thử:** Đối với người dùng văn phòng hay đặt đồ ăn thường xuyên (22–40 tuổi, đặt ăn ≥ 2 lần/tuần), khi họ mô tả nhu cầu bữa ăn bằng ngôn ngữ tự nhiên (ví dụ: *"Trưa 1 người 50k không cay"*), hệ thống API (SSE) sẽ trích xuất ngữ cảnh, đề xuất 2 món ăn thích hợp trước kèm lý do cụ thể, và sau khi người dùng chọn món, AI sẽ tiếp tục gợi ý 2 quán ăn gần đó đáp ứng đúng tiêu chuẩn.

---

## 3. AI Product Canvas

| Ô Canvas | Câu hỏi & Giải pháp thực tế |
|---|---|
| **Value (Giá trị)** | **Dành cho:** Người đặt đồ ăn văn phòng bận rộn hay gặp hội chứng "không biết ăn gì".<br>**Nỗi đau:** App hiện tại ép search bằng từ khóa khô khan, trả ra quán ngẫu nhiên gây ngợp.<br>**AI giải quyết:** Hiểu ngôn ngữ tự nhiên về mood/budget/dietary để gợi ý đúng thứ tự: **Món trước ➔ Quán sau**. |
| **Trust (Niềm tin)** | **Cách nhận biết lỗi:** AI hiển thị rõ phần Context trích xuất được (ngân sách, yêu cầu ăn chay...) ngay trên giao diện trước khi đưa ra món.<br>**Cách sửa đổi:** Người dùng sửa trực tiếp context bằng nút bấm hoặc chat điều chỉnh (correction). Prototype có cảnh báo miễn trừ trách nhiệm (disclaimer) và **không tự động đặt hàng (no auto-order)**. |
| **Feasibility (Khả thi)** | **Chi phí & Độ trễ:** LLM chỉ làm nhiệm vụ trích xuất context & sinh text summary ngắn, dữ liệu món ăn được lấy từ catalog tĩnh và quán ăn từ OpenStreetMap (Overpass API) hoàn toàn miễn phí. Độ trễ thấp nhờ stream Server-Sent Events (SSE) từng chữ.<br>**Rủi ro lớn nhất:** LLM bị mất kết nối API key ➔ Có cơ chế fallback tự động chọn món/quán tĩnh. |
| **Tín hiệu học** | **Đầu vào học máy:** Khi người dùng click chọn món ăn nào hoặc gõ sửa lại context (ví dụ: *"không ăn bún chả đâu"*), dữ liệu này được ghi vào file log.<br>**Tác dụng:** Giúp phân tích tỉ lệ chuyển đổi (món được chọn nhiều) và cải tiến trọng số xếp hạng của `rank_restaurants` trong tương lai. |

---

## 4. Tăng năng lực hay tự động hóa (Augmentation vs Automation)

* **Quyết định:** **Augmentation (Tăng năng lực quyết định cho con người)**.
* **Lý do:**
  1. Yêu cầu về dietary (ăn chay, dị ứng thực phẩm) ảnh hưởng trực tiếp đến sức khỏe của người dùng, nếu AI tự động đặt hàng mà sai sót sẽ gây hậu quả nghiêm trọng.
  2. Mọi quyết định chi tiêu tiền bạc cần có sự phê duyệt cuối cùng của con người.
* **Quy trình tương tác:** AI chỉ đóng vai trò trợ lý tổng hợp thông tin, lọc quán, tính điểm. Người dùng đóng vai trò **Decider (Quyết định chọn món/quán)** và **Corrector (Chỉnh sửa thông tin nếu AI trích xuất thiếu)**.

---

## 5. Bốn đường đi của trải nghiệm

| Đường đi | Kịch bản chi tiết trong Prototype | Ngữ cảnh kiểm thử |
|---|---|---|
| **Đường thuận (Happy)** | Người dùng nhập đủ thông tin ➔ Trả ra thẻ `context` xác nhận ➔ Đề xuất 2 món ➔ User click chọn món ➔ Trả tiếp 2 quán tương ứng kèm bản đồ vị trí. | **C1** (Trưa 1 người 50k không cay) hoặc **C2** (Healthy ~60k) |
| **Khi AI không chắc** | User nhập chung chung: *"Ăn gì ngon"* ➔ Hệ thống phát hiện thiếu thông tin cốt lõi (địa điểm, budget) ➔ Kích hoạt event `ask_context` hỏi lại thân thiện. | **C11** (Ăn gì ngon) |
| **Khi AI sai** | Gợi ý nhầm món mặn khi yêu cầu chay ➔ Hệ thống áp dụng bộ lọc rule-based cứng dựa trên tags của file `dishes.json` để chặn lỗi của LLM; cho phép user gõ *"đổi món khác"* để chạy lại. | **C10** (Ăn chay 50k) |
| **Khi người dùng sửa** | User gõ bổ sung: *"Không lấy quán xa"* hoặc sửa ngân sách trên giao diện ➔ Gọi lại API cập nhật `UserContext` ➔ Tạo gợi ý mới. | **C3** + tin nhắn điều chỉnh |

---

## 6. Những kiểu lỗi đáng lo nhất

### Lỗi 1: Bỏ sót hoặc nhận diện sai yêu cầu ăn chay / dị ứng thực phẩm (Dietary Failure)
* **Tình huống xảy ra:** Người dùng nhập yêu cầu dị ứng bằng ngôn ngữ địa phương hoặc từ lóng (vd: *"không hành tỏi"*, *"chay"* viết tắt) làm LLM không phân tách được vào trường `allergies`/`dietary`.
* **Ảnh hưởng:** Người dùng có thể gặp sự cố sức khỏe hoặc vi phạm quy tắc tôn giáo/sở thích ăn uống.
* **Giải pháp trong Prototype:** Sử dụng prompt chỉ dẫn nghiêm ngặt cho LLM trích xuất intent; áp dụng bộ lọc từ khóa tĩnh cứng (hard-coded filter) trên file danh mục món ăn `be/data/dishes.json`; luôn hiển thị cảnh báo từ chối trách nhiệm yêu cầu người dùng kiểm tra kỹ thực đơn của quán trước khi đặt.

### Lỗi 2: Sai lệch vị trí tìm kiếm quán ăn (Wrong Proximity)
* **Tình huống xảy ra:** Người dùng nhập địa danh chung chung (vd: *"đường Nguyễn Huệ"*) nhưng hệ thống tìm kiếm ở thành phố khác hoặc định vị sai tọa độ do API Overpass trả về kết quả nhiễu.
* **Ảnh hưởng:** Phí giao hàng cực cao hoặc quán ăn không hỗ trợ khu vực thực tế của user.
* **Giải pháp trong Prototype:** Hiển thị rõ tọa độ/địa chỉ đã resolve ở góc màn hình; nếu địa điểm mơ hồ sẽ gọi tool `ask_user_for_context` yêu cầu làm rõ Quận/Thành phố.

---

## 7. Kế hoạch kiểm thử và bằng chứng demo

Hệ thống sẽ được kiểm tra với 3 kịch bản đầu vào:

1. **Đầu vào thuận lợi (Happy Path - C1):**
   * *Input:* `"Trưa nay ăn cơm tấm tầm 60k ở Quận 1"`
   * *Kỳ vọng:* Nhận diện bữa trưa, ngân sách 60.000đ, món cơm tấm, địa điểm Quận 1. Đề xuất đúng món cơm sườn và các quán cơm tấm ngon tại Q1.
2. **Đầu vào mơ hồ (Low-confidence - C11):**
   * *Input:* `"Trưa nay ăn gì"`
   * *Kỳ vọng:* Hệ thống không tự ý đoán mò mà phản hồi yêu cầu làm rõ vị trí và ngân sách dự kiến.
3. **Đầu vào chứa lỗi lọc (Failure Test - C10):**
   * *Input:* `"Tìm món chay dưới 40k ở Hoàn Kiếm"`
   * *Kỳ vọng:* Đảm bảo tuyệt đối không gợi ý bất kỳ món mặn nào (ví dụ: bún chả, cơm sườn) dù giá có rẻ đến mấy.

---

## 8. Phân công nhiệm vụ (Team Assignment)

Hệ thống được xây dựng đồng bộ bởi các thành viên nhóm B2 với sự phân nhiệm cụ thể:

* **Nguyễn Đăng Khương (2A202600584):** Nghiên cứu thị trường, thu thập dữ liệu bằng chứng thực tế từ người dùng (`evidence-pack`).
* **Mai Đức Vinh (2A202600587):** Thiết kế tài liệu đặc tả sản phẩm (SPEC) và xây dựng hệ thống prompts cho LLM (`be/prompt/`).
* **Nguyễn Mạnh Hiếu (2A202600887):** Thiết lập kiến trúc Orchestrator (`orchestrator.py`), hệ thống Router FastAPI, Executor và tích hợp Restaurant Agent.
* **Trần Duy Khánh (2A202600592):** Phát triển Food Agent, thuật toán tìm kiếm món ăn (`food_search.py`) và cơ sở dữ liệu `data/dishes.json`.
* **Tống Anh Huy (2A202600761):** Viết kịch bản demo chi tiết và tài liệu hướng dẫn vận hành mã nguồn.
