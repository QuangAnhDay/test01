# ==========================================
# ADMIN STATE - Quản lý trạng thái Admin
# ==========================================
"""
Quản lý config cho phiên admin.
"""

import os
import json

CONFIG_FILE = "config.json"


def load_admin_config():
    """Load cấu hình admin từ file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_admin_config(config):
    """Lưu cấu hình admin."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
