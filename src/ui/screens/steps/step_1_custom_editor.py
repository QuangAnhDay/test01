# ==========================================
# STEP 1 - CUSTOM EDITOR (Chỉnh sửa tùy chọn)
# ==========================================
"""
Màn hình cho phép người dùng tự điều chỉnh vị trí và tỷ lệ các ô ảnh
sau khi chọn "Dạng Custom".
"""

import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMessageBox, QSlider, QGroupBox,
                             QComboBox, QLineEdit, QSpinBox, QGridLayout)
from PyQt5.QtCore import Qt, QPoint, QRect, QSize, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont

# Tỉ lệ mặc định (sẽ được ghi đè bởi CustomEditorLogic)
DEFAULT_ASPECT_RATIO = (4, 3)  

class InteractiveCanvas(QLabel):
    """Màn hình preview có thể kéo thả các ô ảnh trực quan."""
    def __init__(self, parent_step):
        super().__init__()
        self.step = parent_step
        self.selected_idx = -1
        self.dragging = False
        self.resizing = False
        self.last_pos = QPoint()
        
        self.setMouseTracking(True)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: #000; border: 4px solid #4361ee; border-radius: 15px;")

    def mousePressEvent(self, event):
        pos = event.pos()
        scaled_pos = self.to_canvas_coords(pos)

        # Kiểm tra click vào ô ảnh nào
        for i, slot in enumerate(self.step.temp_slots):
            rect = QRect(*slot[:4])
            # Resize handle ở góc dưới phải
            resize_rect = QRect(rect.right()-40, rect.bottom()-40, 50, 50)
            if resize_rect.contains(scaled_pos):
                self.selected_idx = i
                self.resizing = True
                self.last_pos = scaled_pos
                self.update_ui()
                return
            if rect.contains(scaled_pos):
                self.selected_idx = i
                self.dragging = True
                self.last_pos = scaled_pos
                self.update_ui()
                return

        self.selected_idx = -1
        self.update_ui()

    def mouseMoveEvent(self, event):
        if self.selected_idx == -1: return
        if not (self.dragging or self.resizing): return

        # Kiểm tra an toàn chỉ số index
        if self.selected_idx >= len(self.step.temp_slots):
            self.selected_idx = -1
            return

        pos = event.pos()
        scaled_pos = self.to_canvas_coords(pos)
        diff = scaled_pos - self.last_pos
        
        x, y, w, h, *rot = self.step.temp_slots[self.selected_idx]
        rotation = rot[0] if rot else 0

        if self.resizing:
            # Sử dụng tỉ lệ từ logic (đã hỗ trợ xoay)
            ratio = self.step.get_aspect_ratio_for_slot(rotation)
            new_w = max(120, w + diff.x())
            new_h = int(new_w * ratio[1] / ratio[0])
            self.step.temp_slots[self.selected_idx] = (x, y, new_w, new_h, rotation)
        elif self.dragging:
            self.step.temp_slots[self.selected_idx] = (x + diff.x(), y + diff.y(), w, h, rotation)

        self.last_pos = scaled_pos
        self.update_ui()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False

    def to_canvas_coords(self, pos):
        CW, CH = self.step.canvas_w, self.step.canvas_h
        LW, LH = self.width(), self.height()
        scale = min((LW - 40) / CW, (LH - 40) / CH)
        offset_x = (LW - CW * scale) / 2
        offset_y = (LH - CH * scale) / 2
        return QPoint(int((pos.x() - offset_x) / scale), int((pos.y() - offset_y) / scale))

    def update_ui(self):
        self.step.update_preview()



# Kích thước canvas cố định theo loại khung
CANVAS_SIZES = {
    "vertical": (600, 1800),   # Khung dọc: 600 x 1800 px
    "custom":   (1210, 1810),  # Khung custom: 1210 x 1810 px
}


def _generate_unique_layout_name():
    """Tạo tên layout mặc định duy nhất (Custom_1, Custom_2, ...)."""
    from src.shared.types.models import load_custom_layouts
    existing = load_custom_layouts()
    i = 1
    while True:
        candidate = f"Custom_{i}"
        if candidate not in existing:
            return candidate
        i += 1


def create_custom_editor_screen(app):
    """Màn hình công cụ dành cho ADMIN: Thiết kế bộ khung ảnh mới."""
    screen = QWidget()
    screen_layout = QVBoxLayout(screen)
    screen_layout.setContentsMargins(30, 30, 30, 30)
    screen_layout.setSpacing(20)

    # --- TOP BAR ---
    top_bar = QHBoxLayout()
    title = QLabel("🛠️ ADMIN: DESIGN NEW LAYOUT")
    title.setObjectName("TitleLabel")
    title.setStyleSheet("font-family: 'Cooper Black'; font-size: 28px; color: #ffd700;")
    top_bar.addWidget(title)
    top_bar.addStretch()
    
    btn_add = QPushButton("➕ ADD SLOT")
    btn_add.setStyleSheet("background-color: #FFFFFF; padding: 10px 20px; border-radius: 10px;")
    btn_add.clicked.connect(lambda: app.custom_editor_step.add_slot())
    top_bar.addWidget(btn_add)
    
    btn_clear = QPushButton("🗑️ CLEAR ALL")
    btn_clear.setStyleSheet("background-color: #e94560; padding: 10px 20px; border-radius: 10px; margin-left:10px;")
    btn_clear.clicked.connect(lambda: app.custom_editor_step.clear_slots())
    top_bar.addWidget(btn_clear)

    # Nút Xoay màn hình / camera
    btn_rotate_canvas = QPushButton("🔄 ROTATE CANVAS")
    btn_rotate_canvas.setToolTip("Xoay toàn bộ khổ giấy (Ngang/Dọc)")
    btn_rotate_canvas.setStyleSheet("background-color: #fb8500; padding: 10px 20px; border-radius: 10px; margin-left:10px; font-weight: bold;")
    btn_rotate_canvas.clicked.connect(lambda: app.custom_editor_step.toggle_rotation())
    top_bar.addWidget(btn_rotate_canvas)

    # Nút Xoay ẢNH (Chỉ xoay ô đang chọn)
    btn_rotate_photo = QPushButton("📸 ROTATE PHOTO")
    btn_rotate_photo.setToolTip("Xoay hướng ảnh trong Ô đang chọn (Dọc <=> Ngang)")
    btn_rotate_photo.setStyleSheet("background-color: #4361ee; color: white; padding: 10px 20px; border-radius: 10px; margin-left:10px; font-weight: bold;")
    btn_rotate_photo.clicked.connect(lambda: app.custom_editor_step.toggle_slot_rotation())
    top_bar.addWidget(btn_rotate_photo)

    # Nút bật/tắt lưới căn chỉnh
    btn_grid = QPushButton("📐 GRID")
    btn_grid.setCheckable(True)
    btn_grid.setChecked(True)
    btn_grid.setStyleSheet(
        "QPushButton { background-color: #06d6a0; padding: 10px 20px; border-radius: 10px; margin-left:10px; color: #000; font-weight: bold; }"
        "QPushButton:checked { background-color: #06d6a0; }"
        "QPushButton:!checked { background-color: #4a4a6a; color: #aaa; }"
    )
    btn_grid.clicked.connect(lambda checked: app.custom_editor_step.toggle_grid(checked))
    top_bar.addWidget(btn_grid)

    screen_layout.addLayout(top_bar)

    # --- BODY ---
    body_layout = QHBoxLayout()
    
    # Left Side: Admin Controls with ScrollArea
    scroll_area = QFrame()
    scroll_area.setFixedWidth(400) # Tăng nhẹ chiều rộng sidebar
    scroll_area.setStyleSheet("background-color: #FFFFFF; border-radius: 20px;")
    scroll_layout = QVBoxLayout(scroll_area)
    scroll_layout.setContentsMargins(0, 0, 0, 0)

    from PyQt5.QtWidgets import QScrollArea
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet("border: none; background: transparent;")
    
    controls = QWidget()
    controls.setStyleSheet("background: transparent; color: white;")
    ctrl_layout = QVBoxLayout(controls)
    ctrl_layout.setContentsMargins(15, 15, 15, 15)
    
    ctrl_layout.addSpacing(20)
    lbl_1 = QLabel("1. LAYOUT NAME:")
    lbl_1.setStyleSheet("color: #ffd700; font-weight: bold; font-size: 14px;")
    ctrl_layout.addWidget(lbl_1)
    
    app.admin_layout_name = QLineEdit(_generate_unique_layout_name())
    app.admin_layout_name.setStyleSheet("background: #000; color: #06d6a0; border: 1px solid #4361ee; padding: 10px; font-size: 18px;")
    ctrl_layout.addWidget(app.admin_layout_name)
    
    ctrl_layout.addSpacing(15)
    lbl_2 = QLabel("2. CATEGORY:")
    lbl_2.setStyleSheet("color: #ffd700; font-weight: bold; font-size: 14px;")
    ctrl_layout.addWidget(lbl_2)
    
    app.admin_layout_group = QComboBox()
    app.admin_layout_group.addItem("🎞️ Strip (Vertical) — 600×1800", "vertical")
    app.admin_layout_group.addItem("🎨 Custom Frame — 1210×1810", "custom")
    app.admin_layout_group.setStyleSheet("background: #1a1a2e; color: #fff; padding: 10px; border: 1px solid #4361ee;")
    ctrl_layout.addWidget(app.admin_layout_group)

    # Hiển thị kích thước canvas hiện tại (chỉ đọc)
    ctrl_layout.addSpacing(20)
    lbl_3 = QLabel("3. CANVAS SIZE (FIXED):")
    lbl_3.setStyleSheet("color: #ffd700; font-weight: bold; font-size: 14px;")
    ctrl_layout.addWidget(lbl_3)

    app.admin_canvas_size_label = QLabel("600 × 1800 px")
    app.admin_canvas_size_label.setAlignment(Qt.AlignCenter)
    app.admin_canvas_size_label.setStyleSheet(
        "color: #06d6a0; font-size: 22px; font-weight: bold; "
        "background: #000; border: 1px solid #4361ee; padding: 12px; border-radius: 8px;"
    )
    ctrl_layout.addWidget(app.admin_canvas_size_label)

    lbl_fixed_note = QLabel("⚠️ Canvas size is fixed based on category\nto ensure compatibility with the printer.")
    lbl_fixed_note.setStyleSheet("color: #ff6b6b; font-size: 11px; font-style: italic;")
    lbl_fixed_note.setWordWrap(True)
    ctrl_layout.addWidget(lbl_fixed_note)
    
    ctrl_layout.addSpacing(20)
    lbl_note = QLabel(
        "💡 Note:\n"
        "- Left click: Move slot\n"
        "- Drag white corner: Resize (keep 4:3)\n"
        "- Button 📐: Toggle grid"
    )
    lbl_note.setStyleSheet("color: #a8dadc; font-size: 12px; font-style: italic;")
    ctrl_layout.addWidget(lbl_note)

    # Label hiển thị thông tin ô đang chọn
    app.admin_slot_info_label = QLabel("No slot selected")
    app.admin_slot_info_label.setAlignment(Qt.AlignCenter)
    app.admin_slot_info_label.setStyleSheet(
        "color: #ffd700; font-size: 12px; "
        "background: #0d1b2a; border: 1px solid #4361ee; padding: 8px; border-radius: 6px; margin-top: 10px;"
    )
    app.admin_slot_info_label.setWordWrap(True)
    ctrl_layout.addWidget(app.admin_slot_info_label)

    # --- Bảng điều khiển tinh chỉnh Pixel ---
    precision_group = QGroupBox("🎯 PIXEL PRECISION")
    precision_group.setStyleSheet("margin-top: 10px; color: #06d6a0;")
    precision_layout = QGridLayout(precision_group)
    precision_layout.setSpacing(10)

    lbl_x = QLabel("X:")
    app.spin_x = QSpinBox()
    app.spin_x.setRange(-2000, 4000)
    app.spin_x.setStyleSheet("background: #000; color: #fff; padding: 5px;")
    
    lbl_y = QLabel("Y:")
    app.spin_y = QSpinBox()
    app.spin_y.setRange(-2000, 4000)
    app.spin_y.setStyleSheet("background: #000; color: #fff; padding: 5px;")

    lbl_w = QLabel("Width:")
    app.spin_w = QSpinBox()
    app.spin_w.setRange(50, 4000)
    app.spin_w.setStyleSheet("background: #000; color: #fff; padding: 5px;")

    lbl_h = QLabel("Height:")
    app.spin_h = QSpinBox()
    app.spin_h.setRange(50, 4000)
    app.spin_h.setStyleSheet("background: #000; color: #aaa; padding: 5px;") # Cao thường tự tính
    app.spin_h.setReadOnly(True) # Để đảm bảo tỉ lệ 4:3

    precision_layout.addWidget(lbl_x, 0, 0)
    precision_layout.addWidget(app.spin_x, 0, 1)
    precision_layout.addWidget(lbl_y, 0, 2)
    precision_layout.addWidget(app.spin_y, 0, 3)
    precision_layout.addWidget(lbl_w, 1, 0)
    precision_layout.addWidget(app.spin_w, 1, 1)
    precision_layout.addWidget(lbl_h, 1, 2)
    precision_layout.addWidget(app.spin_h, 1, 3)

    # Kết nối sự kiện SpinBox -> Cập nhật layout
    def on_spinner_changed():
        if not hasattr(app, 'custom_editor_step'): return
        idx = app.custom_canvas.selected_idx
        if 0 <= idx < len(app.custom_editor_step.temp_slots):
            # Lấy giá trị từ các spinner
            nx = app.spin_x.value()
            ny = app.spin_y.value()
            nw = app.spin_w.value()

            # Tính nh theo tỉ lệ hiện tại của ô
            slots = app.custom_editor_step.temp_slots
            rot = slots[idx][4] if len(slots[idx]) > 4 else 0
            ratio = app.custom_editor_step.get_aspect_ratio_for_slot(rot)
            nh = int(nw * ratio[1] / ratio[0])
            
            # Cập nhật hiển thị spin_h (chặn signal để tránh đệ quy)
            app.spin_h.blockSignals(True)
            app.spin_h.setValue(nh)
            app.spin_h.blockSignals(False)
            
            # Cập nhật vào data
            app.custom_editor_step.temp_slots[idx] = (nx, ny, nw, nh, rot)
            app.custom_editor_step.update_preview()

    app.spin_x.valueChanged.connect(lambda: on_spinner_changed())
    app.spin_y.valueChanged.connect(lambda: on_spinner_changed())
    app.spin_w.valueChanged.connect(lambda: on_spinner_changed())

    ctrl_layout.addWidget(precision_group)
    
    ctrl_layout.addSpacing(20)
    lbl_manage = QLabel("🗑️ MANAGE / DELETE LAYOUTS:")
    lbl_manage.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 14px; margin-top: 10px;")
    ctrl_layout.addWidget(lbl_manage)

    app.admin_layout_list = QComboBox()
    app.admin_layout_list.setStyleSheet("background: #1a1a2e; color: #fff; padding: 10px; border: 1px solid #ff6b6b;")
    ctrl_layout.addWidget(app.admin_layout_list)

    def refresh_layout_list():
        app.admin_layout_list.clear()
        from src.shared.types.models import load_custom_layouts
        layouts = load_custom_layouts()
        for name in layouts.keys():
            app.admin_layout_list.addItem(name)
    
    app.refresh_admin_layouts = refresh_layout_list
    refresh_layout_list()

    btn_delete = QPushButton("DELETE SELECTED LAYOUT")
    btn_delete.setStyleSheet("""
        QPushButton { background-color: #d32f2f; color: white; padding: 10px; border-radius: 8px; font-weight: bold; margin-top: 5px; }
        QPushButton:hover { background-color: #f44336; }
    """)
    def delete_selected():
        name = app.admin_layout_list.currentText()
        if not name: return
        
        reply = QMessageBox.question(None, "Xác nhận xóa", f"Bạn có chắc muốn xóa vĩnh viễn layout '{name}'?\n(Dữ liệu và file ảnh sẽ bị xóa hoàn toàn)", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            from src.shared.types.models import delete_custom_layout, TEMPLATE_DIR, load_custom_layouts
            cfg = load_custom_layouts().get(name, {})
            group = cfg.get("group", "custom")
            
            if delete_custom_layout(name):
                # Xóa file ảnh PNG
                png_path = os.path.join(TEMPLATE_DIR, group, f"frame_{name}.png")
                if os.path.exists(png_path):
                    try:
                        os.remove(png_path)
                    except: pass
                
                QMessageBox.information(None, "Thành công", f"Đã xóa layout: {name}")
                refresh_layout_list()
            else:
                QMessageBox.critical(None, "Lỗi", "Không thể xóa layout!")

    btn_delete.clicked.connect(delete_selected)
    ctrl_layout.addWidget(btn_delete)

    ctrl_layout.addStretch()
    scroll.setWidget(controls)
    scroll_layout.addWidget(scroll)
    body_layout.addWidget(scroll_area)

    # Right Side: Canvas Designer
    app.custom_editor_step = CustomEditorLogic(app)
    app.custom_canvas = InteractiveCanvas(app.custom_editor_step)
    app.custom_canvas.setMinimumSize(1000, 750) # Tăng kích thước canvas thiết kế
    body_layout.addWidget(app.custom_canvas, stretch=1)

    screen_layout.addLayout(body_layout)

    # --- Callback khi đổi nhóm → tự cập nhật canvas size ---
    def on_group_changed(index):
        group = app.admin_layout_group.currentData()
        w, h = CANVAS_SIZES.get(group, (1210, 1810))
        app.admin_canvas_size_label.setText(f"{w} × {h} px")
        app.custom_editor_step.set_canvas_size(w, h)

    app.admin_layout_group.currentIndexChanged.connect(on_group_changed)
    # Khởi tạo canvas size theo nhóm mặc định (vertical)
    on_group_changed(0)

    # --- BOTTOM BAR ---
    bottom_bar = QHBoxLayout()
    btn_cancel = QPushButton("⬅️ CANCEL")
    btn_cancel.setStyleSheet("background-color: #4a4a6a; padding: 15px 30px;")
    btn_cancel.clicked.connect(lambda: app.reset_all())
    bottom_bar.addWidget(btn_cancel)
    
    bottom_bar.addStretch()
    
    btn_save = QPushButton("💾 SAVE LAYOUT & CREATE TEMPLATE FOLDER 💾")
    btn_save.setObjectName("GreenBtn")
    btn_save.setFixedSize(500, 70)
    btn_save.clicked.connect(lambda: app.custom_editor_step.admin_save_layout())
    bottom_bar.addWidget(btn_save)

    screen_layout.addLayout(bottom_bar)

    app.custom_editor_step.canvas_widget = app.custom_canvas
    return screen

class CustomEditorLogic:
    """Logic xử lý thiết kế layout dành cho Admin."""
    def __init__(self, app):
        self.app = app
        self.canvas_w = 600
        self.canvas_h = 1800
        self.temp_slots = [(100, 100, 400, 300, 0)] # (x, y, w, h, rotation)
        self.canvas_widget = None
        self.show_grid = True  # Lưới căn chỉnh mặc định BẬT
        self.rotation = 0      # 0, 90, 180, 270 (Toàn bộ canvas)

    def get_aspect_ratio_for_slot(self, slot_rotation):
        """Trả về tỉ lệ (w, h) cho từng ô ảnh cụ thể."""
        if slot_rotation % 180 == 90:
            return (3, 4) # Portrait crop
        return (4, 3)    # Landscape

    def toggle_slot_rotation(self):
        """Xoay hướng ảnh cho duy nhất một ô đang được chọn."""
        if not self.canvas_widget or self.canvas_widget.selected_idx == -1:
            QMessageBox.warning(None, "Lỗi", "Vui lòng chọn một ô ảnh trước khi xoay!")
            return
            
        idx = self.canvas_widget.selected_idx
        x, y, w, h, *rot = self.temp_slots[idx]
        current_rot = rot[0] if rot else 0
        new_rot = (current_rot + 90) % 360
        
        # Swap w và h để chuyển dáng ô từ Thẳng <=> Ngang
        new_w, new_h = h, w
        self.temp_slots[idx] = (x, y, new_w, new_h, new_rot)
        self.update_preview()
        
    def toggle_rotation(self):
        """
        Xoay khổ giấy (Canvas) ngang/dọc.
        """
        # 1. Swap kích thước Canvas (Ngang <=> Dọc)
        self.canvas_w, self.canvas_h = self.canvas_h, self.canvas_w
        
        # 2. Cập nhật nhãn hiển thị kích thước canvas trong UI
        if hasattr(self.app, 'admin_canvas_size_label'):
            self.app.admin_canvas_size_label.setText(f"{self.canvas_w} × {self.canvas_h} px")

        # 3. Giữ nguyên hướng và hình dáng ô ảnh
        new_slots = []
        for s in self.temp_slots:
            # Xử lý cả list 4 phần tử (cũ) và 5 phần tử (mới)
            x, y, w, h = s[:4]
            rot = s[4] if len(s) > 4 else 0
            
            new_x, new_y = x, y
            if new_x + w > self.canvas_w: new_x = max(0, self.canvas_w - w)
            if new_y + h > self.canvas_h: new_y = max(0, self.canvas_h - h)
            new_slots.append((new_x, new_y, w, h, rot))
        
        self.temp_slots = new_slots
        self.update_preview()
        
        mode = "KHỔ NGANG (Horizontal)" if self.canvas_w > self.canvas_h else "KHỔ DỌC (Vertical)"
        QMessageBox.information(None, "Xoay Khổ Giấy", f"Đã xoay sang {mode}.\nGiữ nguyên hướng của các ô ảnh.")

    def toggle_grid(self, checked):
        """Bật/tắt hiển thị lưới căn chỉnh."""
        self.show_grid = checked
        self.update_preview()

    def set_canvas_size(self, w, h):
        """Đặt kích thước canvas cố định theo loại khung."""
        self.canvas_w = w
        self.canvas_h = h
        # Đặt lại slot mặc định phù hợp với canvas mới, giữ tỉ lệ
        ratio = (4, 3) # Mặc định bắt đầu là ngang
        default_slot_w = min(350, w - 40)
        default_slot_h = int(default_slot_w * ratio[1] / ratio[0])
        self.temp_slots = [(20, 20, default_slot_w, default_slot_h, 0)]
        
        # Reset selection để tránh IndexError
        if self.canvas_widget:
            self.canvas_widget.selected_idx = -1
            
        self.update_preview()

    def add_slot(self):
        # Tính vị trí slot mới dựa trên canvas hiện tại, mặc định ngang
        ratio = (4, 3)
        offset_y = len(self.temp_slots) * 50
        slot_w = min(400, self.canvas_w - 40)
        slot_h = int(slot_w * ratio[1] / ratio[0])
        self.temp_slots.append((20, 20 + offset_y, slot_w, slot_h, 0))
        self.update_preview()

    def clear_slots(self):
        self.temp_slots = []
        # Reset selection để tránh IndexError
        if self.canvas_widget:
            self.canvas_widget.selected_idx = -1
        self.update_preview()

    def _draw_grid(self, canvas, w, h):
        """Vẽ lưới căn chỉnh lên canvas."""

        # === Helper: vẽ đường nét đứt dọc ===
        def _dashed_vline(x, color, thickness=1, dash=6, gap=6):
            y_pos = 0
            while y_pos < h:
                end_y = min(y_pos + dash, h)
                cv2.line(canvas, (x, y_pos), (x, end_y), color, thickness)
                y_pos += dash + gap

        # === Helper: vẽ đường nét đứt ngang ===
        def _dashed_hline(y, color, thickness=1, dash=6, gap=6):
            x_pos = 0
            while x_pos < w:
                end_x = min(x_pos + dash, w)
                cv2.line(canvas, (x_pos, y), (end_x, y), color, thickness)
                x_pos += dash + gap

        # Màu xanh dương mờ cho tất cả đường lưới
        blue_dim = (140, 80, 50)  # Xanh dương mờ (BGR)

        # --- 1) Lưới ngang dày đặc: chia 50 phần ---
        for i in range(1, 50):
            _dashed_hline(h * i // 50, blue_dim, 1, 4, 4)

        # --- 2) Lưới dọc: chia 24 phần ---
        for i in range(1, 24):
            _dashed_vline(w * i // 24, blue_dim, 1, 4, 4)

        # --- 3) Đường tâm (center lines) — vàng sáng, nét đậm nhất ---
        center_color = (0, 215, 255)  # Vàng (BGR)
        cx, cy = w // 2, h // 2
        _dashed_vline(cx, center_color, 2, 20, 10)
        _dashed_hline(cy, center_color, 2, 20, 10)

    def update_preview(self):
        if not self.canvas_widget: return
        w, h = self.canvas_w, self.canvas_h
        canvas = np.zeros((h, w, 3), dtype=np.uint8) + 40
        
        # Vẽ lưới nếu bật
        if self.show_grid:
            self._draw_grid(canvas, w, h)

        selected_idx = self.canvas_widget.selected_idx if self.canvas_widget else -1
        
        for i, slot in enumerate(self.temp_slots):
            sx, sy, sw, sh = slot[:4]
            rot = slot[4] if len(slot) > 4 else 0
            # Ô đang chọn có viền khác biệt
            if i == selected_idx:
                # Viền ngoài highlight
                cv2.rectangle(canvas, (sx-3, sy-3), (sx+sw+3, sy+sh+3), (67, 97, 238), 3)
                fill_color = (100, 130, 80)
            else:
                fill_color = (138, 154, 112)
            
            cv2.rectangle(canvas, (sx, sy), (sx + sw, sy + sh), fill_color, -1)
            cv2.rectangle(canvas, (sx, sy), (sx + sw, sy + sh), (255, 255, 255), 4)
            
            # Label số thứ tự + kích thước
            cv2.putText(canvas, f"#{i+1}", (sx+15, sy+50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 3)
            
            # Thêm biểu tượng hướng (V = Vertical, H = Horizontal)
            orient = "V" if rot % 180 == 90 else "H"
            orient_color = (100, 255, 100) if orient == "V" else (255, 150, 150)
            cv2.putText(canvas, orient, (sx+sw-40, sy+45), cv2.FONT_HERSHEY_SIMPLEX, 1.0, orient_color, 3)
            
            size_text = f"{sw}x{sh}"
            cv2.putText(canvas, size_text, (sx+15, sy+85), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,200,200), 2)
            
            # Resize corner hint (tam giác nhỏ ở góc dưới phải)
            pts = np.array([
                [sx+sw-35, sy+sh],
                [sx+sw, sy+sh-35],
                [sx+sw, sy+sh]
            ], np.int32)
            cv2.fillPoly(canvas, [pts], (255, 255, 255))

        # Cập nhật label thông tin ô đang chọn
        if hasattr(self.app, 'admin_slot_info_label'):
            if selected_idx >= 0 and selected_idx < len(self.temp_slots):
                s = self.temp_slots[selected_idx]
                sx, sy, sw, sh = s[:4]
                rot = s[4] if len(s) > 4 else 0
                ratio = self.get_aspect_ratio_for_slot(rot)
                mode_str = "DỌC (3:4 crop)" if rot % 180 == 90 else "NGANG (4:3)"
                info = (
                    f"📍 Slot #{selected_idx+1}:  X={sx}, Y={sy}\n"
                    f"📐 Size: {sw} × {sh} px  ({mode_str})"
                )
                self.app.admin_slot_info_label.setText(info)
                
                # Cập nhật các SpinBox (chặn signal để tránh loop)
                if hasattr(self.app, 'spin_x'):
                    self.app.spin_x.blockSignals(True)
                    self.app.spin_y.blockSignals(True)
                    self.app.spin_w.blockSignals(True)
                    self.app.spin_h.blockSignals(True)

                    self.app.spin_x.setValue(sx)
                    self.app.spin_y.setValue(sy)
                    self.app.spin_w.setValue(sw)
                    # Cập nhật spin_h để hiển thị đúng số pixel
                    self.app.spin_h.blockSignals(True)
                    self.app.spin_h.setValue(sh)
                    self.app.spin_h.blockSignals(False)

                    self.app.spin_x.blockSignals(False)
                    self.app.spin_y.blockSignals(False)
                    self.app.spin_w.blockSignals(False)
                    self.app.spin_h.blockSignals(False)
            else:
                self.app.admin_slot_info_label.setText("No slot selected")
                if hasattr(self.app, 'spin_x'):
                    self.app.spin_x.setEnabled(False)
                    self.app.spin_y.setEnabled(False)
                    self.app.spin_w.setEnabled(False)
                
            if selected_idx >= 0 and hasattr(self.app, 'spin_x'):
                self.app.spin_x.setEnabled(True)
                self.app.spin_y.setEnabled(True)
                self.app.spin_w.setEnabled(True)

        qt_img = self.convert_to_qt(canvas)
        pixmap = QPixmap.fromImage(qt_img).scaled(self.canvas_widget.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.canvas_widget.setPixmap(pixmap)

    def convert_to_qt(self, cv_img):
        h, w, ch = cv_img.shape
        bytes_per_line = ch * w
        return QImage(cv_img.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

    def admin_save_layout(self):
        """Lưu layout vừa thiết kế thành file cấu hình chính thức."""
        name = self.app.admin_layout_name.text().strip()
        group = self.app.admin_layout_group.currentData()
        
        if not name:
            QMessageBox.warning(None, "Lỗi", "Vui lòng nhập tên Layout!")
            return
        
        # Đảm bảo có tiền tố Custom_ để nhận diện
        if not name.startswith("Custom_"):
            name = "Custom_" + name
        
        # Kiểm tra trùng tên - hỏi user có muốn ghi đè không
        from src.shared.types.models import save_custom_layout, TEMPLATE_DIR, load_custom_layouts
        existing = load_custom_layouts()
        if name in existing:
            reply = QMessageBox.question(
                None, "Tên đã tồn tại",
                f"Layout \"{name}\" đã tồn tại.\n\n"
                f"Bạn muốn GHI ĐÈ layout cũ không?\n"
                f"(Nhấn No để quay lại đổi tên)",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
            
        layout_config = {
            "CANVAS_W": self.canvas_w,
            "CANVAS_H": self.canvas_h,
            "SLOTS": self.temp_slots,
            "rotation": self.rotation # Lưu hướng xoay
        }
        
        if save_custom_layout(name, layout_config, group=group):
            # Lưu vào thư mục nhóm tương ứng (vertical hoặc custom)
            save_dir = os.path.join(TEMPLATE_DIR, group)
            os.makedirs(save_dir, exist_ok=True)
            
            # Luôn tạo mới/ghi đè template có bố cục (PNG) để cập nhật vị trí các ô
            blank_frame_path = os.path.join(save_dir, f"frame_{name}.png")
            
            # Tạo ảnh RGBA: nền trắng đục (alpha=255)
            template_img = np.ones((self.canvas_h, self.canvas_w, 4), dtype=np.uint8) * 255

            # BƯỚC 1: Vẽ viền đen đậm + nhãn LÊN NỀN TRẮNG trước
            for i, slot in enumerate(self.temp_slots):
                sx, sy, sw, sh = slot[:4]
                rot = slot[4] if len(slot) > 4 else 0
                
                y1, y2 = max(0, sy), min(self.canvas_h, sy + sh)
                x1, x2 = max(0, sx), min(self.canvas_w, sx + sw)

                # Viền đen đậm bao quanh ô (offset ra ngoài 4px)
                bx1, by1 = max(0, x1 - 4), max(0, y1 - 4)
                bx2, by2 = min(self.canvas_w, x2 + 4), min(self.canvas_h, y2 + 4)
                cv2.rectangle(template_img, (bx1, by1), (bx2, by2), (80, 80, 80, 255), 4)

                # Nhãn "Ảnh 1" bên trên viền
                label_y = max(25, by1 - 10)
                mode_txt = "Portrait" if rot % 180 == 90 else "Landscape"
                cv2.putText(template_img, f"Photo {i+1} ({mode_txt})", (bx1, label_y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100, 255), 2)

            # BƯỚC 2: Khoét các ô ảnh thành trong suốt SAU KHI đã vẽ viền
            for slot in self.temp_slots:
                sx, sy, sw, sh = slot[:4]
                y1, y2 = max(0, sy), min(self.canvas_h, sy + sh)
                x1, x2 = max(0, sx), min(self.canvas_w, sx + sw)
                template_img[y1:y2, x1:x2] = [0, 0, 0, 0]

            cv2.imwrite(blank_frame_path, template_img)
            print(f"[INFO] Đã lưu và cập nhật template: {blank_frame_path}")
            
            # Cập nhật danh sách quản lý
            if hasattr(self.app, 'refresh_admin_layouts'):
                self.app.refresh_admin_layouts()
            
            QMessageBox.information(None, "Thành công", 
                f"Đã lưu Layout: {name}.\n\n"
                f"✅ Đã tạo khung trắng sẵn tại:\n{blank_frame_path}\n\n"
                f"💡 Hãy mở file PNG này và vẽ phần bìa/trang trí lên đó.")
            # Cập nhật tên mặc định cho lần tạo tiếp theo
            self.app.admin_layout_name.setText(_generate_unique_layout_name())
            self.app.reset_all()
        else:
            QMessageBox.critical(None, "Lỗi", "Không thể lưu Layout!")

# ==========================================
# KHỐI TEST STANDALONE
# ==========================================
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    # Giả lập đối tượng app
    class MockApp:
        def __init__(self):
            self.admin_layout_name = None
            self.admin_layout_group = None
            self.admin_canvas_size_label = None
            self.admin_slot_info_label = None
            self.spin_x = None
            self.spin_y = None
            self.spin_w = None
            self.spin_h = None
            self.admin_layout_list = None
            self.custom_editor_step = None
            self.custom_canvas = None

        def reset_all(self):
            print("Reset ứng dụng!")
            
        def refresh_admin_layouts(self):
            print("Làm mới danh sách layout!")

    app_qt = QApplication(sys.argv)
    
    # Áp dụng STYLE cho app test
    from src.ui.styles import GLOBAL_STYLESHEET
    app_qt.setStyleSheet(GLOBAL_STYLESHEET)

    mock_app = MockApp()
    window = create_custom_editor_screen(mock_app)
    window.showFullScreen()
    sys.exit(app_qt.exec_())

