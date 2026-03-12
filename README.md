# 📸 Photobooth App - Professional Suite

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/PyQt5-GUI-green?style=for-the-badge&logo=qt&logoColor=white" alt="UI Framework">
  <img src="https://img.shields.io/badge/OpenCV-Imaging-orange?style=for-the-badge&logo=opencv&logoColor=white" alt="Image Processing">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge" alt="Project Status">
</div>

---

## 📖 Giới thiệu

**Photobooth App** là giải pháp phần mềm toàn diện cho các trạm chụp ảnh tự động (Photobooth stations), hỗ trợ từ chụp ảnh, quay video, thanh toán tự động đến in ấn và chia sẻ Cloud.

### ✨ Tính năng nổi bật
- 🎥 **Live View & Capture**: Hỗ trợ Webcam và DSLR (via digiCamControl).
- 🧩 **Bố cục đa dạng**: 1x2, 2x1, 2x2, 4x1 và **Custom Layout** hoàn toàn linh hoạt.
- 💳 **Thanh toán QR**: Tích hợp VietQR + Casso tự động xác nhận giao dịch.
- 🎨 **Frame Editor**: Thiết kế khung ảnh trực quan, kéo thả linh hoạt.
- ☁️ **Cloud Sharing**: Tự động upload Cloudinary và tạo mã QR tải ảnh/video tại chỗ.
- 🎞️ **Video Rec**: Quay video quá trình chụp (Free Mode) tạo kỷ niệm sinh động.
- 🛠️ **Admin Dashboard**: Quản lý giá, cấu hình ngân hàng, API keys và Camera.

---

## 🏗️ Cấu Trúc Hệ Thống

```text
photobooth-app/
├── src/
│   ├── admin/             # 🛠️ Quản trị (Dashboard, Settings, Frame Editor)
│   ├── services/          # ⚙️ Core Logic (CameraHandler, Payment, ImageWorkflow)
│   ├── ui/                # 📷 Giao diện người dùng (PyQt5 Screens & Widgets)
│   │   ├── screens/       # Các bước trong luồng (Idle, Payment, Capture, Template...)
│   │   └── widgets/       # Thành phần UI dùng chung (CameraView, Buttons...)
│   ├── shared/            # 🔗 Dữ liệu dùng chung (Models, Config, Constants)
│   ├── utils/             # 🛠️ Hàm tiện ích (Files, Fonts, QR Utils)
│   ├── app.py             # 🚀 Entry: Chế độ KINH DOANH (CÓ THANH TOÁN)
│   └── app_free.py        # 🎉 Entry: Chế độ SỰ KIỆN (MIỄN PHÍ - FAST FLOW)
├── templates/             # Thư mục chứa các mẫu khung ảnh (PNG/MOLD)
├── public/                # Assets tĩnh (Sounds, Sample photos, Fonts)
├── config.json            # ⚙️ Cấu hình hệ thống (API Keys, Bank Info)
└── camera_settings.json   # 🎥 Cấu hình Camera hiện hành
```

---

## 🚀 Hướng Dẫn Cài Đặt

### 1. Yêu cầu hệ thống
- **Hệ điều hành**: Windows 10/11 (Khuyến nghị để hỗ trợ driver camera tốt nhất).
- **Python**: Phiên bản 3.8 trở lên.
- **Phụ kiện**: Máy in ảnh (nếu cần in), Camera (Webcam Iriun/USB hoặc DSLR Canon/Nikon).

### 2. Cài đặt Dependencies
```bash
# Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# Cài đặt thêm thư viện hỗ trợ list camera (nếu chưa có)
pip install pygrabber
```

### 3. Cấu hình Camera DSLR (digiCamControl)
Để đạt chất lượng ảnh tốt nhất, nên sử dụng dòng máy DSLR kết nối qua `digiCamControl`:
1. Tải và cài đặt [digiCamControl](https://digicamcontrol.com/).
2. Kết nối máy ảnh qua USB, mở phần mềm và đảm bảo máy ảnh đã được nhận diện.
3. Vào **Settings** → Bật chức năng **Webserver**.
4. Tại màn hình chính, nhấn nút **LV** (Live View) để truyền tín hiệu.
5. Sao chép link MJPEG (mặc định: `http://127.0.0.1:8080/mjpg/video.mjpg`).
6. Chạy cấu hình camera: `python -m src.admin.pages.settings`.
7. Dán link vào ô **MJPEG Stream Address** và nhấn **USE DSLR**.

---

## ▶️ Cách Vận Hành

### 💼 Chế độ Kinh doanh (Pay-to-Snap)
`python -m src.app`
> **Luồng**: Welcome → Chọn gói/Layout → Thanh toán QR → Chờ xác thực (Casso) → Live View & Chụp (10 tấm) → Chọn ảnh → Chọn Template → Xử lý & In → Quét QR tải ảnh.

### 🎈 Chế độ Sự kiện (Free/Fast)
`python -m src.app_free`
> **Luồng**: Welcome (Live view nền) → Chọn Layout → Chụp ngay (3-4 tấm) + Quay Video → Chọn ảnh → Ghép khung → Quét QR tải cả Ảnh & Video.

---

## 🛠️ Công Cụ Quản Trị

| Công cụ | Lệnh thực thi | Chức năng chính |
|:--- |:--- |:--- |
| **Admin Dashboard** | `python -m src.admin.pages.dashboard` | Setup giá, API Keys, Thông tin Bank. |
| **Camera Settings** | `python -m src.admin.pages.settings` | Chọn nguồn Camera, Resolution, DSLR Mode. |
| **Frame Editor** | `python -m src.admin.components.frame_editor` | Thiết kế vùng ảnh (Slots) cho Template. |

---

## 🎨 Tùy Biến Layout & Template

1. Sử dụng **Frame Editor** để tạo bố cục mới (`Custom Mode`).
2. Nhấn **Lưu thành mẫu mới** để hệ thống tự tạo thư mục trong `templates/`.
3. Thay thế file `mold.png` trong thư mục vừa tạo bằng file thiết kế khung của bạn (giữ nguyên tên và định dạng).
4. Hệ thống sẽ tự động quét và hiển thị Template mới trong giao diện chọn khung.

---

## 🔧 Giải quyết sự cố (Troubleshooting)

- **Camera không hiển thị**: Kiểm tra xem `digiCamControl` đã bật Live View chưa, hoặc thử đổi sang `Compatibility Mode` trong Camera Settings.
- **Không nhận thanh toán**: Kiểm tra `casso_api_key` trong `config.json` và đảm bảo webhook/polling đang hoạt động.
- **Lỗi in ấn**: Đảm bảo máy in đã được set làm `Default Printer` trong Windows.

---

<div align="center">
  <p><i>Developed with ❤️ by QuangAnhDay</i></p>
  <p><b>Hãy tạo nên những khoảnh khắc tuyệt vời!</b> 📸✨</p>
</div>
