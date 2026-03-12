import os
import sys

# === PATH FIX ===
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# Backward-compatible re-export
from src.ui.screens.steps.step_7_processing import *
