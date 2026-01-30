# 📸 PHOTOBOOTH MASTER - PHIÊN BẢN MODULAR V2.0

Chào mừng bạn đến với hệ thống Photobooth chuyên nghiệp nhất. Phiên bản này đã được tái cấu trúc hoàn toàn (Refactored) giúp bạn dễ dàng quản lý, tùy chỉnh giao diện và mở rộng tính năng.

---

## �️ QUY TRÌNH THIẾT LẬP (3 BƯỚC)

Để ứng dụng vận hành hoàn hảo, hãy thực hiện theo đúng thứ tự sau:

### Bước 1: Cài đặt môi trường
Đảm bảo máy tính đã cài đặt Python và các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

### Bước 2: Cấu hình quản trị (`setup_admin.py`)
Trước khi chạy máy, bạn cần khai báo các thông tin về ngân hàng và dịch vụ đi kèm.
1. Chạy lệnh: `python setup_admin.py`
2. **Khai báo Gói giá:** Nhập giá tiền cho gói 2 ảnh và 4 ảnh.
3. **Khai báo Ngân hàng:** Chọn ngân hàng từ danh sách thả xuống (Dropdown) và nhập số tài khoản.
4. **Nhập API Keys:** 
   - **Casso:** Để máy tự động nhận diện tiền về tài khoản.
   - **Cloudinary:** Để tự động upload ảnh lên mạng sau khi chụp.
5. Bấm **Lưu cấu hình**. Mọi thông tin sẽ được chuẩn hóa vào file `config.json`.

### Bước 3: Tinh chỉnh khung ảnh (`frame_editor.py`)
Đây là công cụ giúp bạn thiết kế "bì" và "lưới" ảnh một cách trực quan (Real-time).
1. Chạy lệnh: `python frame_editor.py`
2. **Chọn kiểu lưới:** (1x2, 2x1, 2x2, 4x1) ở thanh phía trên.
3. **Kéo thanh trượt:** Ở bên trái để chỉnh độ dày bì (Padding), khoảng cách ảnh (Gap).
4. **Copy Code:** Khi đã ưng ý, copy đoạn mã ở ô "CODE DỰ KIẾN".
5. **Dán vào file:** Mở `frame_config.py` và dán đè dữ liệu mới vào kiểu lưới tương ứng.

---

## � VẬN HÀNH ỨNG DỤNG

Tùy vào nhu cầu sử dụng, bạn có 2 lựa chọn để khởi động hệ thống chính:

### 1. Chế độ Kinh doanh (`main.py`)
Dành cho việc kinh doanh thu phí tự động.
- **Quy trình:** Chào mừng -> Chọn lưới & giá -> Quét mã QR thanh toán -> Chờ xác nhận tiền từ Casso -> Chụp ảnh.
- **Chạy lệnh:** `python main.py`

### 2. Chế độ Sự kiện / Miễn phí (`main_free.py`)
Dành cho tiệc cưới, sinh nhật hoặc chạy demo test máy.
- **Quy trình:** Chào mừng -> Chọn lưới -> Chụp ảnh ngay (Bỏ qua bước quét mã QR).
- **Chạy lệnh:** `python main_free.py`

---

## 📁 CẤU TRÚC HỆ THỐNG MỚI

Dự án được tách ra thành các module chuyên biệt:

### 🧠 Bộ não và Điều khiển
- **`main_app.py`**: Trái tim của hệ thống. Nơi điều phối các module con và quản lý quy trình (Workflow).
- **`configs.py`**: Chứa các hằng số hệ thống và hàm load dữ liệu từ `config.json`.

### �️ Bộ công cụ hỗ trợ
- **`utils.py`**: Xử lý logic thô (cắt ảnh về tỷ lệ 3:2, tạo mã QR, kiểm tra máy in).
- **`workers.py`**: Các công nhân chạy ngầm (Upload ảnh lên Cloud, check tiền từ Casso) giúp phần mềm không bị giật lag.
- **`ui_components.py`**: Bản thiết kế giao diện (Màn hình carousel ảnh mẫu, hộp thoại quét mã tải ảnh).

### 🎨 Quản lý khung (Layouts)
- **`frame_config.py`**: Nơi lưu trữ các con số về padding, gap, canvas size.
- **`frame_editor.py`**: Công cụ chỉnh sửa khung trực quan bằng thanh trượt.

---

## 💡 LƯU Ý KHI THAY ĐỔI CODE

Hệ thống được thiết kế theo nguyên tắc "Tách biệt mối quan tâm":

1. **Muốn đổi logic cắt ảnh?** Hãy sửa `utils.py`. `main_app` sẽ tự động gọi logic mới.
2. **Muốn đổi ngân hàng?** Dùng `setup_admin.py`. Không cần chạm vào code.
3. **Muốn đổi màu sắc/font chữ?** Hãy tìm stylesheet trong `main_app.py`.
4. **Muốn đổi khung nền trang trí?** Hãy thay các file PNG trong thư mục `templates/`.

---

## � HỖ TRỢ & BẢO TRÌ

- Nếu gặp lỗi **ImportError**: Hãy kiểm tra lại bạn đã cài đủ thư viện trong `requirements.txt` chưa.
- Nếu **Camera không lên**: Kiểm tra `CAMERA_INDEX` trong `configs.py` (thường là 0 hoặc 1).
- Nếu **Không nhận tiền**: Kiểm tra lại Casso API Key trong `setup_admin.py`.

---
*Phiên bản được tối ưu hóa cho trải nghiệm người dùng và lập trình viên.*
