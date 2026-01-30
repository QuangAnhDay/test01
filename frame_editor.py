import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QSlider, QGroupBox, QComboBox, 
                             QPushButton, QFrame, QTextEdit)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QFont

# Import default configs if available
try:
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

class FrameEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎨 Photobooth Frame Visual Editor")
        self.resize(1400, 900)
        self.setStyleSheet("background-color: #1a1a2e; color: white;")

        # Current state
        self.current_layout_type = "4x1"
        self.config = DEFAULT_CONFIGS[self.current_layout_type].copy()
        self.photo_ratio = 1.5 # 3:2 default

        self.init_ui()
        self.update_preview()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_vbox = QVBoxLayout(central_widget)

        # --- TOP BAR: Layout Selection ---
        top_bar = QFrame()
        top_bar.setStyleSheet("background-color: #16213e; border-bottom: 2px solid #4361ee;")
        top_bar.setFixedHeight(60)
        top_layout = QHBoxLayout(top_bar)
        
        lbl_select = QLabel("LỰA CHỌN KIỂU LƯỚI:")
        lbl_select.setFont(QFont("Arial", 12, QFont.Bold))
        top_layout.addWidget(lbl_select)

        self.combo_layout = QComboBox()
        self.combo_layout.addItems(["1x2", "2x1", "2x2", "4x1"])
        self.combo_layout.setCurrentText(self.current_layout_type)
        self.combo_layout.setFixedWidth(150)
        self.combo_layout.setStyleSheet("background-color: #4361ee; color: white; padding: 5px; font-weight: bold;")
        self.combo_layout.currentTextChanged.connect(self.change_layout_type)
        top_layout.addWidget(self.combo_layout)
        
        top_layout.addStretch()
        
        btn_save = QPushButton("💾 XEM CODE")
        btn_save.setFixedWidth(120)
        btn_save.setStyleSheet("background-color: #06d6a0; color: #1a1a2e; font-weight: bold;")
        btn_save.clicked.connect(self.show_code)
        top_layout.addWidget(btn_save)

        main_vbox.addWidget(top_bar)

        # --- MAIN CONTENT: Left Controls, Right Preview ---
        content_layout = QHBoxLayout()
        
        # LEFT PANEL (1/3)
        left_panel = QWidget()
        left_panel.setFixedWidth(400)
        left_vbox = QVBoxLayout(left_panel)
        
        # Groups
        self.create_control_group(left_vbox, "KÍCH THƯỚC CANVAS", {
            "CANVAS_W": (400, 2000, "Chiều rộng"),
            "CANVAS_H": (400, 2000, "Chiều cao")
        })
        
        self.create_control_group(left_vbox, "BÌ (PADDING)", {
            "PAD_TOP": (0, 400, "Bì trên"),
            "PAD_BOTTOM": (0, 400, "Bì dưới"),
            "PAD_LEFT": (0, 400, "Bì trái"),
            "PAD_RIGHT": (0, 400, "Bì phải")
        })

        self.create_control_group(left_vbox, "KHOẢNG CÁCH & TỶ LỆ", {
            "GAP": (0, 100, "Khoảng cách ảnh"),
            "PHOTO_RATIO": (10, 30, "Tỷ lệ (x10, vd 1.5=3:2)")
        })

        self.code_display = QTextEdit()
        self.code_display.setReadOnly(True)
        self.code_display.setStyleSheet("background-color: #0f172a; color: #38bdf8; font-family: 'Consolas'; font-size: 11px;")
        left_vbox.addWidget(QLabel("CODE DỰ KIẾN:"))
        left_vbox.addWidget(self.code_display)
        
        content_layout.addWidget(left_panel)

        # RIGHT PREVIEW (2/3)
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #000; border: 1px solid #4361ee;")
        content_layout.addWidget(self.preview_label, stretch=2)

        main_vbox.addLayout(content_layout)

    def create_control_group(self, parent_layout, title, controls):
        group = QGroupBox(title)
        group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #4361ee; margin-top: 10px; padding: 10px; }")
        layout = QVBoxLayout(group)

        for key, (min_v, max_v, label_text) in controls.items():
            h_layout = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(120)
            
            val_lbl = QLabel()
            val_lbl.setFixedWidth(40)
            val_lbl.setAlignment(Qt.AlignRight)
            
            slider = QSlider(Qt.Horizontal)
            slider.setRange(min_v, max_v)
            
            # Initial value
            current_val = int(self.config.get(key, 15)) if key != "PHOTO_RATIO" else int(self.photo_ratio * 10)
            slider.setValue(current_val)
            val_lbl.setText(str(current_val if key != "PHOTO_RATIO" else current_val/10))
            
            slider.valueChanged.connect(lambda v, k=key, l=val_lbl: self.on_slider_change(k, v, l))
            
            h_layout.addWidget(lbl)
            h_layout.addWidget(slider)
            h_layout.addWidget(val_lbl)
            layout.addLayout(h_layout)

        parent_layout.addWidget(group)

    def on_slider_change(self, key, value, label):
        if key == "PHOTO_RATIO":
            self.photo_ratio = value / 10.0
            label.setText(str(self.photo_ratio))
        else:
            self.config[key] = value
            label.setText(str(value))
        
        self.update_preview()
        self.update_code_display()

    def change_layout_type(self, text):
        self.current_layout_type = text
        self.config = DEFAULT_CONFIGS[text].copy()
        # Refresh UI sliders could be complex, for now we just update preview
        self.update_preview()
        self.update_code_display()

    def update_code_display(self):
        code = f"LAYOUT_{self.current_layout_type} = {{\n"
        for k, v in self.config.items():
            code += f"    \"{k}\": {v},\n"
        code += "}"
        self.code_display.setText(code)

    def show_code(self):
        self.update_code_display()

    def update_preview(self):
        # Create canvas
        w, h = self.config["CANVAS_W"], self.config["CANVAS_H"]
        # Scale down for display if too big
        scale = min(800 / h, 500 / w) if h > 800 or w > 500 else 1.0
        
        # Logic to calculate slots (copied from main app logic)
        canvas = np.zeros((h, w, 3), dtype=np.uint8) + 40 # Dark gray bg
        
        # Draw Padding area
        pt, pb, pl, pr = self.config["PAD_TOP"], self.config["PAD_BOTTOM"], self.config["PAD_LEFT"], self.config["PAD_RIGHT"]
        gap = self.config["GAP"]
        
        # Visual padding (light blue)
        cv2.rectangle(canvas, (0, 0), (w, pt), (100, 50, 50), -1) # Top
        cv2.rectangle(canvas, (0, h-pb), (w, h), (100, 50, 50), -1) # Bottom
        cv2.rectangle(canvas, (0, 0), (pl, h), (100, 50, 50), -1) # Left
        cv2.rectangle(canvas, (pr_x:=w-pr, 0), (w, h), (100, 50, 50), -1) # Right

        # Calculate Slots
        avail_w = w - pl - pr
        avail_h = h - pt - pb
        
        slots = []
        if self.current_layout_type == "1x2":
            sw = avail_w
            sh = (avail_h - gap) // 2
            slots = [(pl, pt), (pl, pt + sh + gap)]
        elif self.current_layout_type == "2x1":
            sw = (avail_w - gap) // 2
            sh = avail_h
            slots = [(pl, pt), (pl + sw + gap, pt)]
        elif self.current_layout_type == "2x2":
            sw = (avail_w - gap) // 2
            sh = (avail_h - gap) // 2
            slots = [
                (pl, pt), (pl + sw + gap, pt),
                (pl, pt + sh + gap), (pl + sw + gap, pt + sh + gap)
            ]
        elif self.current_layout_type == "4x1":
            sw = avail_w
            sh = (avail_h - 3 * gap) // 4
            for i in range(4):
                slots.append((pl, pt + i * (sh + gap)))

        # Draw Slots and Photos
        for i, (sx, sy) in enumerate(slots):
            # Draw Slot (Red outline)
            cv2.rectangle(canvas, (sx, sy), (sx + sw, sy + sh), (0, 0, 255), 2)
            
            # Calculate Photo (Maintain Ratio)
            # Find best fit centered in slot
            if sw / sh > self.photo_ratio: # Slot wider than photo
                pw = int(sh * self.photo_ratio)
                ph = sh
                px = sx + (sw - pw) // 2
                py = sy
            else: # Slot taller than photo
                pw = sw
                ph = int(sw / self.photo_ratio)
                px = sx
                py = sy + (sh - ph) // 2
            
            # Draw Photo Placeholder (White)
            cv2.rectangle(canvas, (px, py), (px + pw, py + ph), (255, 255, 255), -1)
            cv2.putText(canvas, f"Photo {i+1}", (px + 10, py + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            cv2.putText(canvas, f"{pw}x{ph}", (px + 10, py + ph - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 50, 50), 1)

        # Info text
        cv2.putText(canvas, f"Layout: {self.current_layout_type} | Canvas: {w}x{h}", (20, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Convert to QPixmap
        h_c, w_c, ch = canvas.shape
        bytes_per_line = ch * w_c
        qt_img = QImage(canvas.data, w_c, h_c, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        
        # Scale to fit UI
        view_w = self.preview_label.width() or 800
        view_h = self.preview_label.height() or 600
        pixmap = QPixmap.fromImage(qt_img).scaled(view_w-20, view_h-20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_preview()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = FrameEditor()
    editor.show()
    sys.exit(app.exec_())
