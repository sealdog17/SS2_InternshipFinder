# 📜 QUY ƯỚC LÀM VIỆC CHUNG (QUYUOC)

File này là **Nguồn Sự Thật Duy Nhất** (Single Source of Truth) dành cho AI khi thực hiện dự án này. AI phải luôn đọc lại file này khi bắt đầu phiên làm việc mới.

---

## 📌 1. QUY ƯỚC LÀM VIỆC CỐ ĐỊNH (MANDATORY)
*   **Đọc và Ghi nhớ:** AI phải luôn đọc file này khi bắt đầu phiên làm việc mới để nắm bắt lịch sử và không lặp lại lỗi cũ.
*   **Cập nhật bắt buộc (Crucial):** AI phải tự động cập nhật file này (`HUONGDAN/QUYUOC.md`) ngay lập tức khi phát sinh bất kỳ quy ước mới, thay đổi thiết kế, hoặc logic hệ thống nào. Đây là "Bộ não ngoài" của dự án.
*   **Quy ước DB:** Không commit file SQLite (`instance/jobfinder.db`) lên repository. Thêm `instance/` hoặc `*.db` vào `.gitignore`. Cung cấp script seed (ví dụ `scratch/seed_demo_data.py`) để tạo DB và dữ liệu mẫu khi clone dự án mới.
*   **Tự động triển khai:** Bỏ qua bước tạo Kế hoạch (Implementation Plan) và xin phép. Thực thi ngay lập tức khi được giao việc.
*   **Ngôn ngữ:** Giao tiếp ngắn gọn, trực tiếp bằng tiếng Việt.
*   **Lưu trữ:** Không tạo file rác ở thư mục gốc. Sử dụng `scratch/` cho file nháp.
*   **Git:** Chỉ thực hiện `pull` và `push` trên nhánh `master` của repository [InternshipFinder](https://github.com/sealdog17/SS2_InternshipFinder).

---

## 🎨 2. TIÊU CHUẨN THIẾT KẾ & TEMPLATES
Luôn đảm bảo sự đồng bộ **Pixel-Perfect** giữa: Trình duyệt, Xem toàn màn hình và File PDF.

### A. Mẫu BLUE (Contemporary)
*   **Bố cục:** 2 cột (Sidebar trái ~36% width).
*   **Màu sắc:** Sidebar `#1964d3`, Font Times New Roman.
*   **PDF:** Vẽ sidebar tràn viền (Zero margins) từ `y=0` đến `y=842`. Headers có vạch phân cách chuyên nghiệp.

### B. Mẫu WHITE (Modern Centered)
*   **Bố cục:** Căn giữa hoàn toàn.
*   **Typography:**
    *   Tên: Uppercase, 22pt, letter-spacing 4px.
    *   Liên hệ: Dạng ngang, cách bởi dấu (•), 8.5pt.
*   **Divider:** Đường kẻ đen 1.5pt dưới thông tin liên hệ.
*   **Khoảng cách:** Nhiều padding/margin để tạo sự tinh tế (Airy spacing).

---

## 🛠 3. CÁC GIẢI PHÁP KỸ THUẬT QUAN TRỌNG (FIXES LOG)

### 🖥 Giao diện
*   **Fullscreen Scroll:** Sử dụng `flex-direction: column` và `align-items: center` để tránh lỗi kẹt cuộn khi dùng `justify-content: center`.
*   **Times New Roman:** Font này phải được đăng ký trong ReportLab từ `/static/fonts/` để hỗ trợ tiếng Việt sắc nét.

### 📄 Xuất File (PDF & PNG)
*   **Sidebar Bleed:** Đặt lề doc bằng 0, dùng `canvas.rect` cho sidebar.
*   **Spacing:** Name `spaceAfter=18`, Contact `spaceAfter=30` để tránh dính chữ.
*   **Headers:** Sử dụng `HRFlowable` để tạo các đường kẻ phân cách section mượt mà.
*   **Export PNG:** Sử dụng thư viện `html2canvas` với `scale: 2` để cho phép người dùng tải CV dưới dạng ảnh chất lượng cao.

### ⚙️ Logic Hệ thống
*   **Time Tracking:** Cập nhật `created_at` trong route `save_cv` theo giờ Việt Nam.
*   **Template Mapping:** Cũ-Mới (`minimalist` -> `white`, `contemporary` -> `blue`).
*   **AI Match Profile:** Dashboard và Job Detail sử dụng logic tính toán match % dựa trên `session['user_skills']` và `job.required_skills`.
*   **AI Optimizer (CV Builder):** Nút "AI Optimize" trực tiếp tại trường Bio/Experience giúp chuyên nghiệp hóa nội dung ngay lập tức.
*   **Navigation:** Thống nhất "Resources" -> "Settings" trên toàn hệ thống. Avatar tài khoản (top-right) luôn dẫn đến trang Settings.
*   **URL Persistence (F5 Proof):**
    *   Sử dụng URL Hash (ví dụ `#step-1`, `#view-inbox`) cho các thành phần điều hướng client-side (Tabs, Wizards).
    *   Sử dụng Query Parameters (ví dụ `?cv_id=5`) để định danh dữ liệu đang được xử lý.
    *   Luôn kiểm tra và phục hồi trạng thái từ URL trong sự kiện `DOMContentLoaded` và `hashchange`.

### 💼 Client Work Structure
*   **Layout:** Sử dụng Local Sidebar (Home, My Jobs, Inbox).
*   **Home:** Chứa Workspace Overview và thẻ quản lý Availability.
*   **My Jobs:** Danh sách công việc với thanh trạng thái màu bên trái (Upcoming: Gray, In Progress: Blue, Done: Green).
*   **Inbox:** Giao diện chat 2 cột đồng bộ với thiết kế đã thống nhất.
*   **Saved Opportunities:** 
    *   Mặc định hiển thị tối đa 2 thẻ công việc gần nhất.
    *   Sử dụng nút "View all" (không kèm số lượng) để mở rộng toàn bộ danh sách.
    *   Hủy lưu trực tiếp trên thẻ bằng AJAX và xóa phần tử khỏi DOM kèm hiệu ứng (opacity/scale).

### 🖼️ Visual Consistency (Đồng bộ thị giác)
*   **Job Images:** Mỗi Job bắt buộc có trường `cover_image` trong DB. Cấm sử dụng chọn ảnh ngẫu nhiên (random) trong Template để đảm bảo một Job luôn hiển thị cùng một ảnh ở mọi trang (Dashboard, Saved list).
*   **Saved Jobs:** Lưu trữ qua bảng trung gian `saved_jobs`. Trạng thái lưu (Bookmark icon) phải được đồng bộ Real-time giữa Dashboard và Client Work.

### 🔐 Privacy & Security (Quyền riêng tư & Bảo mật)
*   **Image Storage (Base64):** Cấm lưu trữ ảnh cá nhân (Avatar, CV photo) trực tiếp vào thư mục công khai (`static/uploads`). Toàn bộ ảnh phải được chuyển sang dạng chuỗi **Base64** và lưu trực tiếp vào Database (SQLite). Điều này đảm bảo quyền riêng tư trên môi trường Localhost và tránh việc truy cập trái phép qua URL file.
*   **Ownership Verification (IDOR Protection):** Tất cả các route tải hoặc thao tác với dữ liệu nhạy cảm (CV, Profile) phải bắt buộc kiểm tra quyền sở hữu bằng cách lọc theo `user_id` từ `session` (Ví dụ: `filter_by(id=cv_id, user_id=session['user_id'])`). Không được phép tin tưởng tuyệt đối vào ID truyền từ Client mà không có bước xác thực này.

---
*Cập nhật lần cuối: 22/04/2026 (với Security & Privacy Update)*

