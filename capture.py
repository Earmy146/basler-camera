"""
capture.py — Bắt ảnh từ webcam Logitech C270 cho deflectometry.

Workflow:
1. Chạy script này trên PC (webcam C270 phải cắm USB).
2. Mở viewer.html trên tablet, bấm START → vào fullscreen, hiện pattern V0.
3. Với mỗi pattern (V0..V3, H0..H3): canh sao cho webcam thấy phản chiếu
   của tablet trên bề mặt sơn bóng, rồi bấm SPACE để chụp.
4. Sau khi chụp xong, script tự thoát. Chạy process.py để xử lý.

Phím:
  SPACE — chụp pattern hiện tại
  R     — chụp lại pattern trước đó
  Q     — thoát sớm
"""
import cv2
import os
import subprocess
import time
import urllib.parse
import urllib.request
from pathlib import Path

CAPTURE_DIR = Path("captures")
CAPTURE_DIR.mkdir(exist_ok=True)

PATTERN_NAMES = [f"V{i}" for i in range(4)] + [f"H{i}" for i in range(4)]
SYNC_VIEWER = os.environ.get("DEFLECTO_SYNC_VIEWER", "1") != "0"
CONTROL_SET_URL = os.environ.get("DEFLECTO_CONTROL_SET_URL", "http://127.0.0.1:8000/api/set")
PATTERN_SETTLE_SEC = float(os.environ.get("DEFLECTO_SETTLE_SEC", "0.35"))
CAPTURE_COOLDOWN_SEC = float(os.environ.get("DEFLECTO_CAPTURE_COOLDOWN_SEC", "0.7"))
ADB_REVERSE = os.environ.get("DEFLECTO_ADB_REVERSE", "1") != "0"
ADB_PATH = os.environ.get("DEFLECTO_ADB_PATH", "adb")
ADB_PORT = os.environ.get("DEFLECTO_ADB_PORT", "8000")
CAM_INDEX = 0  # đổi nếu có nhiều webcam


def open_camera():
    cap = cv2.VideoCapture(CAM_INDEX)
    if not cap.isOpened():
        # thử các backend khác trên Windows
        for backend in (cv2.CAP_DSHOW, cv2.CAP_MSMF):
            cap = cv2.VideoCapture(CAM_INDEX, backend)
            if cap.isOpened():
                break
    if not cap.isOpened():
        raise RuntimeError("Không mở được webcam. Kiểm tra cáp USB và CAM_INDEX.")

    # C270 native: 1280x720
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Cố gắng khóa exposure để các ảnh chụp có cường độ nhất quán.
    # Giá trị driver-specific; nếu không hoạt động bạn có thể chỉnh thủ công
    # qua "Logi Tune" / "Camera Settings" trước khi chạy script.
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)   # manual mode (V4L2/DShow)
    cap.set(cv2.CAP_PROP_EXPOSURE, -6)          # -6..-2 thường ổn cho phòng sáng vừa
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)          # C270 fixed focus rồi nhưng cho chắc
    return cap


def sync_viewer(idx):
    if not SYNC_VIEWER:
        return

    name = PATTERN_NAMES[idx]
    query = urllib.parse.urlencode({"idx": idx})
    url = f"{CONTROL_SET_URL}?{query}"
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            response.read()
        print(f"  [SYNC] viewer -> {name}")
        time.sleep(PATTERN_SETTLE_SEC)
    except Exception as exc:
        print(f"  [WARN] Khong dong bo viewer {name}: {exc}")


def wait_for_key_release(quiet_sec=0.18, timeout_sec=1.5):
    quiet_since = None
    deadline = time.monotonic() + timeout_sec

    while time.monotonic() < deadline:
        raw = cv2.waitKey(20)
        if raw == -1:
            if quiet_since is None:
                quiet_since = time.monotonic()
            elif time.monotonic() - quiet_since >= quiet_sec:
                return
        else:
            quiet_since = None


def setup_adb_reverse():
    if not ADB_REVERSE:
        return

    try:
        result = subprocess.run(
            [ADB_PATH, "reverse", f"tcp:{ADB_PORT}", f"tcp:{ADB_PORT}"],
            capture_output=True,
            text=True,
            timeout=8,
        )
    except FileNotFoundError:
        print("  [WARN] Khong tim thay adb. Bo qua USB reverse, co the dung Wi-Fi URL.")
        return
    except subprocess.TimeoutExpired:
        print("  [WARN] adb reverse qua lau. Kiem tra USB debugging tren dien thoai.")
        return

    if result.returncode == 0:
        print(f"  [ADB] reverse tcp:{ADB_PORT} -> tcp:{ADB_PORT} OK")
    else:
        msg = (result.stderr or result.stdout or "").strip()
        print(f"  [WARN] adb reverse that bai: {msg}")


def main():
    setup_adb_reverse()
    cap = open_camera()
    idx = 0
    print("=" * 60)
    print("DEFLECTOMETRY CAPTURE")
    print("=" * 60)
    print(f"Hiển thị pattern {PATTERN_NAMES[idx]} trên tablet → bấm SPACE")
    print("Phím: SPACE = chụp, R = chụp lại trước đó, Q = thoát\n")
    sync_viewer(idx)
    last_capture_at = 0.0

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        display = frame.copy()
        h, w = display.shape[:2]

        # Overlay hướng dẫn
        txt1 = f"Hien thi: {PATTERN_NAMES[idx]}  ({idx+1}/{len(PATTERN_NAMES)})"
        txt2 = "SPACE: chup   R: chup lai   Q: thoat"
        cv2.rectangle(display, (0, 0), (w, 70), (0, 0, 0), -1)
        cv2.putText(display, txt1, (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        cv2.putText(display, txt2, (10, 58),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

        # Hiển thị mức sáng trung bình (giúp canh exposure)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_val = gray.mean()
        sat_pct = 100.0 * (gray >= 250).mean()
        info = f"mean={mean_val:5.1f}  saturated={sat_pct:4.1f}%"
        cv2.putText(display, info, (10, h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1)

        cv2.imshow("C270 Capture", display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):
            now = time.monotonic()
            if now - last_capture_at < CAPTURE_COOLDOWN_SEC:
                wait_for_key_release(quiet_sec=0.08, timeout_sec=0.4)
                continue
            last_capture_at = now

            path = CAPTURE_DIR / f"{PATTERN_NAMES[idx]}.png"
            # Lưu ảnh xám để xử lý ổn định hơn
            cv2.imwrite(str(path), gray)
            print(f"  [OK] {path}  (mean={mean_val:.1f}, sat={sat_pct:.1f}%)")
            idx += 1
            if idx == len(PATTERN_NAMES):
                idx = 0
                print("  -> Hoan tat 8 captures. Quay lai pattern V0")
                print("  -> Co the chup vong moi hoac bam Q de thoat, sau do chay: python process.py")
            else:
                print(f"  -> Chuyen sang pattern {PATTERN_NAMES[idx]} tren tablet")
            sync_viewer(idx)
            wait_for_key_release()
        elif key == ord('r') and idx > 0:
            idx -= 1
            print(f"  Chup lai {PATTERN_NAMES[idx]}")
            sync_viewer(idx)
        elif key == ord('q'):
            print("Da thoat som.")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
