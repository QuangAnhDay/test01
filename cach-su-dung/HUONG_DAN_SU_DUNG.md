# 📸 HƯỚNG DẪN SỬ DỤNG PHOTOBOOTH

## 📋 MỤC LỤC
1. [Cài đặt môi trường](#1-cài-đặt-môi-trường)
2. [Cấu hình hệ thống](#2-cấu-hình-hệ-thống)
3. [Chạy ứng dụng](#3-chạy-ứng-dụng)
4. [Quy trình sử dụng](#4-quy-trình-sử-dụng)
5. [Quản lý khung ảnh](#5-quản-lý-khung-ảnh)
6. [Lỗi thường gặp](#6-lỗi-thường-gặp)

---

## 1. CÀI ĐẶT MÔI TRƯỜNG

### Bước 1: Cài đặt Python
1. Tải Python từ: https://www.python.org/downloads/
2. Chọn phiên bản **Python 3.8 trở lên**
3. Khi cài đặt, **BẮT BUỘC** tick chọn:
   - ✅ **"Add Python to PATH"**
   - ✅ **"Install pip"**

### Bước 2: Cài đặt thư viện
Mở **Command Prompt** hoặc **PowerShell** và chạy:

```bash
cd D:\photobooth1
pip install -r requirements.txt
```

Hoặc cài thủ công:
```bash
pip install PyQt5 opencv-python numpy qrcode pillow requests cloudinary
```

### Bước 3: Kiểm tra cài đặt
```bash
python -c "import PyQt5, cv2, qrcode, requests; print('OK!')"
```

Nếu thấy `OK!` là thành công.

---

## 2. CẤU HÌNH HỆ THỐNG

### ⚙️ Bước 1: Chạy Setup Admin

**QUAN TRỌNG**: Phải chạy setup trước khi dùng app chính!

```bash
cd D:\photobooth1
python setup_admin.py
```

### 📝 Bước 2: Điền thông tin

Giao diện setup sẽ yêu cầu bạn nhập:

#### 🏦 **Thông tin ngân hàng:**
- **Ngân hàng**: Chọn từ danh sách (VietQR tự động tải)
- **Số tài khoản**: Số tài khoản nhận tiền
- **Tên chủ TK**: Tên không dấu (VD: NGUYEN VAN A)

#### 🔐 **Casso API Key:**
1. Truy cập: https://casso.vn
2. Đăng ký/Đăng nhập
3. Vào **Cài đặt** → **API Keys**
4. Tạo API Key mới
5. Copy và dán vào ô "Casso API Key"

> 💡 **Lưu ý**: Casso API dùng để tự động kiểm tra thanh toán. Nếu không có, khách phải nhấn nút "Đã thanh toán" thủ công.

#### 💰 **Giá tiền:**
- **Gói 2 ảnh**: Nhập giá (VD: 20000)
- **Gói 4 ảnh**: Nhập giá (VD: 35000)

#### ☁️ **Cloudinary (Tùy chọn):**
Nếu muốn khách tải ảnh về điện thoại qua QR:
1. Đăng ký miễn phí tại: https://cloudinary.com
2. Lấy thông tin:
   - Cloud Name
   - API Key
   - API Secret
3. Điền vào form

> 💡 **Bỏ qua** nếu chỉ muốn in ảnh, không cần tải về điện thoại.

### 💾 Bước 3: Lưu cấu hình

Nhấn **"💾 LƯU CẤU HÌNH"**

File `config.json` sẽ được tạo tự động.

---

## 3. CHẠY ỨNG DỤNG

### 🚀 Khởi động

```bash
cd D:\photobooth1
python main_app.py
```

### 🖥️ Chế độ toàn màn hình (khuyến nghị)

Nhấn **F11** hoặc sửa code:
```python
window.showFullScreen()  # Thay vì window.show()
```

### 🔄 Khởi động lại

Nếu sửa config, cần khởi động lại app:
- Đóng app (Alt+F4)
- Chạy lại `python main_app.py`

---

## 4. QUY TRÌNH SỬ DỤNG

### 📱 Luồng hoạt động đầy đủ:

```
1. MÀN HÌNH CHÀO
   ↓ Nhấn "🎬 BẮT ĐẦU CHỤP"
   
2. CHỌN KIỂU LƯỚI ẢNH
   ├─ 2 Hàng x 1 Cột (2 ảnh dọc)    → 20.000 VNĐ
   ├─ 1 Hàng x 2 Cột (2 ảnh ngang)  → 20.000 VNĐ
   ├─ 4 Hàng x 1 Cột (4 ảnh dọc)    → 35.000 VNĐ
   └─ 2 Hàng x 2 Cột (4 ảnh lưới)   → 35.000 VNĐ
   ↓
   
3. THANH TOÁN QR
   ├─ Hiển thị QR VietQR động
   ├─ Mã giao dịch: PBxxxx
   ├─ Khách quét QR → Chuyển khoản
   └─ Hệ thống tự động kiểm tra qua Casso (mỗi 3 giây)
   ↓ Khi nhận tiền
   
4. CHỤP ẢNH
   ├─ Đếm ngược 10 giây (ảnh đầu)
   ├─ Chụp 10 ảnh liên tục (mỗi ảnh cách 1 giây)
   └─ Hiển thị số ảnh đã chụp
   ↓
   
5. CHỌN ẢNH
   ├─ Hiển thị 10 ảnh vừa chụp
   ├─ Chọn 2 hoặc 4 ảnh yêu thích (tùy gói)
   ├─ Thời gian: 60s (gói 2) hoặc 120s (gói 4)
   └─ Nhấn "XÁC NHẬN CHỌN ẢNH"
   ↓
   
6. CHỌN KHUNG VIỀN
   ├─ Xem preview ảnh thành quả
   ├─ Chọn khung trang trí
   ├─ Hoặc "KHÔNG DÙNG KHUNG"
   └─ Thời gian: 60 giây
   ↓
   
7. LƯU ẢNH
   ├─ Ảnh được lưu tại: D:\picture\
   ├─ Tên file: photo_YYYYMMDD-HHMMSS.jpg
   └─ Hiển thị QR để tải về điện thoại (nếu có Cloudinary)
   ↓
   
8. QUAY LẠI MÀN HÌNH CHÀO
```

---

## 5. QUẢN LÝ KHUNG ẢNH

### 📂 Cấu trúc thư mục

```
templates/
├── 2_1x2/          # Khung cho layout 1x2 (1280x720)
│   ├── frame_blue.png
│   ├── frame_gold.png
│   └── ...
├── 2_2x1/          # Khung cho layout 2x1 (640x720)
├── 4_2x2/          # Khung cho layout 2x2 (1280x720)
└── 4_4x1/          # Khung cho layout 4x1 (640x1440)
```

### ➕ Thêm khung mới

1. **Thiết kế khung** theo hướng dẫn trong `HUONG_DAN_THIET_KE_KHUNG.md`
2. **Export PNG** với alpha channel
3. **Đặt tên**: `ten_khung.png` (không dấu, không khoảng trắng)
4. **Copy vào thư mục** tương ứng với layout
5. **Khởi động lại app** để load khung mới

### 🗑️ Xóa khung

Xóa file PNG trong thư mục `templates/[layout]/`

### 📏 Kích thước khung

Xem chi tiết trong file: `KICH_THUOC_ANH.md`

---

## 6. LỖI THƯỜNG GẶP

### ❌ Lỗi: "Không tìm thấy file config.json"

**Nguyên nhân**: Chưa chạy setup_admin.py

**Giải pháp**:
```bash
python setup_admin.py
```

---

### ❌ Lỗi: "Không tìm thấy camera"

**Nguyên nhân**: 
- Camera chưa kết nối
- Đang được dùng bởi app khác
- Index camera sai

**Giải pháp**:
1. Kiểm tra camera đã cắm
2. Đóng Zoom/Skype/Teams
3. Thử đổi `CAMERA_INDEX`:
   ```python
   # Trong main_app.py, dòng ~37
   CAMERA_INDEX = 0  # Thử đổi thành 1, 2, 3...
   ```

---

### ❌ Lỗi: "Casso API Key không hợp lệ"

**Nguyên nhân**: API key sai hoặc hết hạn

**Giải pháp**:
1. Vào https://casso.vn
2. Tạo API key mới
3. Chạy lại `python setup_admin.py`
4. Nhập API key mới

---

### ❌ Lỗi: "Không tải được QR từ VietQR"

**Nguyên nhân**: Không có internet hoặc VietQR API lỗi

**Giải pháp**:
- App sẽ tự động dùng QR backup (tự tạo)
- Kiểm tra kết nối mạng
- QR backup vẫn hoạt động bình thường

---

### ❌ Lỗi: Font chữ bị lỗi

**Nguyên nhân**: Windows thiếu font tiếng Việt

**Giải pháp**:
- App đã dùng Arial/Segoe UI (có sẵn trên Windows)
- Nếu vẫn lỗi, cài font "Arial Unicode MS"

---

### ❌ Lỗi: "Không tìm thấy máy in"

**Nguyên nhân**: Máy in chưa kết nối hoặc chưa cài driver

**Giải pháp**:
1. Kiểm tra máy in đã bật
2. Kiểm tra driver đã cài
3. Test in thử:
   ```powershell
   Get-Printer
   ```

---

### ❌ Lỗi: Ảnh bị méo/vỡ

**Nguyên nhân**: Khung không đúng kích thước

**Giải pháp**:
1. Kiểm tra kích thước khung:
   ```bash
   python -c "from PIL import Image; print(Image.open('templates/2_1x2/frame.png').size)"
   ```
2. Phải khớp với layout:
   - 1x2: 1280x720
   - 2x1: 640x720
   - 2x2: 1280x720
   - 4x1: 640x1440

---

### ❌ Lỗi: Cloudinary upload failed

**Nguyên nhân**: 
- Chưa cài thư viện cloudinary
- Thông tin Cloudinary sai
- Không có internet

**Giải pháp**:
1. Cài thư viện:
   ```bash
   pip install cloudinary
   ```
2. Kiểm tra config trong `config.json`
3. Nếu không cần upload cloud, bỏ qua lỗi này

---

## 📞 HỖ TRỢ

### 📚 Tài liệu tham khảo:
- `README_KICH_THUOC.md` - Kích thước ảnh
- `KICH_THUOC_ANH.md` - Chi tiết kỹ thuật
- `HUONG_DAN_THIET_KE_KHUNG.md` - Hướng dẫn thiết kế

### 🔧 Debug:
```bash
# Kiểm tra Python
python --version

# Kiểm tra thư viện
pip list

# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAIL')"

# Test config
python -c "import json; print(json.load(open('config.json')))"
```

---

## 🎯 TIPS SỬ DỤNG

### ⚡ Tối ưu hiệu suất:
- Đóng các app không cần thiết
- Dùng camera USB chất lượng tốt
- Đảm bảo đủ ánh sáng

### 🎨 Thiết kế đẹp:
- Dùng khung đơn giản, không quá rườm rà
- Để margin 40-50px tránh che mặt
- Test với ảnh thật trước khi dùng

### 💰 Quản lý thanh toán:
- Kiểm tra Casso mỗi ngày
- Đối chiếu số tiền với số lượt chụp
- Backup file config.json

---

**Chúc bạn sử dụng thành công!** 🎉📸
