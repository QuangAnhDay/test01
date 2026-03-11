# ==========================================
# STEP 6 - TEMPLATE (Chọn khung hình)
# ==========================================
import sys
import os
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QScrollArea, QFrame, QApplication,
                             QScroller, QScrollerProperties)
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QPixmap, QFont, QIcon

class ClickAndDragScrollArea(QScrollArea):
    """ScrollArea hỗ trợ kéo chuột/vuốt mượt mà kiểu điện thoại (Kinetic Scrolling)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("background: transparent; border: none;")

        # Kích hoạt QScroller để vuốt/kéo mượt mà
        scroller = QScroller.scroller(self.viewport())
        scroller.grabGesture(self.viewport(), QScroller.LeftMouseButtonGesture)
        
        # Tinh chỉnh thuộc tính scroller để mượt hơn
        props = scroller.scrollerProperties()
        # Cho phép kéo nhạy hơn
        props.setScrollMetric(QScrollerProperties.DragStartDistance, 0.001)
        props.setScrollMetric(QScrollerProperties.ScrollingCurve, 4) 
        scroller.setScrollerProperties(props)

def create_template_screen(app):
    """
    Màn hình chọn template sử dụng Tọa độ Tuyệt đối (Absolute Positioning).
    Bạn có thể tự do tinh chỉnh vị trí các khối bằng cách thay đổi số X, Y trong setGeometry.
    """
    screen = QWidget()
    screen.setObjectName("templateScreen")
    screen.setFixedSize(1920, 1080)
    screen.setStyleSheet("background-color: #F2E3E5;") # Nền hồng nhạt toàn màn hình
    
    # --- [1] NÚT QUAY LẠI (Góc trên trái) ---
    app.btn_template_back = QPushButton("←", screen)
    # Tinh chỉnh vị trí: setGeometry(X, Y, Rộng, Cao)
    app.btn_template_back.setGeometry(40, 40, 160, 90) 
    app.btn_template_back.setStyleSheet("""
        QPushButton {
            background-color: #FADBDC; color: white;
            font-size: 70px; font-weight: 300;
            border-radius: 30px; border: 5px solid white;
        }
        QPushButton:hover { background-color: #F8B9BC; }
    """)
    if hasattr(app, 'stacked'):
        app.btn_template_back.clicked.connect(lambda: app.stacked.setCurrentIndex(1))
    
    # --- [2] TIÊU ĐỀ CHÍNH ("chọn khung bạn muốn") ---
    title_box = QLabel("chọn khung bạn muốn", screen)
    title_box.setAlignment(Qt.AlignCenter)
    # Tinh chỉnh vị trí: setGeometry(X, Y, Rộng, Cao)
    title_box.setGeometry(435, 40, 450, 85) 
    title_box.setStyleSheet("""
        background-color: #FADBDC; color: white;
        font-family: 'Cooper Black', 'Arial'; font-size: 28px; font-style: italic; font-weight: bold;
        border-radius: 25px;
    """)
    
    # --- [3] TIMER (Đồng hồ đếm ngược) ---
    app.lbl_template_timer = QLabel("60", screen)
    # Tinh chỉnh vị trí: setGeometry(X, Y, Rộng, Cao)
    app.lbl_template_timer.setGeometry(1780, 40, 100, 85)
    app.lbl_template_timer.setStyleSheet("color: white; font-size: 34px; font-weight: bold;")
    app.lbl_template_timer.setAlignment(Qt.AlignCenter)

    # --- [4] KHUNG CHỨA CÁC NÚT LỌC ("khung 3 ảnh" và "khung 4 ảnh") ---
    app.filter_container = QFrame(screen)
    # Tinh chỉnh vị trí: setGeometry(X, Y, Rộng, Cao)
    app.filter_container.setGeometry(40, 160, 1160, 120) 
    app.filter_container.setStyleSheet("background-color: #FADBDC; border-radius: 25px; border: 5px solid white;")
    
    filter_layout = QHBoxLayout(app.filter_container)
    filter_layout.setContentsMargins(5, 5, 60, 15) # Changed left margin from 60 to 20
    filter_layout.setSpacing(63)

    app.btn_filter_3 = QPushButton("khung 3 ảnh")
    app.btn_filter_4 = QPushButton("khung 4 ảnh")
    app.btn_filter_all = QPushButton("tất cả khung") # Nút mới
    
    for btn in [app.btn_filter_3, app.btn_filter_4, app.btn_filter_all]:
        btn.setFixedSize(375, 100)
        btn.setCheckable(True)
        btn.setStyleSheet("""
            QPushButton {
                background-color: white; color: black;
                font-family: 'Cooper Black', 'Arial'; font-size: 26px; font-style: italic; font-weight: bold;
                border-radius: 15px; border: none;
            }
            QPushButton:checked { background-color: #F2BFC1; color: white; }
        """)
        btn.clicked.connect(lambda checked, b=btn: [
            app.btn_filter_3.setChecked(b==app.btn_filter_3), 
            app.btn_filter_4.setChecked(b==app.btn_filter_4),
            app.btn_filter_all.setChecked(b==app.btn_filter_all)
        ])
    
    if hasattr(app, 'filter_templates_by_count'):
        app.btn_filter_3.clicked.connect(lambda: app.filter_templates_by_count(3))
        app.btn_filter_4.clicked.connect(lambda: app.filter_templates_by_count(4))
        app.btn_filter_all.clicked.connect(lambda: app.filter_templates_by_count(0)) # 0 nghĩa là Lấy tất cả
    
    filter_layout.addWidget(app.btn_filter_all) # Cho nút Tất cả lên đầu hoặc cuối tùy ý bạn, mình để ở đầu nhé
    filter_layout.addWidget(app.btn_filter_3)
    filter_layout.addWidget(app.btn_filter_4)
    filter_layout.addStretch()

    # --- [5] KHUNG CHỨA DANH SÁCH TEMPLATE (Hồng lớn) ---
    app.list_container = QFrame(screen)
    # Tinh chỉnh vị trí: setGeometry(X, Y, Rộng, Cao)
    app.list_container.setGeometry(40, 300, 1160, 740) 
    app.list_container.setStyleSheet("background-color: #FADBDC; border-radius: 35px; border: 5px solid white;")
    
    list_inner = QVBoxLayout(app.list_container)
    list_inner.setContentsMargins(20, 20, 20, 20)

    # --- [6] KHU VỰC VUỐT NGANG (Scroll Area) ---
    app.template_scroll_area = ClickAndDragScrollArea()
    app.template_scroll_area.setWidgetResizable(True)
    list_inner.addWidget(app.template_scroll_area)

    app.template_btn_widget = QWidget()
    app.template_btn_widget.setStyleSheet("background: transparent;")
    app.template_btn_layout = QHBoxLayout(app.template_btn_widget) 
    app.template_btn_layout.setSpacing(30)
    app.template_btn_layout.setContentsMargins(15, 15, 15, 15)
    app.template_btn_layout.setAlignment(Qt.AlignLeft)
    
    app.template_scroll_area.setWidget(app.template_btn_widget)

    # --- [7] KHUNG XEM TRƯỚC (Preview Box trắng lớn bên phải) ---
    preview_container = QFrame(screen)
    # Tinh chỉnh vị trí: setGeometry(X, Y, Rộng, Cao)
    preview_container.setGeometry(1240, 40, 640, 840) 
    preview_container.setStyleSheet("background-color: #FADBDC; border-radius: 40px; border: 5px solid white;")
    
    preview_layout = QVBoxLayout(preview_container)
    preview_layout.setContentsMargins(25, 25, 25, 25)

    app.template_preview_label = QLabel()
    app.template_preview_label.setAlignment(Qt.AlignCenter)
    app.template_preview_label.setStyleSheet("background: transparent; border: none;")
    preview_layout.addWidget(app.template_preview_label)

    # --- [8] NÚT CHỤP ẢNH (Góc dưới cùng bên phải) ---
    app.btn_confirm_template = QPushButton("CHỤP ẢNH!", screen)
    # Tinh chỉnh vị trí: setGeometry(X, Y, Rộng, Cao)
    app.btn_confirm_template.setGeometry(1335, 920, 450, 110) 
    app.btn_confirm_template.setStyleSheet("""
        QPushButton {
            background-color: #FADBDC; color: white;
            font-family: 'Cooper Black', 'Arial'; font-size: 38px; font-style: italic; font-weight: bold;
            border-radius: 25px;
        }
        QPushButton:hover { background-color: #F8B9BC; }
    """)
    if hasattr(app, 'handle_template_confirmation'):
        app.btn_confirm_template.clicked.connect(app.handle_template_confirmation)

    return screen

# ==========================================
# KHỐI TEST STANDALONE
# ==========================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    class DummyApp:
        def __init__(self):
            class MockStacked:
                def setCurrentIndex(self, idx):
                    print(f"Chuyển sang Page {idx}")
            self.stacked = MockStacked()
        def filter_templates_by_count(self, count):
            print(f"Lọc template {count} ảnh")
        def handle_template_confirmation(self):
            print("Xác nhận chụp ảnh!")

    dummy = DummyApp()
    window = create_template_screen(dummy)
    
    for i in range(10):
        btn = QPushButton(f"Frame {i}")
        btn.setFixedSize(220, 500)
        btn.setStyleSheet("background-color: transparent; border: none;")
        dummy.template_btn_layout.addWidget(btn)

    # Áp dụng STYLE giống hệt App chính để xem cho chuẩn
    app.setStyleSheet("""
        QMainWindow { background-color: #F5EBEC; }
        QPushButton {
            background-color: #e94560; color: white; border: none;
            border-radius: 15px; padding: 20px 40px; font-size: 22px;
            font-weight: bold; font-family: 'Arial', 'Tahoma', sans-serif;
            min-height: 60px;
        }
        QPushButton:hover { background-color: #ff6b6b; }
    """)
    
    window.showFullScreen()
    sys.exit(app.exec_())
