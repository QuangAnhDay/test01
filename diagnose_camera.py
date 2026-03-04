"""Chan doan camera NHANH - chi dung DirectShow."""
import cv2
import numpy as np
import sys
import json

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Lay ten camera
cam_names = {}
try:
    from pygrabber.dshow_graph import FilterGraph
    names = FilterGraph().get_input_devices()
    for i, n in enumerate(names):
        cam_names[i] = n
    print(f"Tim thay {len(names)} camera: {names}")
except:
    print("Khong lay duoc ten camera, quet index 0-4")

print("-" * 60)

best = None
best_br = 0
best_cfg = {}

max_idx = max(max(cam_names.keys()) + 1, 3) if cam_names else 3

for idx in range(max_idx):
    name = cam_names.get(idx, f"Camera {idx}")
    
    for mjpg in [False, True]:
        tag = f"DSHOW{'+MJPG' if mjpg else ''}"
        try:
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if not cap.isOpened():
                print(f"  Index {idx} [{tag:15s}]: Khong mo duoc")
                continue
            if mjpg:
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Warmup nhanh
            for _ in range(10):
                cap.read()
            
            ret, frame = cap.read()
            cap.release()
            
            if ret and frame is not None:
                br = np.mean(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
                ok = "CO HINH" if br > 10 else "DEN"
                print(f"  Index {idx} [{tag:15s}]: {ok} (brightness={br:.1f}) - {name}")
                if br > best_br:
                    best_br = br
                    best = idx
                    best_cfg = {"camera_index": idx, "use_dshow": True, "use_compat": mjpg,
                                "width": 640 if mjpg else 1280, "height": 480 if mjpg else 720}
            else:
                print(f"  Index {idx} [{tag:15s}]: Khong doc duoc frame - {name}")
        except Exception as e:
            print(f"  Index {idx} [{tag:15s}]: Loi: {e}")

print("=" * 60)
if best is not None and best_br > 10:
    print(f"CAMERA TOT NHAT: Index {best} (brightness={best_br:.1f})")
    print(f"Config: {json.dumps(best_cfg, indent=2)}")
    with open("camera_settings.json", 'w') as f:
        json.dump(best_cfg, f, indent=4)
    print("Da luu vao camera_settings.json!")
else:
    print("KHONG TIM THAY CAMERA NAO CO HINH!")
    print("Thu: Settings > Privacy > Camera, hoac kiem tra Device Manager")

input("\nNhan Enter de thoat...")
