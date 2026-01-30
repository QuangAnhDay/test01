# 📚 TÁC DỤNG CỦA TỪNG FILE

## 🎯 HƯỚNG DẪN ĐỌC

- 🟢 **File Python** - Code chương trình
- 🔵 **File Markdown** - Tài liệu hướng dẫn
- 🟡 **File JSON** - Cấu hình
- 🟣 **File TXT** - Danh sách dependencies

---

## 🟢 CÁC FILE PYTHON (Code)

### 1. **`main.py`** 🚀
**Tác dụng:** File khởi động chính của ứng dụng (Entry Point)

**Chức năng:**
- Tạo QApplication (PyQt5)
- Kiểm tra file `config.json` có tồn tại không
- Gọi hàm `load_config()` để load cấu hình
- Khởi tạo và hiển thị cửa sổ `PhotoboothApp`
- Chạy event loop của ứng dụng

**Khi nào dùng:**
- Chạy app: `python main.py`
- Đây là file bạn chạy đầu tiên!

**Code chính:**
```python
from main_app import PhotoboothApp
app = QApplication(sys.argv)
window = PhotoboothApp()
window.show()
app.exec_()
```

---

### 2. **`configs.py`** ⚙️
**Tác dụng:** Quản lý tất cả cấu hình toàn cục

**Chứa:**
- Các hằng số: `WINDOW_WIDTH`, `WINDOW_HEIGHT`, `CAMERA_INDEX`
- Đường dẫn thư mục: `TEMPLATE_DIR`, `OUTPUT_DIR`, `SAMPLE_PHOTOS_DIR`
- Biến toàn cục: `APP_CONFIG` (dict chứa config từ JSON)

**Các hàm quan trọng:**
- `load_config()` - Đọc file `config.json`
- `get_price_2()` - Lấy giá gói 2 ảnh
- `get_price_4()` - Lấy giá gói 4 ảnh
- `format_price(amount)` - Format số tiền thành VNĐ
- `generate_unique_code()` - Tạo mã giao dịch (PB1234)
- `generate_vietqr_url()` - Tạo URL QR thanh toán

**Khi nào sửa:**
- Muốn thay đổi kích thước cửa sổ
- Muốn đổi camera index
- Muốn thêm cấu hình mới

---

### 3. **`utils.py`** 🛠️
**Tác dụng:** Chứa các hàm tiện ích xử lý ảnh và hệ thống

**Nhóm 1: Quản lý thư mục**
- `ensure_directories()` - Tạo thư mục nếu chưa có
- `create_sample_templates()` - Tạo khung ảnh mẫu
- `create_sample_photos()` - Tạo ảnh demo
- `load_sample_photos()` - Load ảnh từ thư mục

**Nhóm 2: Xử lý ảnh**
- `generate_qr_code(content)` - Tạo mã QR
- `overlay_images(bg, fg)` - Ghép ảnh có alpha lên background
- `convert_cv_qt(cv_img)` - Chuyển ảnh OpenCV → QPixmap
- `crop_to_aspect(img, ratio)` - Cắt ảnh theo tỷ lệ 3:2

**Nhóm 3: Hệ thống**
- `check_printer_available()` - Kiểm tra máy in (Windows)

**Khi nào dùng:**
- Cần xử lý ảnh
- Cần tạo QR code
- Cần kiểm tra máy in

---

### 4. **`workers.py`** 🔄
**Tác dụng:** Chứa các QThread xử lý tác vụ nền (không block UI)

**Class 1: `CloudinaryUploadThread`**
- Upload ảnh lên Cloudinary
- Signals: `upload_success(url)`, `upload_error(msg)`
- Chạy trong background thread

**Class 2: `QRImageLoaderThread`**
- Tải ảnh QR từ VietQR API
- Signals: `image_loaded(pixmap)`, `load_error(msg)`
- Tránh UI bị đơ khi tải ảnh

**Class 3: `CassoCheckThread`**
- Kiểm tra giao dịch từ Casso API mỗi 3 giây
- Signals: `payment_received()`, `check_error(msg)`
- Method: `stop()` để dừng thread

**Tại sao cần:**
- Nếu upload/download trong main thread → UI bị đơ
- Thread chạy background → UI vẫn mượt

---

### 5. **`ui_components.py`** 🎨
**Tác dụng:** Chứa các widget giao diện tùy chỉnh

**Class 1: `DownloadQRDialog`**
- Dialog hiển thị QR code để tải ảnh
- Tự động upload ảnh lên Cloudinary
- Hiển thị QR code khi upload xong
- Có nút "Đóng" để thoát

**Class 2: `CarouselPhotoWidget`**
- Widget hiển thị ảnh carousel tự động cuộn
- Cuộn từ trái sang phải liên tục
- Dùng trong màn hình welcome
- Methods: `set_photos(paths)`, `update_scroll()`

**Khi nào sửa:**
- Muốn thay đổi giao diện dialog
- Muốn điều chỉnh tốc độ carousel
- Muốn thêm widget mới

---

### 6. **`main_app.py`** 📱
**Tác dụng:** File chính chứa class `PhotoboothApp` - trái tim của ứng dụng

**Chức năng:**
- Quản lý tất cả màn hình (welcome, price, QR, capture, photo select, etc.)
- Xử lý logic workflow (chụp → chọn → thanh toán → in)
- Quản lý camera
- Xử lý countdown
- Tạo collage ảnh
- Ghép ảnh với khung
- In ảnh
- Upload cloud

**Các màn hình:**
1. Welcome screen - Carousel ảnh
2. Price select - Chọn gói 2 hoặc 4 ảnh
3. QR payment - Hiển thị QR thanh toán
4. Capture - Chụp 10 ảnh
5. Layout select - Chọn kiểu bố cục (1x2, 2x1, 2x2, 4x1)
6. Photo select - Chọn 2 hoặc 4 ảnh
7. Template select - Chọn khung
8. Confirm - Xác nhận và in

**Khi nào sửa:**
- Muốn thêm màn hình mới
- Muốn thay đổi workflow
- Muốn sửa giao diện

---

### 7. **`frame_config.py`** 📏
**Tác dụng:** Cấu hình kích thước và padding cho từng layout

**Chứa 4 layout:**
- `LAYOUT_1x2` - 2 ảnh ngang (1280x720)
- `LAYOUT_2x1` - 2 ảnh dọc (640x900)
- `LAYOUT_2x2` - 4 ảnh lưới (1280x720)
- `LAYOUT_4x1` - 4 ảnh dọc dài (640x1600)

**Mỗi layout có:**
- `CANVAS_W`, `CANVAS_H` - Kích thước canvas
- `PAD_TOP`, `PAD_BOTTOM` - Bì trên/dưới
- `PAD_LEFT`, `PAD_RIGHT` - Bì trái/phải
- `GAP` - Khoảng cách giữa ảnh

**Hàm:**
- `get_layout_config(layout_type)` - Lấy config theo layout

**Khi nào sửa:**
- Muốn thay đổi kích thước khung
- Muốn điều chỉnh padding
- Muốn ảnh gần/xa nhau hơn

---

### 8. **`preview_frame.py`** 👁️
**Tác dụng:** Xem trước khung ảnh với padding từ `frame_config.py`

**Chức năng:**
- Đọc config từ `frame_config.py`
- Tạo ảnh demo cho mỗi layout
- Hiển thị:
  - Màu xanh nhạt = Vùng padding
  - Khung đỏ = Slot (vùng có thể đặt ảnh)
  - Khung trắng = Ảnh 3:2 thực tế
- Tính toán và gợi ý padding tối ưu
- Lưu ảnh vào `preview_frames/`

**Cách dùng:**
```bash
python preview_frame.py
```

**Khi nào chạy:**
- Sau khi sửa `frame_config.py`
- Muốn xem kết quả trước khi áp dụng
- Muốn tối ưu padding

---

## 🔵 CÁC FILE MARKDOWN (Tài liệu)

### 1. **`README.md`** 📖
**Tác dụng:** Tài liệu chính của dự án

**Nội dung:**
- Giới thiệu dự án
- Hướng dẫn cài đặt
- Hướng dẫn chạy
- Cấu trúc dự án
- Tính năng
- Workflow
- Troubleshooting

**Khi nào đọc:**
- Lần đầu tiên làm việc với dự án
- Cần hướng dẫn nhanh

---

### 2. **`COMPLETE.md`** 📋
**Tác dụng:** Tổng quan hoàn chỉnh về refactoring

**Nội dung:**
- Danh sách file đã tạo
- Cấu trúc thư mục
- Thống kê refactoring
- Hướng dẫn sử dụng
- Tips & tricks
- Troubleshooting

**Khi nào đọc:**
- Muốn hiểu toàn bộ dự án
- Cần biết file nào làm gì

---

### 3. **`FRAME_CONFIG_GUIDE.md`** 🎨
**Tác dụng:** Hướng dẫn chi tiết cách điều chỉnh khung ảnh

**Nội dung:**
- Giải thích `frame_config.py`
- Giải thích `preview_frame.py`
- Quy trình điều chỉnh từng bước
- Mẹo điều chỉnh
- Hiểu về tỷ lệ 3:2
- Ví dụ thực tế
- Checklist

**Khi nào đọc:**
- Muốn thay đổi kích thước khung
- Muốn điều chỉnh padding
- Cần tối ưu tỷ lệ 3:2

---

### 4. **`REFACTORING_SUMMARY.md`** 📊
**Tác dụng:** Tóm tắt quá trình refactoring

**Nội dung:**
- Cấu trúc mới
- Chi tiết từng module
- Lợi ích refactoring
- Cách sử dụng
- Import dependencies

**Khi nào đọc:**
- Muốn hiểu tại sao refactor
- Muốn biết module nào chứa gì

---

### 5. **`REFACTORING_GUIDE.md`** 🔧
**Tác dụng:** Hướng dẫn kỹ thuật về refactoring

**Nội dung:**
- Cách refactor chi tiết
- 2 cách thực hiện
- Kiểm tra sau refactor
- Xử lý lỗi import

**Khi nào đọc:**
- Muốn hiểu cách refactor
- Gặp lỗi import
- Muốn refactor thêm

---

### 6. **`CLEAN_STRUCTURE.md`** 🧹
**Tác dụng:** Tổng kết sau khi dọn dẹp file cũ

**Nội dung:**
- Cấu trúc sạch sẽ
- File đã xóa
- Thống kê
- Checklist hoàn thành

**Khi nào đọc:**
- Muốn biết file nào đã xóa
- Kiểm tra cấu trúc hiện tại

---

## 🟡 CÁC FILE JSON (Cấu hình)

### 1. **`config.json`** ⚙️
**Tác dụng:** File cấu hình chính của ứng dụng

**Chứa:**
- `price_2_photos` - Giá gói 2 ảnh
- `price_4_photos` - Giá gói 4 ảnh
- `bank_bin` - Mã ngân hàng
- `bank_account` - Số tài khoản
- `account_name` - Tên tài khoản
- `casso_api_key` - API key Casso
- `cloudinary` - Thông tin Cloudinary
  - `cloud_name`
  - `api_key`
  - `api_secret`

**Khi nào sửa:**
- Thay đổi giá tiền
- Đổi tài khoản ngân hàng
- Cập nhật API key

**⚠️ LƯU Ý:** File này chứa thông tin nhạy cảm, đã được gitignore!

---

### 2. **`config.example.json`** 📝
**Tác dụng:** File mẫu cấu hình (không chứa thông tin thật)

**Chức năng:**
- Hướng dẫn cấu trúc file config
- Dùng để tạo `config.json` mới
- An toàn để commit lên Git

**Cách dùng:**
```bash
copy config.example.json config.json
# Sau đó sửa config.json với thông tin thật
```

---

## 🟣 CÁC FILE TXT

### 1. **`requirements.txt`** 📦
**Tác dụng:** Danh sách các thư viện Python cần cài đặt

**Chứa:**
```
PyQt5
opencv-python
numpy
Pillow
qrcode
requests
cloudinary
```

**Cách dùng:**
```bash
pip install -r requirements.txt
```

**Khi nào sửa:**
- Thêm thư viện mới vào dự án
- Cập nhật phiên bản thư viện

---

### 2. **`.gitignore`** 🚫
**Tác dụng:** Chỉ định file/thư mục không commit lên Git

**Chứa:**
- `config.json` - Bảo mật thông tin
- `__pycache__/` - File cache Python
- `*.pyc` - File compiled Python
- `output/` - Ảnh đầu ra
- `preview_frames/` - Ảnh preview

**Tại sao cần:**
- Bảo vệ thông tin nhạy cảm
- Giảm kích thước repo
- Tránh conflict không cần thiết

---

## 📂 CÁC THƯ MỤC

### 1. **`templates/`** 🖼️
**Tác dụng:** Chứa các khung ảnh template (PNG có alpha)

**Nội dung:**
- `frame_red.png` - Khung đỏ
- `frame_blue.png` - Khung xanh
- Các khung tùy chỉnh khác

**Khi nào thêm:**
- Muốn thêm khung mới
- File phải là PNG với alpha channel

---

### 2. **`sample_photos/`** 📸
**Tác dụng:** Chứa ảnh mẫu để hiển thị trong carousel

**Nội dung:**
- `sample_1.jpg` đến `sample_8.jpg`
- Ảnh demo với gradient màu

**Khi nào thêm:**
- Muốn thêm ảnh mẫu mới
- Thay thế ảnh demo

---

### 3. **`output/`** 💾
**Tác dụng:** Lưu ảnh đầu ra sau khi ghép

**Nội dung:**
- Ảnh đã ghép với khung
- Tên file: `photobooth_YYYYMMDD_HHMMSS.jpg`

**Tự động tạo:** Khi chụp và lưu ảnh

---

### 4. **`preview_frames/`** 👁️
**Tác dụng:** Lưu ảnh preview từ `preview_frame.py`

**Nội dung:**
- `preview_1x2.png`
- `preview_2x1.png`
- `preview_2x2.png`
- `preview_4x1.png`

**Tự động tạo:** Khi chạy `python preview_frame.py`

---

### 5. **`stickers/`** ✨
**Tác dụng:** Chứa sticker trang trí (nếu có)

**Nội dung:**
- Sticker PNG với alpha
- Có thể thêm lên ảnh

---

### 6. **`__pycache__/`** 🗂️
**Tác dụng:** Cache của Python (tự động tạo)

**Nội dung:**
- File `.pyc` compiled
- Tăng tốc độ import

**Không cần quan tâm:** Python tự quản lý

---

### 7. **`.git/`** 📦
**Tác dụng:** Thư mục Git repository

**Nội dung:**
- Lịch sử commit
- Branches
- Remote info

**Không cần sửa:** Git tự quản lý

---

## 🎯 TÓM TẮT NHANH

### Muốn chạy app:
```bash
python main.py
```

### Muốn xem trước khung:
```bash
python preview_frame.py
```

### Muốn sửa giá tiền:
→ Sửa `config.json`

### Muốn đổi kích thước khung:
→ Sửa `frame_config.py` → Chạy `preview_frame.py`

### Muốn thêm khung mới:
→ Thêm PNG vào `templates/`

### Muốn hiểu code:
→ Đọc `COMPLETE.md` → `REFACTORING_SUMMARY.md`

### Muốn sửa giao diện:
→ Sửa `main_app.py` hoặc `ui_components.py`

### Muốn thêm tính năng:
→ Xem module nào phù hợp → Sửa file đó

---

## 📞 HƯỚNG DẪN NHANH

| Muốn làm gì | Sửa file nào |
|-------------|--------------|
| Chạy app | `python main.py` |
| Đổi giá | `config.json` |
| Đổi kích thước khung | `frame_config.py` |
| Xem preview | `python preview_frame.py` |
| Thêm hàm tiện ích | `utils.py` |
| Thêm background task | `workers.py` |
| Thêm widget | `ui_components.py` |
| Sửa workflow | `main_app.py` |
| Đọc hướng dẫn | `README.md`, `COMPLETE.md` |

---

**Tạo ngày:** 2026-01-29  
**Phiên bản:** 2.0 (Refactored)
