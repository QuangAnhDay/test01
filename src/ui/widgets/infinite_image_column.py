import os
import random
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QPainterPath


class _ScrollingColumn(QWidget):
    """Một cột ảnh cuộn liên tục theo chiều dọc với chiều cao biến đổi (Masonry)."""

    def __init__(self, photo_paths, col_width, spacing=-2,
                 scroll_speed=1, border_radius=15, parent=None):
        super().__init__(parent)
        self.photo_paths = photo_paths
        self.col_width = col_width
        self.spacing = spacing
        self.scroll_speed = scroll_speed
        self.border_radius = border_radius
        self.scroll_offset = 0

        self.setFixedWidth(col_width)

        # Cache ảnh
        self._pixmaps = []
        self._heights = []
        self._raw_pixmaps = []
        
        self._load_pixmaps()

    def _load_pixmaps(self):
        """Load ảnh gốc vào cache."""
        self._raw_pixmaps = []
        for path in self.photo_paths:
            if not path or not os.path.exists(path):
                continue
            pix = QPixmap(path)
            if not pix.isNull():
                self._raw_pixmaps.append(pix)
        
        self.update_column_width(self.col_width)

    def update_column_width(self, new_width):
        """Tính toán lại toàn bộ ảnh khi chiều rộng cột thay đổi (Masonry)."""
        self.col_width = max(new_width, 10)
        self.setFixedWidth(self.col_width)
        self._pixmaps = []
        self._heights = []
        
        for pix in self._raw_pixmaps:
            scaled = pix.scaledToWidth(self.col_width, Qt.SmoothTransformation)
            self._pixmaps.append(scaled)
            self._heights.append(scaled.height())
            
        # Tính lại tổng chiều cao block
        self._block_height = sum(h + self.spacing for h in self._heights)
        if self._block_height <= 0:
            self._block_height = 1
        self.update()

    def advance_scroll(self):
        """Tiến offset scroll 1 bước."""
        self.scroll_offset += self.scroll_speed
        if self._block_height > 0:
            self.scroll_offset %= self._block_height
        self.update()

    def paintEvent(self, event):
        """Vẽ các ảnh với chiều cao biến đổi, nối tiếp nhau khít."""
        if not self._pixmaps:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        widget_h = self.height()
        
        # Vẽ đủ ảnh để lấp đầy viewport
        for repeat in range(-1, 2):
            current_y = (repeat * self._block_height) - self.scroll_offset
            for pix, h in zip(self._pixmaps, self._heights):
                # Chỉ vẽ nếu trong viewport (có buffer)
                if current_y + h >= -100 and current_y <= widget_h + 100:
                    painter.save()
                    path = QPainterPath()
                    path.addRoundedRect(
                        0, current_y, float(self.col_width), float(h),
                        float(self.border_radius), float(self.border_radius)
                    )
                    painter.setClipPath(path)
                    painter.drawPixmap(0, int(current_y), pix)
                    painter.restore()
                
                current_y += (h + self.spacing)

        painter.end()


class InfiniteImageColumnWidget(QWidget):
    """Widget hiển thị nhiều cột ảnh cuộn liên tục với phong cách Masonry khít."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.photo_paths = []
        self.columns = []

        self.setMinimumWidth(400)

        # Load ảnh
        self._load_photos()

        # Tạo layout cho các cột
        self._spacing_h = 20 # Khoảng cách ngang (20px)
        self._spacing_v = -2 # Ép khít hơn nữa (overlap 2px) để xóa bỏ vạch trắng li ti giữa các ảnh
        
        self._main_layout = QHBoxLayout(self)
        self._main_layout.setContentsMargins(20, 20, 20, 20)
        self._main_layout.setSpacing(20)

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
            r"D:\photobooth2\public\sample_photos\vertical", # Thêm thư mục chứa ảnh dọc
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
        """Tạo 4 cột ảnh với ảnh và tốc độ khác nhau để trông 'khít' hơn."""
        # Xóa cột cũ nếu có
        for col in self.columns:
            col.deleteLater()
        self.columns = []

        if not self.photo_paths:
            return

        # Trộn ảnh và chia cho 3 cột (giảm số cột để ảnh to hơn)
        photos = list(self.photo_paths)
        random.shuffle(photos)

        # Chia ảnh cho từng cột
        num_cols = 3
        col_photos = []
        for i in range(num_cols):
            col_photos.append(photos[i::num_cols] * 3)

        # Cấu hình tốc độ cuộn cho 3 cột
        speeds = [1.2, -0.9, 1.0]

        col_width = 250  # Sẽ được tính lại trong resizeEvent

        for photos_list, speed in zip(col_photos, speeds):
            col = _ScrollingColumn(
                photo_paths=photos_list,
                col_width=col_width,
                spacing=self._spacing_v, 
                scroll_speed=speed,
                border_radius=15, # Khôi phục bo góc cho đẹp khi có khoảng cách
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
            col.update_column_width(col_w)
