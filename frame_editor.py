import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSlider, QGroupBox, QComboBox, 
                             QPushButton, QFrame, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, QSize, QPoint, QRect
from PyQt5.QtGui import QImage, QPixmap, QFont, QPainter, QPen, QColor

# Import default configs
try:
    import frame_config
    from frame_config import LAYOUT_1x2, LAYOUT_2x1, LAYOUT_2x2, LAYOUT_4x1
    DEFAULT_CONFIGS = {
        "1x2": LAYOUT_1x2,
        "2x1": LAYOUT_2x1,
        "2x2": LAYOUT_2x2,
        "4x1": LAYOUT_4x1
    }
except:
    DEFAULT_CONFIGS = {
        "1x2": {"CANVAS_W": 1280, "CANVAS_H": 720, "PAD_TOP": 50, "PAD_BOTTOM": 50, "PAD_LEFT": 50, "PAD_RIGHT": 50, "GAP": 20},
        "2x1": {"CANVAS_W": 640, "CANVAS_H": 900, "PAD_TOP": 20, "PAD_BOTTOM": 50, "PAD_LEFT": 25, "PAD_RIGHT": 25, "GAP": 20},
        "2x2": {"CANVAS_W": 1280, "CANVAS_H": 720, "PAD_TOP": 40, "PAD_BOTTOM": 40, "PAD_LEFT": 40, "PAD_RIGHT": 40, "GAP": 20},
        "4x1": {"CANVAS_W": 640, "CANVAS_H": 1600, "PAD_TOP": 20, "PAD_BOTTOM": 250, "PAD_LEFT": 10, "PAD_RIGHT": 10, "GAP": 25}
    }

class DraggableLabel(QLabel):
    """Màn hình preview có thể kéo thả các ô ảnh."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor = parent
        self.selected_slot_idx = -1
        self.dragging = False
        self.resizing = False
        self.last_pos = QPoint()
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if not self.editor.is_custom_mode: return
        pos = event.pos()
        scaled_pos = self.to_canvas_coords(pos)
        
        # Check if clicking a slot (handle resize corner first)
        for i, slot in enumerate(self.editor.slots):
            rect = QRect(*slot)
            # Resize handle (bottom right)
            resize_rect = QRect(rect.right()-30, rect.bottom()-30, 40, 40)
            if resize_rect.contains(scaled_pos):
                self.selected_slot_idx = i
                self.resizing = True
                self.last_pos = scaled_pos
                self.update()
                return
                
            if rect.contains(scaled_pos):
                self.selected_slot_idx = i
                self.dragging = True
                self.last_pos = scaled_pos
                self.update()
                return
        
        self.selected_slot_idx = -1
        self.update()

    def mouseMoveEvent(self, event):
        if not self.editor.is_custom_mode: return
        pos = event.pos()
        scaled_pos = self.to_canvas_coords(pos)
        
        if self.selected_slot_idx != -1:
            diff = scaled_pos - self.last_pos
            x, y, w, h = self.editor.slots[self.selected_slot_idx]
            
            if self.resizing:
                self.editor.slots[self.selected_slot_idx] = (x, y, max(50, w + diff.x()), max(50, h + diff.y()))
            elif self.dragging:
                self.editor.slots[self.selected_slot_idx] = (x + diff.x(), y + diff.y(), w, h)
                
            self.last_pos = scaled_pos
            self.editor.update_preview()
            self.editor.update_code_display()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False

    def to_canvas_coords(self, pos):
        """Chuyển tọa độ từ Label sang tọa độ Canvas thực tế một cách chính xác."""
        # Kích thước thực tế của Canvas từ config
        CW = self.editor.config["CANVAS_W"]
        CH = self.editor.config["CANVAS_H"]
        
        # Kích thước của widget Label hiện tại
        LW = self.width()
        LH = self.height()
        
        # Tính toán tỷ lệ scale mà Qt sử dụng cho KeepAspectRatio
        # (Nó khớp với logic .scaled(LW-20, LH-20, Qt.KeepAspectRatio))
        scale = min((LW - 20) / CW, (LH - 20) / CH)
        
        # Kích thước của ảnh sau khi scale hiển thị trên màn hình
        display_w = CW * scale
        display_h = CH * scale
        
        # Lề đen xung quanh ảnh (vì ảnh được căn giữa trong Label)
        offset_x = (LW - display_w) / 2
        offset_y = (LH - display_h) / 2
        
        # Công thức: (Tọa độ chuột - Lề) / Tỷ lệ scale = Tọa độ Canvas thực
        canvas_x = (pos.x() - offset_x) / scale
        canvas_y = (pos.y() - offset_y) / scale
        
        return QPoint(int(canvas_x), int(canvas_y))

class FrameEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎨 Photobooth Frame EDITOR - Custom Layout Mode")
        self.resize(1400, 950)
        self.setStyleSheet("background-color: #1a1a2e; color: white;")

        # Current state
        self.current_layout_type = "4x1"
        self.is_custom_mode = False
        self.config = DEFAULT_CONFIGS[self.current_layout_type].copy()
        self.slots = [] # List of (x, y, w, h) for custom mode
        self.photo_ratio = 1.5 

        self.init_ui()
        self.update_preview()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_vbox = QVBoxLayout(central_widget)

        # --- TOP BAR ---
        top_bar = QFrame()
        top_bar.setStyleSheet("background-color: #16213e; border-bottom: 2px solid #709a8a;")
        top_bar.setFixedHeight(70)
        top_layout = QHBoxLayout(top_bar)
        
        lbl_select = QLabel("KIỂU LƯỚI:")
        lbl_select.setFont(QFont("Arial", 12, QFont.Bold))
        top_layout.addWidget(lbl_select)

        self.combo_layout = QComboBox()
        self.combo_layout.addItems(["1x2", "2x1", "2x2", "4x1", "CUSTOM"])
        self.combo_layout.setCurrentText(self.current_layout_type)
        self.combo_layout.setFixedWidth(150)
        self.combo_layout.setStyleSheet("background-color: #709a8a; color: white; padding: 8px; font-weight: bold; border-radius: 5px;")
        self.combo_layout.currentTextChanged.connect(self.change_layout_type)
        top_layout.addWidget(self.combo_layout)
        
        top_layout.addStretch()
        
        self.btn_add_slot = QPushButton("➕ THÊM Ô ẢNH")
        self.btn_add_slot.setStyleSheet("background-color: #4361ee; color: white; font-weight: bold; padding: 10px 20px; border-radius: 5px;")
        self.btn_add_slot.clicked.connect(self.add_custom_slot)
        self.btn_add_slot.hide()
        top_layout.addWidget(self.btn_add_slot)

        btn_gen = QPushButton("🛠️ TẠO FILE KHUNG")
        btn_gen.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold; padding: 10px; margin-left:10px;")
        btn_gen.clicked.connect(self.run_frame_gen)
        top_layout.addWidget(btn_gen)

        main_vbox.addWidget(top_bar)

        # --- CONTENT ---
        content_layout = QHBoxLayout()
        
        # LEFT PANEL
        left_panel = QWidget()
        left_panel.setFixedWidth(380)
        self.left_vbox = QVBoxLayout(left_panel)
        self.setup_controls()
        
        self.code_display = QTextEdit()
        self.code_display.setReadOnly(False) # Cho phép copy
        self.code_display.setStyleSheet("background-color: #0f172a; color: #10b981; font-family: 'Consolas'; font-size: 11px; border: 1px solid #334155;")
        self.left_vbox.addWidget(QLabel("MÃ CẤU HÌNH (Copy vào frame_config.py):"))
        self.left_vbox.addWidget(self.code_display)
        
        content_layout.addWidget(left_panel)

        # RIGHT PREVIEW
        self.preview_label = DraggableLabel(self)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #000; border: 2px solid #709a8a; border-radius: 10px;")
        content_layout.addWidget(self.preview_label, stretch=2)

        main_vbox.addLayout(content_layout)

    def setup_controls(self):
        # Clear old controls if any
        # (Simplified: assumes setup once)
        self.create_control_group(self.left_vbox, "KÍCH THƯỚC CANVAS", {
            "CANVAS_W": (400, 2500, "Rộng"),
            "CANVAS_H": (400, 2500, "Cao")
        })
        
        self.pad_group = self.create_control_group(self.left_vbox, "BÌ & KHOẢNG CÁCH", {
            "PAD_TOP": (0, 500, "Trên"),
            "PAD_BOTTOM": (0, 500, "Dưới"),
            "PAD_LEFT": (0, 500, "Trái"),
            "PAD_RIGHT": (0, 500, "Phải"),
            "GAP": (0, 200, "Khoảng cách")
        })

    def create_control_group(self, parent_layout, title, controls):
        group = QGroupBox(title)
        group.setStyleSheet("QGroupBox { font-weight: bold; color: #709a8a; border: 1px solid #334155; margin-top: 10px; padding: 10px; }")
        layout = QVBoxLayout(group)

        for key, (min_v, max_v, label_text) in controls.items():
            h_layout = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(80)
            
            val_lbl = QLabel()
            val_lbl.setFixedWidth(40)
            val_lbl.setAlignment(Qt.AlignRight)
            
            slider = QSlider(Qt.Horizontal)
            slider.setRange(min_v, max_v)
            val = self.config.get(key, 50)
            slider.setValue(val)
            val_lbl.setText(str(val))
            
            slider.valueChanged.connect(lambda v, k=key, l=val_lbl: self.on_slider_change(k, v, l))
            
            h_layout.addWidget(lbl)
            h_layout.addWidget(slider)
            h_layout.addWidget(val_lbl)
            layout.addLayout(h_layout)

        parent_layout.addWidget(group)
        return group

    def on_slider_change(self, key, value, label):
        self.config[key] = value
        label.setText(str(value))
        self.update_preview()
        self.update_code_display()

    def change_layout_type(self, text):
        self.current_layout_type = text
        self.is_custom_mode = (text == "CUSTOM")
        
        if self.is_custom_mode:
            self.btn_add_slot.show()
            self.pad_group.hide()
            if not self.slots:
                self.slots = [(100, 100, 400, 300)]
        else:
            self.btn_add_slot.hide()
            self.pad_group.show()
            self.config = DEFAULT_CONFIGS.get(text, LAYOUT_1x2).copy()
        
        self.update_preview()
        self.update_code_display()

    def add_custom_slot(self):
        self.slots.append((150, 150, 400, 300))
        self.update_preview()
        self.update_code_display()

    def update_code_display(self):
        if self.is_custom_mode:
            code = "\"Custom_Layout\": {\n"
            code += f"    \"CANVAS_W\": {self.config['CANVAS_W']},\n"
            code += f"    \"CANVAS_H\": {self.config['CANVAS_H']},\n"
            code += "    \"SLOTS\": [\n"
            for i, (x, y, w, h) in enumerate(self.slots):
                comma = "," if i < len(self.slots)-1 else ""
                code += f"        ({x}, {y}, {w}, {h}){comma}\n"
            code += "    ]\n}"
        else:
            code = f"LAYOUT_{self.current_layout_type} = {{\n"
            for k, v in self.config.items():
                code += f"    \"{k}\": {v},\n"
            code += "}"
        self.code_display.setText(code)

    def update_preview(self):
        w, h = self.config["CANVAS_W"], self.config["CANVAS_H"]
        canvas = np.zeros((h, w, 3), dtype=np.uint8) + 30 # Thẳng màu nền tối
        
        # Vẽ vùng Padding (dành cho chế độ thường)
        if not self.is_custom_mode:
            pt, pb, pl, pr = self.config["PAD_TOP"], self.config["PAD_BOTTOM"], self.config["PAD_LEFT"], self.config["PAD_RIGHT"]
            gap = self.config["GAP"]
            
            # Tính toán các ô ảnh tự động
            avail_w = w - pl - pr
            avail_h = h - pt - pb
            
            slots = []
            if self.current_layout_type == "1x2":
                sw, sh = avail_w, (avail_h - gap) // 2
                slots = [(pl, pt), (pl, pt + sh + gap)]
            elif self.current_layout_type == "2x1":
                sw, sh = (avail_w - gap) // 2, avail_h
                slots = [(pl, pt), (pl + sw + gap, pt)]
            elif self.current_layout_type == "2x2":
                sw, sh = (avail_w - gap) // 2, (avail_h - gap) // 2
                slots = [(pl, pt), (pl+sw+gap, pt), (pl, pt+sh+gap), (pl+sw+gap, pt+sh+gap)]
            elif self.current_layout_type == "4x1":
                sw, sh = avail_w, (avail_h - 3*gap) // 4
                for i in range(4): slots.append((pl, pt + i*(sh+gap)))
            
            for i, (sx, sy) in enumerate(slots):
                cv2.rectangle(canvas, (sx, sy), (sx + sw, sy + sh), (112, 154, 112), -1)
                cv2.rectangle(canvas, (sx, sy), (sx + sw, sy + sh), (255, 255, 255), 2)
                cv2.putText(canvas, f"Photo {i+1}", (sx+20, sy+50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 3)
        else:
            # Chế độ CUSTOM: Vẽ các ô từ self.slots
            for i, (sx, sy, sw, sh) in enumerate(self.slots):
                # Màu Sage Green
                color = (138, 154, 112) # BGR
                if i == self.preview_label.selected_slot_idx:
                    color = (255, 165, 0) # Màu cam khi chọn
                
                cv2.rectangle(canvas, (sx, sy), (sx + sw, sy + sh), color, -1)
                cv2.rectangle(canvas, (sx, sy), (sx + sw, sy + sh), (255, 255, 255), 3)
                cv2.putText(canvas, f"P{i+1}", (sx+10, sy+40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
                
                # Nút resize nhỏ ở góc
                cv2.rectangle(canvas, (sx+sw-30, sy+sh-30), (sx+sw, sy+sh), (255,255,255), -1)

        # Convert to QPixmap
        h_c, w_c, ch = canvas.shape
        bytes_per_line = ch * w_c
        qt_img = QImage(canvas.data, w_c, h_c, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        
        view_w = self.preview_label.width() or 800
        view_h = self.preview_label.height() or 600
        pixmap = QPixmap.fromImage(qt_img).scaled(view_w-20, view_h-20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(pixmap)

    def run_frame_gen(self):
        """Chạy script tạo file khung ảnh."""
        try:
            import frame_config
            frame_config.generate_frame_templates()
            QMessageBox.information(self, "Thành công", "Đã tạo/cập nhật các file khung ảnh trong thư mục /templates")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tạo file khung: {e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_preview()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = FrameEditor()
    editor.show()
    sys.exit(app.exec_())
