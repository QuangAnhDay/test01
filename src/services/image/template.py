# ==========================================
# TEMPLATE SERVICE - Load, detect, overlay template
# ==========================================
"""
Chịu trách nhiệm: tạo frame template, load template files,
phát hiện layout từ tên file, overlay template lên collage.
"""

import os
import re
import cv2
import numpy as np
from src.shared.types.models import (
    TEMPLATE_DIR, get_layout_config, get_all_layouts,
    CUSTOM_LAYOUTS
)
from src.utils.image_helpers import overlay_images


def generate_frame_templates():
    """Tạo file ảnh khung nền trong suốt/màu cho các layout nếu chưa có."""
    base_dir = TEMPLATE_DIR
    os.makedirs(base_dir, exist_ok=True)

    # 1. Xử lý các custom layouts - đặt vào đúng thư mục group
    custom_dir = os.path.join(base_dir, "custom")
    vertical_dir = os.path.join(base_dir, "vertical")
    os.makedirs(custom_dir, exist_ok=True)
    os.makedirs(vertical_dir, exist_ok=True)
    
    # Tập hợp tên layout còn tồn tại để dọn file mồ côi
    valid_custom_names = set(CUSTOM_LAYOUTS.keys())
    
    for name, cfg in CUSTOM_LAYOUTS.items():
        # Xác định thư mục dựa trên group
        group = cfg.get("group", "custom")
        if group == "vertical":
            target_dir = vertical_dir
        else:
            target_dir = custom_dir
        
        filename = os.path.join(target_dir, f"frame_{name}.png")
        if not os.path.exists(filename):
            print(f"Creating custom frame: {filename}")
            w, h = cfg["CANVAS_W"], cfg["CANVAS_H"]
            # Tạo nền trắng đục (alpha=255)
            frame = np.ones((h, w, 4), dtype=np.uint8) * 255
            cv2.putText(frame, f"CUSTOM: {name}", (50, h - 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100, 255), 2)
            # Khoét vùng slot trong suốt (alpha=0) để ảnh hiện ra
            for slot in cfg.get("SLOTS", []):
                sx, sy, sw, sh = slot[:4]
                y1, y2 = max(0, sy), min(h, sy + sh)
                x1, x2 = max(0, sx), min(w, sx + sw)
                frame[y1:y2, x1:x2] = [0, 0, 0, 0]
            cv2.imwrite(filename, frame)
        
        # Xóa file ở thư mục SAI (nếu trước đó bị đặt nhầm)
        wrong_dir = vertical_dir if group != "vertical" else custom_dir
        wrong_path = os.path.join(wrong_dir, f"frame_{name}.png")
        if os.path.exists(wrong_path):
            print(f"[CLEANUP] Removing misplaced template: {wrong_path}")
            os.remove(wrong_path)

    # Dọn các file template mồ côi trong thư mục custom
    for f in os.listdir(custom_dir):
        if f.lower().endswith(('.png', '.jpg', '.jpeg')) and f.startswith('frame_'):
            fname_no_ext = os.path.splitext(f)[0]
            rest = fname_no_ext[len('frame_'):]
            m = re.match(r'^(Custom_\d+)', rest)
            if m:
                layout_name = m.group(1)
                if layout_name not in valid_custom_names:
                    orphan_path = os.path.join(custom_dir, f)
                    print(f"[CLEANUP] Removing orphaned template: {orphan_path} (layout '{layout_name}' no longer exists)")
                    os.remove(orphan_path)


def load_templates_for_layout(layout_type, selected_frame_count):
    """Load danh sách templates cho một nhóm layout (vertical hoặc custom)."""
    templates = []
    
    cfg = get_layout_config(layout_type)
    layout_group = cfg.get("group", "vertical" if layout_type == "4x1" else "custom")
    
    search_dirs = []
    if layout_group == "vertical" or layout_type == "4x1":
        search_dirs.append(os.path.join(TEMPLATE_DIR, "vertical"))
    else:
        search_dirs.append(os.path.join(TEMPLATE_DIR, "custom"))

    for directory in search_dirs:
        if os.path.exists(directory):
            for f in os.listdir(directory):
                fpath = os.path.join(directory, f)
                if os.path.isfile(fpath) and f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    full_path = os.path.abspath(fpath)
                    
                    fname_no_ext = os.path.splitext(f)[0]
                    exact_match = f"frame_{layout_type}"
                    variant_prefix = f"frame_{layout_type}_"
                    
                    if fname_no_ext == exact_match or fname_no_ext.startswith(variant_prefix):
                        if full_path not in templates:
                            templates.append(full_path)
                    else:
                        continue

    print(f"[DEBUG] Templates for {layout_type}: {templates}")
    return templates


def load_all_templates_for_group(group_name):
    """Load TẤT CẢ templates trong một nhóm (vertical hoặc custom), không phân biệt layout."""
    templates = []
    
    search_dirs = []
    if group_name == "vertical":
        search_dirs.append(os.path.join(TEMPLATE_DIR, "vertical"))
    else:
        search_dirs.append(os.path.join(TEMPLATE_DIR, "custom"))

    valid_layout_names = None
    if group_name == "custom":
        all_layouts = get_all_layouts()
        valid_layout_names = set()
        for lname, lcfg in all_layouts.items():
            lgroup = lcfg.get("group", "vertical" if lname == "4x1" else "custom")
            if lgroup == "custom":
                valid_layout_names.add(lname)

    for directory in search_dirs:
        if os.path.exists(directory):
            for f in sorted(os.listdir(directory)):
                fpath = os.path.join(directory, f)
                if os.path.isfile(fpath) and f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    if valid_layout_names is not None:
                        detected = detect_layout_from_template(fpath)
                        if detected and detected not in valid_layout_names:
                            continue
                    
                    full_path = os.path.abspath(fpath)
                    if full_path not in templates:
                        templates.append(full_path)

    print(f"[DEBUG] All templates for group '{group_name}': {templates}")
    return templates


def detect_layout_from_template(template_path):
    """Phát hiện layout_type từ tên file template.
    
    Quy tắc: frame_{layout_type}.png hoặc frame_{layout_type}_suffix.png
    Ví dụ: frame_4x1.png -> '4x1', frame_Custom_3_tet.png -> 'Custom_3'
    """
    fname = os.path.splitext(os.path.basename(template_path))[0]
    
    if fname.startswith("frame_"):
        rest = fname[len("frame_"):]
    else:
        return None
    
    # Thử khớp với pattern Custom_N trước
    m = re.match(r'^(Custom_\d+)', rest)
    if m:
        return m.group(1)
    
    # Thử khớp layout đơn giản như 4x1, 2x2, ...
    m = re.match(r'^(\d+x\d+)', rest)
    if m:
        return m.group(1)
    
    # Thử khớp tên layout đơn (ví dụ: "5", "6")
    m = re.match(r'^(\d+)', rest)
    if m:
        return m.group(1)
    
    return rest.split("_")[0] if "_" in rest else rest


def apply_template_overlay(collage_image, template_path):
    """Áp dụng template lên collage."""
    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    if template is not None and collage_image is not None:
        return overlay_images(collage_image.copy(), template)
    return collage_image
