import os
import random
from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QPainterPath


class _ScrollingColumn(QWidget):
    """Một cột ảnh cuộn liên tục theo chiều dọc."""

    def __init__(self, photo_paths, col_width, photo_height, spacing=14,
                 scroll_speed=1, border_radius=14, parent=None):
        super().__init__(parent)
        self.photo_paths = photo_paths
        self.col_width = col_width
        self.photo_height = photo_height
        self.spacing = spacing
        self.scroll_speed = scroll_speed
        self.border_radius = border_radius
        self.scroll_offset = 0

        self.setFixedWidth(col_width)

        # Cache pixmap đã load
        self._pixmaps = []
        self._load_pixmaps()

        # Tính chiều cao 1 block (tất cả ảnh 1 lần)
        self._block_height = len(self._pixmaps) * (self.photo_height + self.spacing)
        if self._block_height <= 0:
            self._block_height = 1

    def _load_pixmaps(self):
        """Load và cache tất cả ảnh cho cột."""
        for path in self.photo_paths:
            if not path or not os.path.exists(path):
                continue
            pixmap = QPixmap(path)
            if pixmap.isNull():
                continue

            # Scale + crop fill
            scaled = pixmap.scaled(
                self.col_width, self.photo_height,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            x_off = (scaled.width() - self.col_width) // 2
            y_off = (scaled.height() - self.photo_height) // 2
            cropped = scaled.copy(x_off, y_off, self.col_width, self.photo_height)
            self._pixmaps.append(cropped)

    def advance_scroll(self):
        """Tiến offset scroll 1 bước."""
        self.scroll_offset += self.scroll_speed
        if self._block_height > 0:
            self.scroll_offset %= self._block_height
        self.update()

    def paintEvent(self, event):
        """Vẽ các ảnh với bo góc, cuộn vô tận."""
        if not self._pixmaps:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        widget_h = self.height()
        item_h = self.photo_height + self.spacing
        n = len(self._pixmaps)

        # Vẽ đủ ảnh để lấp đầy viewport (lặp 3 lần)
        for repeat in range(-1, 3):
            for i, pix in enumerate(self._pixmaps):
                y = (repeat * self._block_height) + (i * item_h) - self.scroll_offset

                # Chỉ vẽ nếu trong viewport
                if y + self.photo_height < -20 or y > widget_h + 20:
                    continue

                painter.save()
                path = QPainterPath()
                path.addRoundedRect(
                    0, y, self.col_width, self.photo_height,
                    self.border_radius, self.border_radius
                )
                painter.setClipPath(path)
                painter.drawPixmap(0, int(y), self.col_width, self.photo_height, pix)
                painter.restore()

        painter.end()


class InfiniteImageColumnWidget(QWidget):
    """Widget hiển thị nhiều cột ảnh cuộn liên tục với tốc độ khác nhau."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.photo_paths = []
        self.columns = []

        self.setMinimumWidth(400)

        # Load ảnh
        self._load_photos()

        # Tạo layout cho các cột
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(14, 14, 14, 14)
        self._main_layout.setSpacing(14)

        self._build_columns()

        # Timer chung để cuộn tất cả cột
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(30)

    def _load_photos(self):
        """Tải danh sách ảnh mẫu từ thư mục."""
        search_dirs = [
            os.path.join(os.path.dirname(__file__), '../../../sample_photos'),
            os.path.join(os.path.dirname(__file__), '../../../public/sample_photos'),
            r"D:\photobooth2\sample_photos",
            r"D:\photobooth2\public\sample_photos",
        ]

        for dir_path in search_dirs:
            abs_path = os.path.abspath(dir_path)
            if os.path.exists(abs_path):
                files = [
                    os.path.join(abs_path, f)
                    for f in sorted(os.listdir(abs_path))
                    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
                ]
                if files:
                    self.photo_paths.extend(files)

        # Loại bỏ trùng
        self.photo_paths = list(dict.fromkeys(self.photo_paths))

    def _build_columns(self):
        """Tạo 3 cột ảnh với ảnh và tốc độ khác nhau."""
        # Xóa cột cũ nếu có
        for col in self.columns:
            col.deleteLater()
        self.columns = []

        if not self.photo_paths:
            return

        # Trộn ảnh và chia cho 3 cột
        photos = list(self.photo_paths)
        random.shuffle(photos)

        # Chia ảnh cho từng cột (nhân đôi để có đủ ảnh cuộn)
        n = len(photos)
        col_photos = [
            (photos[0::3] * 3),  # Cột 1: lấy ảnh 0, 3, 6, ...
            (photos[1::3] * 3),  # Cột 2: lấy ảnh 1, 4, 7, ...
            (photos[2::3] * 3),  # Cột 3: lấy ảnh 2, 5, 8, ...
        ]

        # Cấu hình mỗi cột: (chiều cao ảnh, tốc độ cuộn)
        col_configs = [
            (380, 1.2),   # Cột trái: ảnh cao, cuộn vừa
            (300, -0.8),  # Cột giữa: ảnh vừa, cuộn ngược
            (340, 1.0),   # Cột phải: ảnh trung bình, cuộn xuôi
        ]

        col_width = 250  # Sẽ được điều chỉnh trong resizeEvent

        for i, (photos_list, (ph, speed)) in enumerate(zip(col_photos, col_configs)):
            col = _ScrollingColumn(
                photo_paths=photos_list,
                col_width=col_width,
                photo_height=ph,
                spacing=14,
                scroll_speed=speed,
                border_radius=14,
                parent=self,
            )
            self._main_layout.addWidget(col)
            self.columns.append(col)

    def _tick(self):
        """Cập nhật scroll cho tất cả cột."""
        for col in self.columns:
            col.advance_scroll()

    def resizeEvent(self, event):
        """Cập nhật chiều rộng cột khi resize."""
        super().resizeEvent(event)
        if not self.columns:
            return

        margins = self._main_layout.contentsMargins()
        total_spacing = self._main_layout.spacing() * (len(self.columns) - 1)
        avail_w = self.width() - margins.left() - margins.right() - total_spacing
        col_w = max(avail_w // len(self.columns), 100)

        for col in self.columns:
            col.setFixedWidth(col_w)
