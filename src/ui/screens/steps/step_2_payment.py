import os
import sys

# === PATH FIX: Cho phép chạy trực tiếp bằng `python step_2_payment.py` ===
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame, QApplication
from PyQt5.QtCore import Qt


def create_payment_screen(app):
    """
    Màn hình QR thanh toán (Step 2) - Phong cách Pink Pastel.
    """
    screen = QWidget()
    screen.setObjectName("paymentScreen")
    screen.setFixedSize(1920, 1080)
    # Mau nen man hinh thanh toan (Hong pastel dam hon)
    screen.setStyleSheet("background-color: #F2E3E5;")

    # --- [1] TIÊU ĐỀ ("THANH TOÁN") ---
    title_box = QLabel("SCAN TO PAY", screen)
    title_box.setAlignment(Qt.AlignCenter)
    title_box.setGeometry(685, 40, 550, 85) 
    title_box.setStyleSheet("""
        /* Mau nen tieu de (Hong nhat) */
        background-color: #FADBDC; color: white;
        font-family: 'Cooper Black', 'Arial'; font-size: 32px; font-style: italic; font-weight: bold;
        border-radius: 25px; border: 5px solid white;
    """)

    # --- [2] KHUNG CHỨA QR (Bên trái) ---
    qr_outer = QFrame(screen)
    qr_outer.setGeometry(200, 180, 700, 700)
    qr_outer.setStyleSheet("background-color: #FADBDC; border-radius: 40px; border: 8px solid white;")
    
    qr_layout = QVBoxLayout(qr_outer)
    qr_layout.setContentsMargins(40, 40, 40, 40)
    qr_layout.setSpacing(20)

    qr_white_bg = QWidget()
    qr_white_bg.setStyleSheet("background-color: white; border-radius: 25px;")
    qr_white_bg.setFixedSize(500, 500)
    qr_white_layout = QVBoxLayout(qr_white_bg)
    qr_white_layout.setAlignment(Qt.AlignCenter)

    app.qr_label = QLabel("⏳ Loading...")
    app.qr_label.setAlignment(Qt.AlignCenter)
    app.qr_label.setFixedSize(450, 450)
    app.qr_label.setStyleSheet("font-size: 24px; color: #333; background: transparent;")
    qr_white_layout.addWidget(app.qr_label)
    qr_layout.addWidget(qr_white_bg, alignment=Qt.AlignCenter)

    app.payment_status_label = QLabel("🔄 Waiting for payment...")
    app.payment_status_label.setAlignment(Qt.AlignCenter)
    app.payment_status_label.setStyleSheet("font-size: 26px; color: white; font-weight: bold; font-style: italic;")
    qr_layout.addWidget(app.payment_status_label)

    # --- [3] KHUNG THÔNG TIN GÓI (Bên phải) ---
    info_outer = QFrame(screen)
    info_outer.setGeometry(950, 180, 770, 700)
    info_outer.setStyleSheet("background-color: #FADBDC; border-radius: 40px; border: 8px solid white;")
    
    info_layout = QVBoxLayout(info_outer)
    info_layout.setContentsMargins(50, 60, 50, 60)
    info_layout.setSpacing(30)

    app.selected_package_label = QLabel("4-Photo Package")
    app.selected_package_label.setStyleSheet("font-size: 34px; font-weight: bold; color: white;")
    app.selected_package_label.setWordWrap(True)
    
    app.transaction_code_label = QLabel("Ref: AB123")
    app.transaction_code_label.setStyleSheet("font-size: 28px; color: white; background-color: rgba(255,255,255,40); border-radius: 15px; padding: 10px;")
    
    app.bank_info_label = QLabel("BIDV - 12345678")
    app.bank_info_label.setStyleSheet("font-size: 24px; color: #FFF0F0;")
    app.bank_info_label.setWordWrap(True)

    info_layout.addWidget(QLabel("📦 SELECTED PACKAGE:"), alignment=Qt.AlignLeft)
    info_layout.addWidget(app.selected_package_label)
    info_layout.addSpacing(20)
    info_layout.addWidget(QLabel("📝 TRANSFER DETAILS:"), alignment=Qt.AlignLeft)
    info_layout.addWidget(app.transaction_code_label)
    info_layout.addSpacing(20)
    info_layout.addWidget(app.bank_info_label)
    info_layout.addStretch()

    # --- [4] NÚT QUAY LẠI (Dưới cùng) ---
    app.btn_back_qr = QPushButton("CANCEL AND GO BACK", screen)
    app.btn_back_qr.setGeometry(685, 920, 550, 100)
    app.btn_back_qr.setStyleSheet("""
        QPushButton {
            /* Mau nen nut quay lai (Trang) */
            background-color: white; 
            /* Mau chu nut quay lai (Hong do) */
            color: #FF7E7E;
            font-family: 'Cooper Black', 'Arial'; font-size: 28px; font-style: italic; font-weight: bold;
            border-radius: 25px; border: 5px solid #FADBDC;
        }
        QPushButton:hover { background-color: #FFF0F0; }
    """)
    app.btn_back_qr.clicked.connect(app.cancel_payment_and_go_back)

    return screen

# ==========================================
# KHỐI TEST STANDALONE
# ==========================================
if __name__ == "__main__":
    app_qt = QApplication(sys.argv)
    
    class DummyApp:
        def __init__(self):
            self.current_transaction_code = "TEST123"
            self.current_amount = 50000
            self.layout_type = "4x1"
            self.selected_frame_count = 4
        def cancel_payment_and_go_back(self):
            print("Hủy thanh toán!")

    dummy = DummyApp()
    
    # Áp dụng STYLE cho app test
    from src.ui.styles import GLOBAL_STYLESHEET
    app_qt.setStyleSheet(GLOBAL_STYLESHEET)

    window = create_payment_screen(dummy)
    
    # Giả lập dữ liệu hiển thị
    dummy.selected_package_label.setText("Gói 4 ảnh - 50,000đ")
    dummy.transaction_code_label.setText("Nội dung: TEST123")
    dummy.bank_info_label.setText("BIDV - 12345678")
    
    window.showFullScreen()
    sys.exit(app_qt.exec_())
