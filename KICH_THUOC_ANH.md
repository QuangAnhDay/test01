# 📐 KÍCH THƯỚC ẢNH THÀNH QUẢ - PHOTOBOOTH

## 🎯 TÓM TẮT NHANH

| Layout | Kích thước (px) | Tỷ lệ | Hướng | Mô tả |
|--------|----------------|-------|-------|-------|
| **1x2** (2 ảnh ngang) | 1280 x 720 | 16:9 | Ngang | 2 ảnh xếp ngang |
| **2x1** (2 ảnh dọc) | 640 x 720 | ~8:9 | Dọc | 2 ảnh xếp dọc |
| **2x2** (4 ảnh lưới) | 1280 x 720 | 16:9 | Ngang | 4 ảnh lưới 2x2 |
| **4x1** (4 ảnh dọc) | 640 x 1440 | 4:9 | Dọc | 4 ảnh xếp dọc |

---

## 📏 CHI TIẾT TỪNG LAYOUT

### 1. Layout 1x2 (2 ảnh - Ngang)
```
Kích thước ảnh thành quả: 1280 x 720 pixels
Tỷ lệ: 16:9 (Landscape)
Định dạng: Ngang

Cấu trúc:
┌─────────┬─────────┐
│  Ảnh 1  │  Ảnh 2  │
│ 640x720 │ 640x720 │
└─────────┴─────────┘

Kích thước khung PNG: 1280 x 720 pixels (RGBA)
```

### 2. Layout 2x1 (2 ảnh - Dọc)
```
Kích thước ảnh thành quả: 640 x 720 pixels
Tỷ lệ: ~8:9 (Portrait)
Định dạng: Dọc

Cấu trúc:
┌─────────┐
│  Ảnh 1  │
│ 640x360 │
├─────────┤
│  Ảnh 2  │
│ 640x360 │
└─────────┘

Kích thước khung PNG: 640 x 720 pixels (RGBA)
```

### 3. Layout 2x2 (4 ảnh - Lưới)
```
Kích thước ảnh thành quả: 1280 x 720 pixels
Tỷ lệ: 16:9 (Landscape)
Định dạng: Ngang

Cấu trúc:
┌─────────┬─────────┐
│  Ảnh 1  │  Ảnh 2  │
│ 640x360 │ 640x360 │
├─────────┼─────────┤
│  Ảnh 3  │  Ảnh 4  │
│ 640x360 │ 640x360 │
└─────────┴─────────┘

Kích thước khung PNG: 1280 x 720 pixels (RGBA)
```

### 4. Layout 4x1 (4 ảnh - Dọc)
```
Kích thước ảnh thành quả: 640 x 1440 pixels
Tỷ lệ: 4:9 (Portrait - Dài)
Định dạng: Dọc

Cấu trúc:
┌─────────┐
│  Ảnh 1  │
│ 640x360 │
├─────────┤
│  Ảnh 2  │
│ 640x360 │
├─────────┤
│  Ảnh 3  │
│ 640x360 │
├─────────┤
│  Ảnh 4  │
│ 640x360 │
└─────────┘

Kích thước khung PNG: 640 x 1440 pixels (RGBA)
```

---

## 🎨 HƯỚNG DẪN THIẾT KẾ KHUNG

### Yêu cầu file khung:
- **Format**: PNG với alpha channel (RGBA)
- **Kích thước**: Phải khớp chính xác với layout tương ứng
- **Vùng trong suốt**: Phần ảnh sẽ hiển thị qua vùng alpha = 0
- **Viền/Khung**: Vẽ ở phần alpha = 255

### Ví dụ thiết kế khung 1x2 (1280x720):
```
1. Tạo canvas 1280 x 720 pixels
2. Vẽ viền/khung trang trí
3. Để vùng giữa trong suốt (alpha = 0) cho ảnh
4. Export PNG với alpha channel
5. Lưu vào: templates/2_1x2/ten_khung.png
```

### Lưu ý quan trọng:
⚠️ **Vùng ảnh an toàn**: Nên để margin ~40-50px từ mép để tránh khung che mất khuôn mặt
⚠️ **Tỷ lệ**: Giữ đúng tỷ lệ để ảnh không bị méo
⚠️ **Độ phân giải**: 1280x720 là HD ready, đủ cho in ảnh 4x6 inch

---

## 📂 CẤU TRÚC THƯ MỤC TEMPLATES

```
templates/
├── 2_1x2/          # Khung cho layout 1x2 (1280x720)
│   ├── frame_blue.png
│   ├── frame_gold.png
│   └── ...
├── 2_2x1/          # Khung cho layout 2x1 (640x720)
│   ├── frame_blue.png
│   └── ...
├── 4_2x2/          # Khung cho layout 2x2 (1280x720)
│   ├── frame_blue.png
│   └── ...
└── 4_4x1/          # Khung cho layout 4x1 (640x1440)
    ├── frame_blue.png
    └── ...
```

---

## 💡 TIPS THIẾT KẾ

### Cho layout ngang (1x2, 2x2):
- Phù hợp in ảnh 6x4 inch (landscape)
- Dễ xem trên màn hình ngang
- Tỷ lệ 16:9 chuẩn HD

### Cho layout dọc (2x1, 4x1):
- Phù hợp in ảnh 4x6 inch (portrait)
- Dễ chia sẻ trên Instagram Stories
- Layout 4x1 rất dài, phù hợp in strip

### Vùng an toàn (Safe Area):
```
Margin khuyến nghị:
- Top: 40-60px
- Bottom: 40-60px
- Left/Right: 40-50px
```

---

## 🖨️ KÍCH THƯỚC IN ẢNH

| Layout | Kích thước in khuyến nghị | DPI |
|--------|---------------------------|-----|
| 1x2 (1280x720) | 6x4 inch ngang | ~213 DPI |
| 2x1 (640x720) | 4x6 inch dọc | ~120 DPI |
| 2x2 (1280x720) | 6x4 inch ngang | ~213 DPI |
| 4x1 (640x1440) | 4x12 inch strip | ~120 DPI |

**Lưu ý**: DPI thấp hơn 300 nhưng vẫn chấp nhận được cho photobooth event.

---

## 🔧 CODE THAM KHẢO

Trong code, ảnh được xử lý tại hàm `create_collage()` (nếu có).
Kích thước được định nghĩa dựa trên layout type:

```python
if layout_type == "1x2":
    canvas_size = (1280, 720)
elif layout_type == "2x1":
    canvas_size = (640, 720)
elif layout_type == "2x2":
    canvas_size = (1280, 720)
elif layout_type == "4x1":
    canvas_size = (640, 1440)
```

---

**Tạo bởi**: Photobooth System
**Ngày**: 2026-01-26
