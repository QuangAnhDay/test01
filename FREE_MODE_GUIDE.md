# 🎉 HƯỚNG DẪN SỬ DỤNG CHẾ ĐỘ MIỄN PHÍ

## 📋 Tổng quan

Dự án có **2 chế độ** chạy:

### 1. **Chế độ THƯỜNG** (`main.py`)
- ✅ Có bước chọn giá (2 ảnh / 4 ảnh)
- ✅ Có bước thanh toán QR
- ✅ Kiểm tra thanh toán qua Casso
- ✅ Phù hợp cho kinh doanh

### 2. **Chế độ MIỄN PHÍ** (`main_free.py`) 🆕
- ✅ **KHÔNG** cần thanh toán
- ✅ Bấm "Bắt đầu" → Chụp ngay
- ✅ Mặc định: 4 ảnh
- ✅ Phù hợp cho sự kiện, demo, test

---

## 🚀 CÁCH SỬ DỤNG

### Chế độ THƯỜNG (Có thanh toán):
```bash
python main.py
```

**Workflow:**
```
Welcome → Chọn giá → QR Payment → Chụp ảnh → Chọn layout → Chọn ảnh → Chọn khung → In
```

---

### Chế độ MIỄN PHÍ (Không thanh toán):
```bash
python main_free.py
```

**Workflow:**
```
Welcome → Chụp ảnh ngay → Chọn layout → Chọn ảnh → Chọn khung → In
```

---

## 🎯 SO SÁNH 2 CHẾ ĐỘ

| Tính năng | main.py | main_free.py |
|-----------|---------|--------------|
| Màn hình Welcome | ✅ | ✅ |
| Chọn giá (2/4 ảnh) | ✅ | ❌ Bỏ qua |
| QR Payment | ✅ | ❌ Bỏ qua |
| Kiểm tra Casso | ✅ | ❌ Bỏ qua |
| Chụp ảnh | ✅ | ✅ |
| Chọn layout | ✅ | ✅ |
| Chọn ảnh | ✅ | ✅ |
| Chọn khung | ✅ | ✅ |
| Upload Cloudinary | ✅ | ✅ |
| In ảnh | ✅ | ✅ |
| Số ảnh mặc định | Theo chọn | 4 ảnh |

---

## 💡 KHI NÀO DÙNG CHẾ ĐỘ NÀO?

### Dùng `main.py` (Thường) khi:
- 🏪 Kinh doanh photobooth
- 💰 Cần thu phí
- 📊 Cần theo dõi doanh thu
- 🔐 Cần xác thực thanh toán

### Dùng `main_free.py` (Miễn phí) khi:
- 🎉 Sự kiện miễn phí
- 🎊 Tiệc cưới, sinh nhật
- 🧪 Test, demo
- 🎓 Sự kiện trường học
- 🏢 Sự kiện công ty

---

## 🔧 CẤU HÌNH

### Cả 2 chế độ đều cần:
- ✅ File `config.json` (cho Cloudinary, camera, etc.)
- ✅ Thư mục `templates/` (khung ảnh)
- ✅ Thư mục `sample_photos/` (ảnh mẫu)

### Chỉ `main.py` cần:
- 💰 `price_2_photos`, `price_4_photos` trong config
- 🏦 `bank_bin`, `bank_account`, `account_name`
- 🔑 `casso_api_key`

### `main_free.py` không cần:
- ❌ Thông tin ngân hàng
- ❌ Casso API key
- ℹ️ Nhưng vẫn cần Cloudinary nếu muốn upload

---

## 📝 CHỈNH SỬA CHẾ ĐỘ MIỄN PHÍ

### Đổi số ảnh mặc định:
Mở `main_free.py`, tìm dòng:
```python
self.selected_price_type = 4  # Mặc định 4 ảnh
self.selected_frame_count = 4
```

Đổi thành:
```python
self.selected_price_type = 2  # Đổi thành 2 ảnh
self.selected_frame_count = 2
```

### Đổi text nút:
Tìm dòng:
```python
self.btn_start.setText("🎉 BẮT ĐẦU CHỤP MIỄN PHÍ")
```

Đổi thành:
```python
self.btn_start.setText("📸 CHỤP ẢNH NGAY")
```

---

## 🐛 TROUBLESHOOTING

### Lỗi: "Không tìm thấy config.json"
**Giải pháp:**
```bash
copy config.example.json config.json
# Sau đó sửa config.json
```

### Lỗi: Camera không hoạt động
**Giải pháp:**
- Kiểm tra `CAMERA_INDEX` trong `configs.py`
- Thử đổi từ 0 sang 1 hoặc 2

### Lỗi: Không upload được Cloudinary
**Giải pháp:**
- Kiểm tra thông tin Cloudinary trong `config.json`
- Đảm bảo có internet

### App không hiển thị gì
**Giải pháp:**
- Kiểm tra console có lỗi gì
- Chạy `python -c "from main_app import PhotoboothApp"`

---

## 🎨 TÙY CHỈNH THÊM

### Thêm chế độ chọn số ảnh trong FREE mode:
Bạn có thể sửa `main_free.py` để thêm dialog chọn 2 hoặc 4 ảnh trước khi chụp.

### Tắt upload Cloudinary trong FREE mode:
Tìm và comment dòng upload trong `main_app.py` hoặc tạo flag `free_mode`.

### Thêm watermark "FREE" vào ảnh:
Sửa hàm tạo collage để thêm text "MIỄN PHÍ" vào ảnh.

---

## 📊 THỐNG KÊ

### Thời gian workflow:

**Chế độ THƯỜNG:**
```
Welcome (10s) → Chọn giá (5s) → QR (30s) → Chụp (30s) → Chọn (20s) → In (10s)
Tổng: ~105 giây (~1.75 phút)
```

**Chế độ MIỄN PHÍ:**
```
Welcome (10s) → Chụp (30s) → Chọn (20s) → In (10s)
Tổng: ~70 giây (~1.2 phút)
```

**Tiết kiệm:** ~35 giây mỗi lượt!

---

## ✅ CHECKLIST

### Trước khi chạy FREE mode:
- [ ] Đã cài `pip install -r requirements.txt`
- [ ] Đã có file `config.json`
- [ ] Đã có thư mục `templates/`
- [ ] Camera hoạt động
- [ ] (Tùy chọn) Cloudinary đã cấu hình

### Khi chạy:
- [ ] Chạy `python main_free.py`
- [ ] Bấm "Bắt đầu"
- [ ] Chụp 10 ảnh
- [ ] Chọn layout
- [ ] Chọn 4 ảnh
- [ ] Chọn khung
- [ ] In/Tải về

---

## 🎉 KẾT LUẬN

Bây giờ bạn có **2 chế độ** linh hoạt:
- 💰 **main.py** - Kinh doanh có thu phí
- 🎉 **main_free.py** - Miễn phí cho sự kiện

Chọn chế độ phù hợp với nhu cầu của bạn!

---

**Tạo ngày:** 2026-01-29  
**Phiên bản:** 2.0 (Refactored + Free Mode)
