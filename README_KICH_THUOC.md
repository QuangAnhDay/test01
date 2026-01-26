# 📸 KÍCH THƯỚC ẢNH - TÓM TẮT NHANH

## 🎯 4 LAYOUT CHÍNH

### 1️⃣ Layout 1x2 (2 ảnh ngang)
```
📏 Kích thước: 1280 x 720 pixels
📐 Tỷ lệ: 16:9 (Landscape)
📁 Thư mục: templates/2_1x2/
🖼️ Cấu trúc: [Ảnh 1][Ảnh 2]
```

### 2️⃣ Layout 2x1 (2 ảnh dọc)
```
📏 Kích thước: 640 x 720 pixels  
📐 Tỷ lệ: 8:9 (Portrait)
📁 Thư mục: templates/2_2x1/
🖼️ Cấu trúc: [Ảnh 1]
            [Ảnh 2]
```

### 3️⃣ Layout 2x2 (4 ảnh lưới)
```
📏 Kích thước: 1280 x 720 pixels
📐 Tỷ lệ: 16:9 (Landscape)
📁 Thư mục: templates/4_2x2/
🖼️ Cấu trúc: [Ảnh 1][Ảnh 2]
            [Ảnh 3][Ảnh 4]
```

### 4️⃣ Layout 4x1 (4 ảnh dọc)
```
📏 Kích thước: 640 x 1440 pixels
📐 Tỷ lệ: 4:9 (Portrait - Dài)
📁 Thư mục: templates/4_4x1/
🖼️ Cấu trúc: [Ảnh 1]
            [Ảnh 2]
            [Ảnh 3]
            [Ảnh 4]
```

---

## ⚡ THIẾT KẾ KHUNG NHANH

### Bước 1: Tạo file PNG
- Kích thước: Theo layout ở trên
- Background: **Transparent** (bắt buộc!)

### Bước 2: Vẽ viền
- Viền dày: 40-60px
- Vùng giữa: **Trong suốt** (để ảnh hiển thị)

### Bước 3: Lưu file
- Format: **PNG** (không phải JPG!)
- Tên: `ten_khung.png` (không dấu, không khoảng trắng)
- Vị trí: `templates/[layout]/ten_khung.png`

---

## 📋 CHECKLIST

- [ ] File PNG có alpha channel
- [ ] Kích thước đúng
- [ ] Vùng giữa trong suốt
- [ ] Viền không che mặt (margin 40-50px)
- [ ] Tên file hợp lệ
- [ ] Đặt đúng thư mục

---

## 📚 TÀI LIỆU CHI TIẾT

- 📄 [KICH_THUOC_ANH.md](./KICH_THUOC_ANH.md) - Thông tin chi tiết
- 📄 [HUONG_DAN_THIET_KE_KHUNG.md](./HUONG_DAN_THIET_KE_KHUNG.md) - Hướng dẫn từng bước
- 🖼️ [template_guide_diagram.png](./template_guide_diagram.png) - Sơ đồ kích thước
- 🖼️ [frame_design_example.png](./frame_design_example.png) - Ví dụ thiết kế

---

**💡 Tip**: Xem file mẫu trong `templates/2_1x2/frame_blue.png` để tham khảo!
