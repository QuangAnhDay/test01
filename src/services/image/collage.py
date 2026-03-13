# ==========================================
# COLLAGE SERVICE - Tạo collage từ nhiều ảnh
# ==========================================
"""
Chịu trách nhiệm: crop ảnh theo tỷ lệ, xếp ảnh vào canvas
theo layout (2x1, 4x1, 2x2, custom slots).
"""

import cv2
import numpy as np


def crop_to_aspect_wh(img, target_w, target_h):
    """Crop ảnh về đúng tỷ lệ trước khi resize để tránh méo."""
    if img is None:
        return np.zeros((target_h, target_w, 3), np.uint8)

    h, w = img.shape[:2]
    target_ratio = target_w / target_h
    current_ratio = w / h

    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        start_x = (w - new_w) // 2
        return img[:, start_x:start_x + new_w]
    else:
        new_h = int(w / target_ratio)
        start_y = (h - new_h) // 2
        return img[start_y:start_y + new_h, :]


def create_collage(images, layout_type):
    """Tạo collage từ các ảnh đã chọn dựa trên kiểu bố cục với padding."""
    count = len(images)

    try:
        import importlib
        from src.shared.types import models as frame_config_module
        importlib.reload(frame_config_module)
        config = frame_config_module.get_layout_config(layout_type)

        PAD_TOP = config.get("PAD_TOP", 20)
        PAD_BOTTOM = config.get("PAD_BOTTOM", 100)
        PAD_LEFT = config.get("PAD_LEFT", 20)
        PAD_RIGHT = config.get("PAD_RIGHT", 20)
        GAP = config.get("GAP", 15)
        CANVAS_W = config.get("CANVAS_W", 1280)
        CANVAS_H = config.get("CANVAS_H", 720)

        print(f"DEBUG: Loaded config for {layout_type}: {CANVAS_W}x{CANVAS_H}")
    except Exception as e:
        print(f"WARNING: Cannot load config ({e}). Using defaults.")
        config = {}
        PAD_TOP, PAD_BOTTOM, PAD_LEFT, PAD_RIGHT, GAP = 20, 100, 20, 20, 15
        if layout_type == "2x1":
            CANVAS_W, CANVAS_H = 640, 900
        elif layout_type == "4x1":
            CANVAS_W, CANVAS_H = 640, 1600
        else:
            CANVAS_W, CANVAS_H = 1210, 1810

    if count == 0:
        return np.zeros((CANVAS_H, CANVAS_W, 3), dtype=np.uint8)

    # HỖ TRỢ LAYOUT CUSTOM (SLOTS)
    if "SLOTS" in config:
        canvas = np.zeros((CANVAS_H, CANVAS_W, 3), dtype=np.uint8)
        slots = config["SLOTS"]
        for i, img in enumerate(images):
            if i >= len(slots):
                break
            slot = slots[i]
            sx, sy, sw, sh = slot[:4]
            # Không cần check rotation ở đây vì sw, sh đã phản ánh hình dáng ô
            # crop_to_aspect_wh sẽ tự động cắt ảnh theo sw/sh
            cropped = crop_to_aspect_wh(img, sw, sh)
            resized = cv2.resize(cropped, (sw, sh))
            canvas[sy:sy + sh, sx:sx + sw] = resized
        return canvas

    if count == 2:
        canvas = np.zeros((CANVAS_H, CANVAS_W, 3), dtype=np.uint8)
        if layout_type == "1x2":
            available_w = CANVAS_W - PAD_LEFT - PAD_RIGHT - GAP
            available_h = CANVAS_H - PAD_TOP - PAD_BOTTOM
            img_w = available_w // 2
            img_h = available_h
            for i, img in enumerate(images):
                cropped = crop_to_aspect_wh(img, img_w, img_h)
                resized = cv2.resize(cropped, (img_w, img_h))
                x = PAD_LEFT + i * (img_w + GAP)
                y = PAD_TOP
                canvas[y:y + img_h, x:x + img_w] = resized
        elif layout_type == "2x1":
            available_w = CANVAS_W - PAD_LEFT - PAD_RIGHT
            available_h = CANVAS_H - PAD_TOP - PAD_BOTTOM - GAP
            img_w = available_w
            img_h = available_h // 2
            for i, img in enumerate(images):
                cropped = crop_to_aspect_wh(img, img_w, img_h)
                resized = cv2.resize(cropped, (img_w, img_h))
                x = PAD_LEFT
                y = PAD_TOP + i * (img_h + GAP)
                canvas[y:y + img_h, x:x + img_w] = resized
        else:
            available_w = CANVAS_W - PAD_LEFT - PAD_RIGHT - GAP
            available_h = CANVAS_H - PAD_TOP - PAD_BOTTOM
            img_w = available_w // 2
            img_h = available_h
            for i, img in enumerate(images):
                cropped = crop_to_aspect_wh(img, img_w, img_h)
                resized = cv2.resize(cropped, (img_w, img_h))
                x = PAD_LEFT + i * (img_w + GAP)
                y = PAD_TOP
                canvas[y:y + img_h, x:x + img_w] = resized

    elif count == 4:
        canvas = np.zeros((CANVAS_H, CANVAS_W, 3), dtype=np.uint8)
        if layout_type == "2x2":
            available_w = CANVAS_W - PAD_LEFT - PAD_RIGHT - GAP
            available_h = CANVAS_H - PAD_TOP - PAD_BOTTOM - GAP
            img_w = available_w // 2
            img_h = available_h // 2
            for i, img in enumerate(images):
                cropped = crop_to_aspect_wh(img, img_w, img_h)
                resized = cv2.resize(cropped, (img_w, img_h))
                row = i // 2
                col = i % 2
                x = PAD_LEFT + col * (img_w + GAP)
                y = PAD_TOP + row * (img_h + GAP)
                canvas[y:y + img_h, x:x + img_w] = resized
        elif layout_type == "4x1":
            available_w = CANVAS_W - PAD_LEFT - PAD_RIGHT
            available_h = CANVAS_H - PAD_TOP - PAD_BOTTOM - 3 * GAP
            img_w = available_w
            img_h = available_h // 4
            for i, img in enumerate(images):
                cropped = crop_to_aspect_wh(img, img_w, img_h)
                resized = cv2.resize(cropped, (img_w, img_h))
                x = PAD_LEFT
                y = PAD_TOP + i * (img_h + GAP)
                canvas[y:y + img_h, x:x + img_w] = resized
        else:
            available_w = CANVAS_W - PAD_LEFT - PAD_RIGHT - GAP
            available_h = CANVAS_H - PAD_TOP - PAD_BOTTOM - GAP
            img_w = available_w // 2
            img_h = available_h // 2
            for i, img in enumerate(images):
                cropped = crop_to_aspect_wh(img, img_w, img_h)
                resized = cv2.resize(cropped, (img_w, img_h))
                row = i // 2
                col = i % 2
                x = PAD_LEFT + col * (img_w + GAP)
                y = PAD_TOP + row * (img_h + GAP)
                canvas[y:y + img_h, x:x + img_w] = resized
    else:
        canvas = np.zeros((CANVAS_H, CANVAS_W, 3), dtype=np.uint8)

    return canvas
