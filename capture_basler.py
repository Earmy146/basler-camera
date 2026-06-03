"""
capture_basler.py — Bắt ảnh từ camera Basler (pypylon) cho deflectometry.

Giống hệt capture.py về workflow / phím / overlay, chỉ khác phần camera:
dùng Basler InstantCamera thay cho webcam OpenCV.

Cài đặt:
    pip install pypylon opencv-python

Workflow:
1. Chạy script này trên PC (camera Basler cắm USB3 / GigE).
2. Mở viewer.html trên iPhone/tablet, bấm START → fullscreen, hiện pattern V0.
3. Với mỗi pattern (V0..V3, H0..H3): canh sao cho camera thấy phản chiếu
   của màn hình trên bề mặt sơn bóng, rồi bấm SPACE để chụp.
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
from pypylon import pylon

CAPTURE_DIR = Path("captures")
CAPTURE_DIR.mkdir(exist_ok=True)

PATTERN_NAMES = [f"V{i}" for i in range(4)] + [f"H{i}" for i in range(4)]
SYNC_VIEWER = os.environ.get("DEFLECTO_SYNC_VIEWER", "1") != "0"
CONTROL_SET_URL = os.environ.get("DEFLECTO_CONTROL_SET_URL", "http://127.0.0.1:8000/api/set")
PATTERN_SETTLE_SEC = float(os.environ.get("DEFLECTO_SETTLE_SEC", "0.35"))
CAPTURE_COOLDOWN_SEC = float(os.environ.get("DEFLECTO_CAPTURE_COOLDOWN_SEC", "0.25"))
ADB_REVERSE = os.environ.get("DEFLECTO_ADB_REVERSE", "1") != "0"
ADB_PATH = os.environ.get("DEFLECTO_ADB_PATH", "adb")
ADB_PORT = os.environ.get("DEFLECTO_ADB_PORT", "8000")

# Khóa exposure/gain để 8 ảnh có cường độ nhất quán (BẮT BUỘC cho phase shifting).
# Exposure theo micro-giây. Tăng/giảm để tránh saturated (xem overlay khi chạy).
EXPOSURE_US = 30000.0   # 10 ms — chỉnh xuống nếu bị cháy sáng (saturated cao)
GAIN = 2.0             # giữ thấp để ít nhiễu; tăng nếu ảnh quá tối

# Kích thước tối đa của cửa sổ xem trước (chỉ ảnh hưởng HIỂN THỊ, ảnh lưu vẫn full-res).
# Chỉnh cho vừa màn hình của bạn — vd laptop 1920x1080 thì 1280x720 là vừa.
DISPLAY_MAX_W = 1280
DISPLAY_MAX_H = 720


def _try_set(node_owner, name, value):
    """Set một feature của Basler nếu nó tồn tại (tên node khác nhau giữa các model)."""
    node = getattr(node_owner, name, None)
    if node is None:
        return False
    try:
        node.SetValue(value)
        return True
    except Exception:
        return False


def open_camera():
    tl = pylon.TlFactory.GetInstance()
    devices = tl.EnumerateDevices()
    if not devices:
        raise RuntimeError("Khong tim thay camera Basler. Kiem tra cap USB3/GigE va driver pylon.")

    camera = pylon.InstantCamera(tl.CreateFirstDevice())
    camera.Open()
    print(f"Da mo camera: {camera.GetDeviceInfo().GetModelName()}")

    # Ép ROI về FULL khung hình sensor (offset 0, width/height = max).
    # Đặt offset = 0 trước rồi mới mở width/height tới max để không bị chặn ràng buộc.
    _try_set(camera, "OffsetX", 0)
    _try_set(camera, "OffsetY", 0)
    for dim in ("Width", "Height"):
        node = getattr(camera, dim, None)
        if node is not None:
            try:
                node.SetValue(node.GetMax())
            except Exception:
                pass
    if getattr(camera, "Width", None) is not None and getattr(camera, "Height", None) is not None:
        print(f"Full frame: {camera.Width.GetValue()}x{camera.Height.GetValue()}")

    # Tắt auto exposure/gain rồi đặt giá trị cố định.
    # Tên node tùy model: ExposureTime (USB3 Vision) hoặc ExposureTimeAbs (GigE cũ).
    _try_set(camera, "ExposureAuto", "Off")
    _try_set(camera, "GainAuto", "Off")
    if not _try_set(camera, "ExposureTime", EXPOSURE_US):
        _try_set(camera, "ExposureTimeAbs", EXPOSURE_US)
    _try_set(camera, "Gain", GAIN)

    # Converter: ép mọi pixel format (Mono8 / Bayer / RGB) về BGR8 cho OpenCV.
    converter = pylon.ImageFormatConverter()
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    # Luôn lấy frame mới nhất, bỏ frame cũ trong buffer.
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    return camera, converter


def grab_bgr(camera, converter):
    """Trả về 1 frame BGR (numpy) hoặc None nếu grab lỗi."""
    grab = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    try:
        if not grab.GrabSucceeded():
            return None
        return converter.Convert(grab).GetArray()
    finally:
        grab.Release()


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
    except Exception as exc:
        print(f"  [WARN] Khong dong bo viewer {name}: {exc}")


def wait_for_key_release(quiet_sec=0.08, timeout_sec=0.5):
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
    camera, converter = open_camera()
    idx = 0
    print("=" * 60)
    print("DEFLECTOMETRY CAPTURE (Basler)")
    print("=" * 60)
    print(f"Hiển thị pattern {PATTERN_NAMES[idx]} trên màn hình → bấm SPACE")
    print("Phím: SPACE = chụp, R = chụp lại trước đó, Q = thoát\n")
    sync_viewer(idx)
    pattern_ready_at = time.monotonic() + PATTERN_SETTLE_SEC
    last_capture_at = 0.0

    while True:
        frame = grab_bgr(camera, converter)
        if frame is None:
            continue

        # Tính chỉ số sáng từ ảnh GỐC full-res (để canh exposure chính xác)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_val = gray.mean()
        sat_pct = 100.0 * (gray >= 250).mean()

        # Thu nhỏ cho vừa màn hình — chỉ để hiển thị, không đụng tới ảnh lưu.
        fh, fw = frame.shape[:2]
        scale = min(DISPLAY_MAX_W / fw, DISPLAY_MAX_H / fh, 1.0)
        if scale < 1.0:
            display = cv2.resize(frame, (round(fw * scale), round(fh * scale)),
                                 interpolation=cv2.INTER_AREA)
        else:
            display = frame.copy()
        h, w = display.shape[:2]

        # Overlay hướng dẫn (vẽ lên bản đã thu nhỏ nên chữ luôn rõ)
        txt1 = f"Hien thi: {PATTERN_NAMES[idx]}  ({idx+1}/{len(PATTERN_NAMES)})"
        txt2 = "SPACE: chup   R: chup lai   Q: thoat"
        cv2.rectangle(display, (0, 0), (w, 70), (0, 0, 0), -1)
        cv2.putText(display, txt1, (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        cv2.putText(display, txt2, (10, 58),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

        info = f"mean={mean_val:5.1f}  saturated={sat_pct:4.1f}%"
        cv2.putText(display, info, (10, h - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1)

        cv2.imshow("Basler Capture", display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):
            now = time.monotonic()
            if now < pattern_ready_at:
                continue
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
                print(f"  -> Chuyen sang pattern {PATTERN_NAMES[idx]} tren man hinh")
            sync_viewer(idx)
            pattern_ready_at = time.monotonic() + PATTERN_SETTLE_SEC
            wait_for_key_release()
        elif key == ord('r') and idx > 0:
            idx -= 1
            print(f"  Chup lai {PATTERN_NAMES[idx]}")
            sync_viewer(idx)
            pattern_ready_at = time.monotonic() + PATTERN_SETTLE_SEC
        elif key == ord('q'):
            print("Da thoat som.")
            break

    camera.StopGrabbing()
    camera.Close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
