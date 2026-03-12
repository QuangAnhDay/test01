# ==========================================
# CAROUSEL PHOTO WIDGET
# ==========================================
"""
Widget hiển thị ảnh carousel trôi ngang cho màn hình chờ.
"""

import cv2
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from src.utils import convert_cv_qt


class CarouselPhotoWidget(QWidget):
    """Widget hiển thị ảnh carousel trôi từ trái sang phải."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.photos = []
        self.photo_labels = []
        self.current_offset = 0
        self.photo_width = 220
        self.photo_height = 280
        self.spacing = 20
        self.scroll_speed = 2

        self.setMinimumHeight(self.photo_height + 40)

        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.update_scroll)
        self.scroll_timer.start(30)

    def set_photos(self, photo_paths):
        """Đặt danh sách ảnh cho carousel."""
        self.photos = photo_paths
        self.setup_photo_labels()

    def setup_photo_labels(self):
        """Tạo các label ảnh cho carousel."""
        for label in self.photo_labels:
            label.deleteLater()
        self.photo_labels = []

        if not self.photos:
            return

        total_photos = self.photos * 4

        for i, photo_path in enumerate(total_photos):
            label = QLabel(self)
            label.setFixedSize(self.photo_width, self.photo_height)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #2d2d44, stop:1 #1a1a2e);
                    border: 3px solid #4361ee;
                    border-radius: 15px;
                    padding: 5px;
                }
            """)

            img = cv2.imread(photo_path)
            if img is not None:
                qt_img = convert_cv_qt(img)
                scaled = qt_img.scaled(
                    self.photo_width - 16,
                    self.photo_height - 16,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                label.setPixmap(scaled)

            label.show()
            self.photo_labels.append(label)

        self.update_positions()

    def update_positions(self):
        """Cập nhật vị trí các ảnh."""
        if not self.photo_labels:
            return

        y_pos = 20
        for i, label in enumerate(self.photo_labels):
            x_pos = i * (self.photo_width + self.spacing) - self.current_offset
            label.move(int(x_pos), y_pos)

    def update_scroll(self):
        """Cập nhật vị trí scroll."""
        if not self.photo_labels or not self.photos:
            return

        self.current_offset += self.scroll_speed

        single_set_width = len(self.photos) * (self.photo_width + self.spacing)

        if self.current_offset >= single_set_width:
            self.current_offset -= single_set_width
        elif self.current_offset <= 0:
            self.current_offset += single_set_width

        self.update_positions()
