# 📸 Photobooth App - Ứng Dụng Chụp Ảnh Tự Động

## 📖 Giới thiệu

Ứng dụng Photobooth dùng cho quầy chụp ảnh tự động, hỗ trợ:
- Chụp ảnh tự động với đếm ngược
- Chọn kiểu bố cục ảnh (1x2, 2x1, 2x2, 4x1, Custom)
- Thanh toán qua QR Code (VietQR + Casso)
- Chọn khung viền/template
- Upload ảnh lên Cloud (Cloudinary)
- Tạo QR để khách tải ảnh về điện thoại
- Quay video quá trình chụp (Free Mode)
- Hệ thống quản trị (Admin Dashboard)

---

## 🏗️ Cấu Trúc Thư Mục

```
photobooth-app/
├── src/
│   ├── admin/                    # 🛠️ Phân hệ quản trị
│   │   ├── api/                  # API calls (placeholder)
│   │   ├── components/           # UI components cho Admin
│   │   │   └── frame_editor.py   # 🎨 Bộ thiết kế khung ảnh
│   │   ├── pages/                # Các trang quản lý
│   │   │   ├── dashboard.py      # Trang chính: Giá, Ngân hàng, API Keys
│   │   │   ├── pricing.py        # Setup giá tiền (→ Dashboard)
│   │   │   ├── templates.py      # Quản lý khung hình (→ Frame Editor)
│   │   │   └── settings.py       # Thiết lập Camera
│   │   └── store/                # State management
│   │       └── admin_state.py    # Load/Save config.json
│   │
│   ├── modules/                  # ⚙️ Core Logic (Nghiệp vụ)
│   │   ├── camera/               # Kết nối, chụp ảnh, quay video
│   │   │   └── camera_manager.py
│   │   ├── printer/              # Lệnh in, driver máy in
│   │   │   └── printer_manager.py
│   │   ├── payment/              # QR Payment, Casso integration
│   │   │   └── payment_service.py
│   │   ├── image_processing/     # Tạo collage, chèn template, filter
│   │   │   └── processor.py
│   │   └── storage/              # Upload Cloudinary, Landing Page
│   │       └── cloud_upload.py
│   │
│   ├── photobooth/               # 📷 Client UI (Luồng chính)
│   │   ├── components/           # Widget dùng chung
│   │   │   ├── carousel.py       # Carousel ảnh trôi ngang
│   │   │   └── dialogs.py        # Dialog QR tải ảnh/video
│   │   ├── hooks/                # Điều khiển luồng
│   │   │   └── flow_controller.py # State machine & transitions
│   │   └── steps/                # 📋 TỪNG BƯỚC CỦA CHƯƠNG TRÌNH
│   │       ├── step_0_idle.py        # Màn hình chờ (Welcome)
│   │       ├── step_1_package.py     # Chọn gói/layout
│   │       ├── step_2_payment.py     # QR thanh toán
│   │       ├── step_3_liveview.py    # Camera đếm ngược
│   │       ├── step_4_capture.py     # Chọn ảnh đã chụp
│   │       ├── step_5_filter.py      # Filter/Sticker (placeholder)
│   │       ├── step_6_template.py    # Chọn khung viền
│   │       ├── step_7_processing.py  # Chờ render (placeholder)
│   │       └── step_8_finish.py      # Xác nhận & In ảnh
│   │
│   ├── shared/                   # 🔗 Code dùng chung
│   │   ├── types/
│   │   │   └── models.py         # Config, Constants, Layout definitions
│   │   └── utils/
│   │       ├── helpers.py        # Image utils, directory management
│   │       └── qr_utils.py       # QR code generation
│   │
│   ├── app.py                    # 🚀 Entry: Chế độ CÓ THANH TOÁN
│   └── app_free.py               # 🎉 Entry: Chế độ MIỄN PHÍ
│
├── public/                       # Assets tĩnh
│   ├── sample_photos/
│   └── sounds/
├── server/                       # Backend (placeholder)
│   └── database/
├── templates/                    # Khung ảnh templates
│   ├── 1x2/
│   ├── 2x1/
│   ├── 2x2/
│   ├── 4x1/
│   └── custom/
├── output/                       # Ảnh đầu ra
├── config.json                   # ⚙️ File cấu hình chính
├── config.example.json           # Mẫu config
├── camera_settings.json          # Cấu hình camera
└── requirements.txt              # Dependencies
```

---

## 🚀 Hướng Dẫn Cài Đặt

### 1. Yêu cầu hệ thống
- **Python** 3.8+
- **Windows** 10/11 (DirectShow camera support)
- **Camera** USB/Laptop/Iriun Webcam

### 2. Cài đặt Dependencies

```bash
# Clone hoặc copy project
cd photobooth-app

# Cài đặt thư viện
pip install -r requirements.txt
```

### 3. Cấu hình ban đầu

#### Cách 1: Dùng Admin Dashboard (Khuyến nghị)
```bash
python -m src.admin.pages.dashboard
```
Nhập các thông tin:
- **Giá tiền** cho từng layout
- **Thông tin ngân hàng** (VietQR)
- **Casso API Key** (kiểm tra thanh toán)
- **Cloudinary** API credentials

#### Cách 2: Tạo file config.json thủ công
Copy file `config.example.json` thành `config.json` và điền thông tin:

```json
{
    "bank_bin": "970422",
    "bank_name": "MB Bank",
    "bank_account": "YOUR_ACCOUNT_NUMBER",
    "account_name": "YOUR_NAME",
    "casso_api_key": "YOUR_CASSO_KEY",
    "price_2_photos": 20000,
    "price_4_photos": 35000,
    "cloudinary": {
        "cloud_name": "YOUR_CLOUD",
        "api_key": "YOUR_KEY",
        "api_secret": "YOUR_SECRET"
    }
}
```

### 4. Thiết lập Camera
```bash
python -m src.admin.pages.settings
```
- Chọn camera index phù hợp
- Bật/tắt DirectShow
- Chọn độ phân giải
- Nút "LƯU CẤU HÌNH & KẾT THÚC"

---

## ▶️ Cách Chạy Ứng Dụng

### Chế độ CÓ THANH TOÁN (Kinh doanh)
```bash
python -m src.app
```
**Luồng hoạt động:**
1. **Welcome** → Khách nhấn "BẮT ĐẦU CHỤP"
2. **Chọn gói** → Chọn layout (1x2, 2x1, 2x2, 4x1, custom)
3. **Thanh toán** → Quét QR → Casso tự xác nhận
4. **Chụp ảnh** → Đếm ngược → Chụp 10 ảnh
5. **Chọn ảnh** → Chọn 2 hoặc 4 ảnh đẹp nhất
6. **Chọn khung** → Chọn template/khung viền
7. **Kết quả** → Upload Cloud → QR tải ảnh

### Chế độ MIỄN PHÍ (Sự kiện/Party)
```bash
python -m src.app_free
```
**Luồng hoạt động:**
1. **Welcome** → Giao diện Bloom (hồng) + Live camera
2. **Chọn layout** → Chọn và chuyển thẳng sang chụp
3. **Chụp ảnh** → Đếm ngược + Quay video đồng thời
4. **Chọn ảnh** → Chọn ảnh đẹp nhất
5. **Chọn khung** → Chọn template
6. **Kết quả** → QR tải cả ảnh + video

---

## 🛠️ Công Cụ Quản Trị

### Admin Dashboard
```bash
python -m src.admin.pages.dashboard
```
- Cấu hình giá tiền từng layout
- Nhập thông tin ngân hàng
- Nhập API Keys (Casso, Cloudinary)
- Mở Frame Editor

### Camera Setup
```bash
python -m src.admin.pages.settings
```
- Dò tìm camera tự động
- Chế độ DirectShow/Tương thích
- Preview trực tiếp
- Chọn độ phân giải

### Frame Editor (Thiết kế khung ảnh)
```bash
# Mở trực tiếp
python -m src.admin.components.frame_editor

# Hoặc mở từ Admin Dashboard → nút "MỞ BỘ THIẾT KẾ KHUNG"
```
**Chức năng:**
- **Default Mode**: Kéo slider chỉnh padding, gap, kích thước canvas
- **Custom Mode**: Kéo thả các ô ảnh tự do
- **Lưu Custom**: Tạo mẫu mới → Tự tạo thư mục + ảnh mold
- **Export Code**: Copy code config để paste thủ công

---

## 📁 Mô Tả Chi Tiết Từng Module

### `src/shared/types/models.py`
- Tất cả hằng số, biến cấu hình toàn cục
- Hàm load/save config.json
- Định nghĩa layout (1x2, 2x1, 2x2, 4x1)
- Custom layouts (SLOTS format)
- Format giá, tạo mã giao dịch, VietQR URL

### `src/shared/utils/helpers.py`
- Quản lý thư mục (auto-create)
- Tạo dữ liệu mẫu (sample photos, templates)
- Chuyển ảnh OpenCV ↔ QPixmap
- Crop ảnh theo tỷ lệ
- Kiểm tra máy in

### `src/modules/camera/camera_manager.py`
- Auto-detect camera
- Chuyển camera index
- Đọc frame, flip ảnh
- Quay video MP4
- Auto-reconnect khi mất kết nối

### `src/modules/payment/payment_service.py`
- `QRImageLoaderThread`: Load ảnh QR từ VietQR API
- `CassoCheckThread`: Polling API Casso mỗi 3 giây

### `src/modules/image_processing/processor.py`
- `create_collage()`: Tạo ảnh collage từ ảnh đã chọn
- `apply_template_overlay()`: Ghép khung viền
- `load_templates_for_layout()`: Tìm templates phù hợp
- `generate_frame_templates()`: Tạo file khung mặc định

### `src/modules/storage/cloud_upload.py`
- `CloudinaryUploadThread`: Upload ảnh lên Cloudinary
- `CloudinaryLandingPageThread`: Upload + Tạo trang HTML

### `src/photobooth/hooks/flow_controller.py`
- State machine quản lý luồng
- Screen index constants
- Valid state transitions

---

## ⚠️ Lưu Ý Quan Trọng

1. **Ảnh đầu ra** được lưu tại `D:\picture\` (Windows)
2. **Camera Settings** lưu tại `camera_settings.json` ở thư mục gốc
3. **Config chính** là `config.json` - KHÔNG push lên Git (chứa API keys)
4. **Templates** được lưu trong thư mục `templates/` với các subfolder theo layout
5. Chạy `python -m src.admin.pages.settings` trước lần đầu sử dụng để cấu hình camera

---

## 🔧 Troubleshooting

| Vấn đề | Giải pháp |
|--------|-----------|
| Camera đen | Bật "Chế độ Tương thích" trong Camera Setup |
| Không tìm thấy camera | Cài Iriun Webcam hoặc kiểm tra kết nối USB |
| Lỗi thanh toán | Kiểm tra Casso API Key trong Admin Dashboard |
| Không upload được ảnh | Kiểm tra Cloudinary credentials |
| Không có templates | Chạy Frame Editor → "TẠO FILE KHUNG" |
| Thiếu config.json | Copy `config.example.json` → `config.json` hoặc chạy Admin Dashboard |

---

## 📦 Dependencies

| Package | Chức năng |
|---------|-----------|
| PyQt5 | GUI Framework |
| opencv-python | Camera, Image Processing |
| numpy | Xử lý mảng ảnh |
| qrcode | Tạo mã QR |
| Pillow | Xử lý ảnh bổ sung |
| requests | HTTP calls (Casso, VietQR) |
| cloudinary | Upload cloud |

---

## 🎨 Thiết Kế Custom Layout

1. Mở **Frame Editor**: `python -m src.admin.components.frame_editor`
2. Chọn **CUSTOM** trong dropdown
3. Nhấn **➕ THÊM Ô ẢNH** để thêm vùng ảnh mới
4. **Kéo** ô ảnh để di chuyển vị trí
5. **Kéo góc** (ô trắng nhỏ) để thay đổi kích thước
6. Điều chỉnh **Canvas** bằng slider bên trái
7. Nhấn **💾 LƯU THÀNH MẪU MỚI** để tạo custom layout
8. Vào thư mục `templates/customN/` để thay thế file mold bằng khung thiết kế riêng
9. Nhấn **CẬP NHẬT DANH SÁCH LAYOUT** trong Admin Dashboard

---

*Powered by QuangAnhDay's Photobooth* ✨
