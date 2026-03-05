# ==========================================
# FRAME EDITOR - Thiết kế khung ảnh tùy chỉnh
# ==========================================
"""
Công cụ trực quan để thiết kế layout ảnh:
- Kéo thả ô ảnh (Custom mode)
- Slider chỉnh padding/gap (Default mode)
- Export code và lưu custom layout
"""

import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QSlider, QGroupBox, QComboBox,
                             QPushButton, QFrame, QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, QSize, QPoint, QRect
from PyQt5.QtGui import QImage, QPixmap, QFont, QPainter, QPen, QColor

# Import configs
try:
    from src.shared.types import models as frame_config_module
    from src.shared.types.models import LAYOUT_4x1
    DEFAULT_CONFIGS = {
        "4x1": LAYOUT_4x1
    }
except:
    DEFAULT_CONFIGS = {
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

        for i, slot in enumerate(self.editor.slots):
            rect = QRect(*slot)
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
        """Chuyển tọa độ từ Label sang tọa độ Canvas thực tế."""
        CW = self.editor.config["CANVAS_W"]
        CH = self.editor.config["CANVAS_H"]
        LW = self.width()
        LH = self.height()
        scale = min((LW - 20) / CW, (LH - 20) / CH)
        display_w = CW * scale
        display_h = CH * scale
        offset_x = (LW - display_w) / 2
        offset_y = (LH - display_h) / 2
        canvas_x = (pos.x() - offset_x) / scale
        canvas_y = (pos.y() - offset_y) / scale
        return QPoint(int(canvas_x), int(canvas_y))


class FrameEditor(QMainWindow):
    """Công cụ thiết kế khung ảnh trực quan."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎨 Photobooth Frame EDITOR - Custom Layout Mode")
        self.resize(1400, 950)
        self.setStyleSheet("background-color: #1a1a2e; color: white;")

        self.current_layout_type = "4x1"
        self.is_custom_mode = False
        self.config = DEFAULT_CONFIGS[self.current_layout_type].copy()
        self.slots = []
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
        self.combo_layout.addItems(["4x1", "CUSTOM"])
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

        self.btn_save_custom = QPushButton("💾 LƯU THÀNH MẪU MỚI (CUSTOM)")
        self.btn_save_custom.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 10px 20px; border-radius: 5px; margin-left: 10px;")
        self.btn_save_custom.clicked.connect(self.save_custom_layout_action)
        top_layout.addWidget(self.btn_save_custom)

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
        self.code_display.setReadOnly(False)
        self.code_display.setStyleSheet("background-color: #0f172a; color: #10b981; font-family: 'Consolas'; font-size: 11px; border: 1px solid #334155;")
        self.left_vbox.addWidget(QLabel("MÃ CẤU HÌNH (Copy vào models.py):"))
        self.left_vbox.addWidget(self.code_display)

        content_layout.addWidget(left_panel)

        # RIGHT PREVIEW
        self.preview_label = DraggableLabel(self)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #000; border: 2px solid #709a8a; border-radius: 10px;")
        content_layout.addWidget(self.preview_label, stretch=2)

        main_vbox.addLayout(content_layout)

    def setup_controls(self):
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
            self.config = DEFAULT_CONFIGS.get(text, DEFAULT_CONFIGS["4x1"]).copy()

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
        canvas = np.zeros((h, w, 3), dtype=np.uint8) + 30

        if not self.is_custom_mode:
            slots, sw_default, sh_default = self.calculate_current_slots()
            for i, (sx, sy) in enumerate(slots):
                cv2.rectangle(canvas, (sx, sy), (sx + sw_default, sy + sh_default), (112, 154, 112), -1)
                cv2.rectangle(canvas, (sx, sy), (sx + sw_default, sy + sh_default), (255, 255, 255), 2)
                cv2.putText(canvas, f"Photo {i+1}", (sx+20, sy+50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 3)
        else:
            for i, (sx, sy, sw, sh) in enumerate(self.slots):
                color = (138, 154, 112)
                if i == self.preview_label.selected_slot_idx:
                    color = (255, 165, 0)
                cv2.rectangle(canvas, (sx, sy), (sx + sw, sy + sh), color, -1)
                cv2.rectangle(canvas, (sx, sy), (sx + sw, sy + sh), (255, 255, 255), 3)
                cv2.putText(canvas, f"P{i+1}", (sx+10, sy+40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
                cv2.rectangle(canvas, (sx+sw-30, sy+sh-30), (sx+sw, sy+sh), (255,255,255), -1)

        h_c, w_c, ch = canvas.shape
        bytes_per_line = ch * w_c
        qt_img = QImage(canvas.data, w_c, h_c, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

        view_w = self.preview_label.width() or 800
        view_h = self.preview_label.height() or 600
        pixmap = QPixmap.fromImage(qt_img).scaled(view_w-20, view_h-20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(pixmap)

    def calculate_current_slots(self):
        w, h = self.config["CANVAS_W"], self.config["CANVAS_H"]
        pt, pb, pl, pr = self.config["PAD_TOP"], self.config["PAD_BOTTOM"], self.config["PAD_LEFT"], self.config["PAD_RIGHT"]
        gap = self.config["GAP"]

        avail_w = w - pl - pr
        avail_h = h - pt - pb

        slots = []
        sw, sh = 0, 0

        if self.current_layout_type == "1x2":
            sw, sh = avail_w, (avail_h - gap) // 2
            slots = [(pl, pt, sw, sh), (pl, pt + sh + gap, sw, sh)]
        elif self.current_layout_type == "2x1":
            sw, sh = (avail_w - gap) // 2, avail_h
            slots = [(pl, pt, sw, sh), (pl + sw + gap, pt, sw, sh)]
        elif self.current_layout_type == "2x2":
            sw, sh = (avail_w - gap) // 2, (avail_h - gap) // 2
            slots = [
                (pl, pt, sw, sh), (pl + sw + gap, pt, sw, sh),
                (pl, pt + sh + gap, sw, sh), (pl + sw + gap, pt + sh + gap, sw, sh)
            ]
        elif self.current_layout_type == "4x1":
            sw, sh = avail_w, (avail_h - 3 * gap) // 4
            for i in range(4):
                slots.append((pl, pt + i * (sh + gap), sw, sh))

        if self.is_custom_mode:
            return self.slots, 0, 0
        return [(s[0], s[1]) for s in slots], sw, sh

    def save_custom_layout_action(self):
        """Lưu cấu hình custom, tạo folder và lưu ảnh mold."""
        try:
            from src.shared.types import models as fc_module

            if self.is_custom_mode:
                save_slots = self.slots
            else:
                calculated_slots_info, sw, sh = self.calculate_current_slots()
                save_slots = [(pos[0], pos[1], sw, sh) for pos in calculated_slots_info]

            if not save_slots:
                QMessageBox.warning(self, "Lỗi", "Không có ô ảnh nào để lưu!")
                return

            base_templates_dir = "templates"
            custom_dir = os.path.join(base_templates_dir, "custom")
            os.makedirs(custom_dir, exist_ok=True)

            # Tìm số thứ tự Custom_N tiếp theo dựa trên custom_layouts.json
            import re
            existing_layouts = fc_module.load_custom_layouts()
            existing_nums = []
            for key in existing_layouts.keys():
                m = re.match(r'^Custom_(\d+)$', key)
                if m:
                    existing_nums.append(int(m.group(1)))
            
            next_num = max(existing_nums) + 1 if existing_nums else 1
            custom_name = f"Custom_{next_num}"

            config_to_save = {
                "CANVAS_W": self.config["CANVAS_W"],
                "CANVAS_H": self.config["CANVAS_H"],
                "SLOTS": save_slots
            }

            success = fc_module.save_custom_layout(custom_name, config_to_save)
            if not success:
                raise Exception("Không thể ghi vào custom_layouts.json")

            w, h = self.config["CANVAS_W"], self.config["CANVAS_H"]
            
            # Lưu mold.png vào thư mục custom
            mold = np.zeros((h, w, 3), dtype=np.uint8) + 255

            for idx, (sx, sy, sw, sh) in enumerate(save_slots):
                cv2.rectangle(mold, (sx, sy), (sx + sw, sy + sh), (220, 220, 220), -1)
                cv2.rectangle(mold, (sx, sy), (sx + sw, sy + sh), (0, 0, 0), 2)
                info_text = f"P{idx+1}: {sw}x{sh}"
                cv2.putText(mold, info_text, (sx + 10, sy + 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (50, 50, 50), 2)

            mold_path = os.path.join(custom_dir, f"mold_{custom_name}.png")
            cv2.imwrite(mold_path, mold)

            QMessageBox.information(self, "Tạo thành công",
                                    f"Đã lưu mẫu {custom_name} thành công!\n\n"
                                    f"📍 Thư mục: {custom_dir}\n"
                                    f"🖼️ File 'mold_{custom_name}.png' đã được tạo với kích thước đúng tỉ lệ.\n"
                                    f"Hãy dùng file này để thiết kế khung theo ý thích của bạn.")

            self.run_frame_gen()

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu cấu hình: {e}")

    def run_frame_gen(self):
        """Chạy script tạo file khung ảnh."""
        try:
            from src.modules.image_processing.processor import generate_frame_templates
            generate_frame_templates()
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
