# 📜 QUY ƯỚC LÀM VIỆC CHUNG (QUYUOC)

File này là **Nguồn Sự Thật Duy Nhất** (Single Source of Truth) dành cho AI khi thực hiện dự án này. AI phải luôn đọc lại file này khi bắt đầu phiên làm việc mới.

---

## 📌 1. QUY ƯỚC LÀM VIỆC CỐ ĐỊNH (MANDATORY)
*   **Đọc và Ghi nhớ:** AI phải luôn đọc file này khi bắt đầu phiên làm việc mới để nắm bắt lịch sử và không lặp lại lỗi cũ.
*   **Cập nhật bắt buộc (Crucial):** AI phải tự động cập nhật file này (`HUONGDAN/QUYUOC.md`) ngay lập tức khi phát sinh bất kỳ quy ước mới, thay đổi thiết kế, hoặc logic hệ thống nào. Đây là "Bộ não ngoài" của dự án.
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

### 📄 Xuất PDF (ReportLab)
*   **Sidebar Bleed:** Đặt lề doc bằng 0, dùng `canvas.rect` cho sidebar.
*   **Spacing:** Name `spaceAfter=18`, Contact `spaceAfter=30` để tránh dính chữ.
*   **Headers:** Sử dụng `HRFlowable` để tạo các đường kẻ phân cách section mượt mà.

### ⚙️ Logic Hệ thống
*   **Time Tracking:** Cập nhật `created_at` trong route `save_cv` theo giờ Việt Nam.
*   **Template Mapping:** Cũ-Mới (`minimalist` -> `white`, `contemporary` -> `blue`).

---
*Cập nhật lần cuối: 15/04/2026*
