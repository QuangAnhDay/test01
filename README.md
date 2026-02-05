# PHOTOBOOTH MASTER - PHIÊN BẢN MODULAR V2.0

Chào mừng bạn đến với hệ thống Photobooth chuyên nghiệp nhất. Phiên bản này đã được tái cấu trúc hoàn toàn (Refactored) giúp bạn dễ dàng quản lý, tùy chỉnh giao diện và mở rộng tính năng.

---

## QUY TRÌNH THIẾT LẬP (4 BƯỚC)

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

### Bước 3: Thiết lập Camera (`setup_camera.py`)
Công cụ giúp bạn chọn và cấu hình camera phù hợp.
1. Chạy lệnh: `python setup_camera.py`
2. Chọn camera từ danh sách (Laptop webcam, Iriun, HDMI capture, ...)
3. Điều chỉnh độ phân giải (1280x720 khuyến nghị)
4. Bấm **Lưu** để lưu cài đặt vào `camera_settings.json`

### Bước 4: Tinh chỉnh khung ảnh (Tùy chọn)
Sử dụng Frame Editor để thiết kế khung ảnh tùy chỉnh.
1. Chọn kiểu lưới: (1x2, 2x1, 2x2, 4x1)
2. Kéo thanh trượt để chỉnh độ dày bì (Padding), khoảng cách ảnh (Gap)
3. Lưu layout custom để sử dụng

---

## VẬN HÀNH ỨNG DỤNG

Tùy vào nhu cầu sử dụng, bạn có 2 lựa chọn để khởi động hệ thống chính:

### 1. Chế độ Kinh doanh (`main_app.py`)
Dành cho việc kinh doanh thu phí tự động.
- **Quy trình:** Chào mừng -> Chọn lưới & giá -> Quét mã QR thanh toán -> Chờ xác nhận tiền từ Casso -> Chụp ảnh.
- **Chạy lệnh:** `python main_app.py`

### 2. Chế độ Sự kiện / Miễn phí (`main_free.py`)
Dành cho tiệc cưới, sinh nhật hoặc chạy demo test máy.
- **Quy trình:** Chào mừng -> Chọn lưới -> Chụp ảnh ngay (Bỏ qua bước quét mã QR).
- **Chạy lệnh:** `python main_free.py`

---

## CẤU TRÚC HỆ THỐNG MỚI (MODULAR)

Dự án được tách ra thành các module chuyên biệt:

```
photobooth2/
├── main_app.py              # Entry point chế độ kinh doanh
├── main_free.py             # Entry point chế độ miễn phí
├── setup_admin.py           # Công cụ cấu hình admin
├── setup_camera.py          # Công cụ thiết lập camera
│
├── config/                  # Cấu hình hệ thống
│   ├── settings.py          # Hằng số, load config.json
│   └── frame_config.py      # Cấu hình khung ảnh & layouts
│
├── modules/                 # Logic xử lý
│   └── utils.py             # Hàm tiện ích (cắt ảnh, QR, printer)
│
├── ui/                      # Giao diện người dùng
│   ├── ui_main.py           # Giao diện chính PhotoboothApp
│   └── ui_components.py     # Components (Carousel, Dialog, ...)
│
├── workers/                 # Xử lý ngầm (Background)
│   └── background_workers.py # Upload Cloud, Check Casso
│
├── templates/               # Khung ảnh PNG
├── sample_photos/           # Ảnh mẫu cho carousel
├── output/                  # Ảnh đầu ra
│
├── config.json              # File cấu hình (tự động tạo)
├── camera_settings.json     # Cài đặt camera (tự động tạo)
└── requirements.txt         # Thư viện Python cần thiết
```

---

## CHI TIẾT CÁC MODULE

### config/ - Cấu hình
- **`settings.py`**: Chứa các hằng số hệ thống và hàm load dữ liệu từ `config.json`
- **`frame_config.py`**: Lưu trữ các con số về padding, gap, canvas size cho từng layout

### modules/ - Xử lý logic
- **`utils.py`**: Xử lý logic thô (cắt ảnh về tỷ lệ 3:2, tạo mã QR, kiểm tra máy in)

### ui/ - Giao diện
- **`ui_main.py`**: Class PhotoboothApp chính, quản lý các màn hình
- **`ui_components.py`**: Bản thiết kế giao diện (Carousel ảnh mẫu, hộp thoại QR)

### workers/ - Xử lý ngầm
- **`background_workers.py`**: Các thread chạy ngầm (Upload Cloudinary, Check Casso)

---

## LƯU Ý KHI THAY ĐỔI CODE

Hệ thống được thiết kế theo nguyên tắc "Tách biệt mối quan tâm":

1. **Muốn đổi logic cắt ảnh?** Sửa `modules/utils.py`
2. **Muốn đổi ngân hàng/giá?** Dùng `setup_admin.py` hoặc sửa `config.json`
3. **Muốn đổi camera?** Dùng `setup_camera.py`
4. **Muốn đổi màu sắc/font chữ?** Sửa stylesheet trong `ui/ui_main.py`
5. **Muốn đổi khung nền?** Thay các file PNG trong thư mục `templates/`
6. **Muốn thêm layout mới?** Sửa `config/frame_config.py`

---

## HỖ TRỢ & XỬ LÝ LỖI

| Lỗi | Giải pháp |
|-----|-----------|
| **ImportError** | Kiểm tra đã cài đủ thư viện: `pip install -r requirements.txt` |
| **Camera không lên** | Chạy `python setup_camera.py` để chọn đúng camera |
| **Không nhận tiền** | Kiểm tra Casso API Key trong `setup_admin.py` |
| **Ảnh không upload** | Kiểm tra Cloudinary API trong `setup_admin.py` |
| **Lỗi encoding terminal** | Đã được xử lý trong phiên bản mới |

---

## CHANGELOG V2.0

- **Tái cấu trúc mô-đun**: Tách code thành các module chuyên biệt
- **Camera Setup**: Thêm công cụ `setup_camera.py` để chọn camera dễ dàng
- **Custom Layouts**: Hỗ trợ tạo và lưu layout tùy chỉnh
- **Free Mode cải tiến**: Ghi video trong quá trình chụp
- **Sửa lỗi encoding**: Không còn lỗi Unicode trên Windows terminal

---

*Phiên bản được tối ưu hóa cho trải nghiệm người dùng và lập trình viên.*
