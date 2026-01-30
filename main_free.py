# ==========================================
# MAIN FREE MODE - KHÔNG CẦN THANH TOÁN
# ==========================================
"""
File chạy ứng dụng Photobooth ở chế độ MIỄN PHÍ.
Bỏ qua hoàn toàn bước chọn giá và thanh toán QR.

CÁCH CHẠY:
    python main_free.py

KHÁC BIỆT VỚI main.py:
    - Không có màn hình chọn giá
    - Không có màn hình QR thanh toán
    - Bấm "Bắt đầu" → Chụp ảnh ngay
    - Mặc định: 4 ảnh
"""

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QPushButton
from PyQt5.QtCore import Qt
from configs import load_config
from utils import ensure_directories
from main_app import PhotoboothApp


class FreePhotobooth(PhotoboothApp):
    """
    Photobooth miễn phí - Bỏ qua thanh toán.
    Kế thừa từ PhotoboothApp và override workflow.
    """
    
    def __init__(self):
        # Đặt flag TRƯỚC khi gọi super().__init__()
        self.is_free_mode = True
        
        # Gọi constructor của class cha
        super().__init__()
        
        # Đặt title khác để phân biệt
        self.setWindowTitle("🎉 Photobooth - MIỄN PHÍ")
        
        # Đặt mặc định cho chế độ free
        self.selected_price_type = 4  # Mặc định 4 ảnh
        self.selected_frame_count = 4
        self.payment_confirmed = True  # Luôn True vì không cần thanh toán
        
        print("\n" + "="*60)
        print("🎉 CHẾ ĐỘ MIỄN PHÍ ĐÃ KÍCH HOẠT")
        print("="*60)
        print("✅ Bỏ qua bước chọn giá")
        print("✅ Bỏ qua bước thanh toán QR")
        print("✅ Mặc định: 4 ảnh")
        print("="*60 + "\n")
    
    def create_welcome_screen(self):
        """Override màn hình welcome - Giữ nguyên, chỉ đổi text nút."""
        # Gọi hàm gốc để tạo màn hình
        super().create_welcome_screen()
        
        # Đổi text nút để rõ ràng là FREE
        if hasattr(self, 'btn_start_welcome'):
            self.btn_start_welcome.setText("🎉 BẮT ĐẦU (MIỄN PHÍ)")
    
    def create_price_select_screen(self):
        """Giữ nguyên màn hình chọn lưới - Không override."""
        # Gọi hàm gốc để tạo màn hình chọn lưới bình thường
        super().create_price_select_screen()
    
    def create_qr_payment_screen(self):
        """Override - Không tạo màn hình QR payment trong free mode."""
        # Tạo màn hình trống để giữ index
        from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
        screen = QWidget()
        layout = QVBoxLayout(screen)
        label = QLabel("Free Mode - Đang chuyển sang chụp ảnh...")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #00f5d4; font-size: 24px;")
        layout.addWidget(label)
        self.stacked.addWidget(screen)
    
    def select_layout_and_price(self, photo_count, layout_type):
        """Override - Bỏ qua QR payment, chuyển thẳng sang chụp ảnh."""
        print(f"\n🎉 FREE MODE - Đã chọn: {photo_count} ảnh, Layout: {layout_type}")
        
        # Lưu thông tin đã chọn
        self.selected_price_type = photo_count
        self.selected_frame_count = photo_count
        self.layout_type = layout_type
        self.payment_confirmed = True  # Luôn True trong free mode
        
        print(f"✅ Bỏ qua thanh toán - Chuyển thẳng sang chụp ảnh")
        
        # Chuyển THẲNG sang màn hình chụp ảnh (bỏ qua QR payment)
        self.start_capture()
    
    def start_capture(self):
        """Bắt đầu chụp ảnh."""
        # Chuyển sang màn hình capture (index 3)
        self.stacked.setCurrentIndex(3)
        self.state = "CAPTURING"
        
        # Reset danh sách ảnh
        self.captured_photos = []
        
        # Bắt đầu countdown
        self.countdown_val = 3
        self.countdown_label.setText(str(self.countdown_val))
        self.countdown_timer.start(1000)
    
    def on_price_2_clicked(self):
        """Override - Không dùng trong free mode."""
        pass
    
    def on_price_4_clicked(self):
        """Override - Không dùng trong free mode."""
        pass
    
    def show_qr_payment(self):
        """Override - Bỏ qua QR payment, chuyển thẳng sang chụp."""
        self.start_free_capture()
    
    def on_payment_received(self):
        """Override - Không cần kiểm tra thanh toán."""
        pass
    
    def on_payment_error(self, error_msg):
        """Override - Không có lỗi thanh toán trong free mode."""
        pass


def main():
    """Entry point cho chế độ FREE."""
    
    # Banner
    print("\n" + "="*60)
    print("🎉 PHOTOBOOTH - CHẾ ĐỘ MIỄN PHÍ")
    print("="*60)
    print("✅ Không cần thanh toán")
    print("✅ Bấm 'Bắt đầu' để chụp ảnh ngay")
    print("✅ Mặc định: 4 ảnh")
    print("="*60 + "\n")
    
    # Tạo QApplication
    app = QApplication(sys.argv)
    
    # Đảm bảo thư mục tồn tại
    ensure_directories()
    
    # Load config (vẫn cần cho Cloudinary, camera, etc.)
    if not load_config():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Thiếu cấu hình")
        msg.setText("Không tìm thấy file config.json")
        msg.setInformativeText(
            "Vui lòng tạo file config.json theo mẫu config.example.json\n\n"
            "Lưu ý: Chế độ FREE vẫn cần config cho:\n"
            "- Cloudinary upload\n"
            "- Camera settings\n"
            "- Các cấu hình khác"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        return 1
    
    # Tạo và hiển thị cửa sổ FREE MODE
    window = FreePhotobooth()
    window.show()
    
    # Chạy app
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
