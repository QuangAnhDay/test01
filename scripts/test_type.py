import os
import sys
# === PATH FIX ===
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication
import sys
app = QApplication(sys.argv)

from src.shared.utils.helpers import convert_cv_qt, get_rounded_pixmap
from PyQt5.QtGui import QPixmap, QImage

# Create a dummy image
img = np.zeros((100, 100, 3), dtype=np.uint8)
qt_img = convert_cv_qt(img)
print(f"Type of qt_img: {type(qt_img)}")
print(f"Is QPixmap? {isinstance(qt_img, QPixmap)}")

# Test get_rounded_pixmap
try:
    rounded = get_rounded_pixmap(qt_img)
    print("get_rounded_pixmap SUCCESS with QPixmap")
except Exception as e:
    print(f"get_rounded_pixmap FAILED with QPixmap: {e}")

try:
    img_obj = QImage(100, 100, QImage.Format_RGB888)
    rounded = get_rounded_pixmap(img_obj)
    print("get_rounded_pixmap SUCCESS with QImage")
except Exception as e:
    print(f"get_rounded_pixmap FAILED with QImage: {e}")
