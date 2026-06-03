# Hướng Dẫn Chạy Deflectometry Qua MQTT, Không Cần ADB

Mục tiêu của cấu hình hiện tại là bỏ ADB/cáp USB cho phần đồng bộ pattern.
PC chỉ chụp ảnh và gửi lệnh đổi pattern lên HiveMQ. Điện thoại mở viewer và
nhận lệnh qua MQTT over WebSocket.

`control_server.py` vẫn có thể cần chạy, nhưng chỉ để phát file `viewer.html`
cho điện thoại qua Wi-Fi LAN. Nó không còn là kênh điều khiển pattern khi đang
dùng MQTT.

## 1. Cài thư viện Python

Tạo môi trường ảo nếu chưa có:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Cài thư viện:

```powershell
pip install -r requirements.txt
```

`requirements.txt` hiện gồm các thư viện cần cho:

- `paho-mqtt`: kết nối HiveMQ từ Python.
- `opencv-python`: xem camera, lưu ảnh capture.
- `numpy`: xử lý số liệu ảnh.
- `matplotlib`: vẽ và lưu `results.png`.
- `pypylon`: dùng camera Basler.

Nếu chỉ dùng webcam thường thì `pypylon` không được dùng, nhưng vẫn để trong
requirements để chạy được `capture_basler.py` khi cần.

## 2. Cấu hình `.env`

File `.env` cần đặt chế độ MQTT và tắt ADB reverse:

```env
DEFLECTO_CONTROL_MODE=mqtt
DEFLECTO_ADB_REVERSE=0

DEFLECTO_MQTT_HOST=09403771044540c8bc18d960af026317.s1.eu.hivemq.cloud
DEFLECTO_MQTT_PORT=8883
DEFLECTO_MQTT_USERNAME=deflecto
DEFLECTO_MQTT_PASSWORD=your_password
DEFLECTO_MQTT_SESSION=lab1
DEFLECTO_MQTT_RETAIN=1

DEFLECTO_PATTERN_T=40
DEFLECTO_MQTT_EXPECTED_VIEWERS=0
DEFLECTO_MQTT_ACK_TIMEOUT_SEC=2.0
```

Python dùng MQTT TLS port `8883`.

## 3. Kiểm tra `deflecto-viewer-config.js`

File `deflecto-viewer-config.js` là cấu hình cho browser trên điện thoại. File
này phải khớp với `.env`, nhưng browser dùng WebSocket TLS port `8884`:

```js
window.DEFLECTO_VIEWER_CONFIG = {
  control: "mqtt",
  T: 40,
  mqtt: {
    host: "09403771044540c8bc18d960af026317.s1.eu.hivemq.cloud",
    wsPort: 8884,
    path: "/mqtt",
    scheme: "wss",
    username: "deflecto",
    password: "your_password",
    session: "lab1"
  }
};
```

File này đang bị `.gitignore` vì chứa MQTT password phía browser.

## 4. Chạy server phát viewer qua Wi-Fi

Trên PC:

```powershell
python control_server.py --host 0.0.0.0 --port 8000
```

Server này chỉ để điện thoại tải `viewer.html`; điều khiển pattern vẫn đi qua
HiveMQ.

Lấy IP LAN của PC:

```powershell
ipconfig
```

Tìm dòng `IPv4 Address`, ví dụ:

```text
192.168.1.23
```

Trên điện thoại, dùng cùng Wi-Fi với PC và mở:

```text
http://192.168.1.23:8000/viewer.html
```

Thay IP bằng IP thật của PC. Bấm `START`. Nếu kết nối MQTT ổn, góc màn hình sẽ
hiện trạng thái kiểu:

```text
MQTT connected deflectometry/lab1/cmd
```

## 5. Chạy capture

Nếu dùng camera Basler:

```powershell
python capture_basler.py
```

Nếu dùng webcam thường:

```powershell
python capture.py
```

Trong cửa sổ camera:

- `SPACE`: chụp pattern hiện tại, rồi gửi lệnh đổi pattern qua MQTT.
- `R`: quay lại chụp lại pattern trước.
- `Q`: thoát.

Ảnh sẽ được lưu vào thư mục `captures/` với tên:

```text
V0.png
V1.png
V2.png
V3.png
H0.png
H1.png
H2.png
H3.png
```

## 6. Xử lý kết quả

Sau khi đã có đủ 8 ảnh:

```powershell
python process.py
```

Kết quả được lưu thành:

```text
results.png
```

## Tóm Tắt Luồng Chạy

```text
Điện thoại mở viewer.html qua Wi-Fi
        ↓
Viewer kết nối HiveMQ bằng MQTT over WebSocket
        ↓
PC chạy capture_basler.py hoặc capture.py
        ↓
Khi bấm SPACE, Python publish lệnh lên HiveMQ
        ↓
Viewer nhận lệnh MQTT và đổi pattern
```

Không cần cắm cáp điện thoại. Không cần `adb`. Không cần `adb reverse`.

## Khi Nào Cần App Nhỏ?

Nếu muốn bỏ luôn bước chạy `control_server.py` để phát file HTML, lúc đó nên
đóng gói viewer thành app nhỏ trên điện thoại. App có thể dùng WebView chứa
`viewer.html` hiện tại, hoặc viết native MQTT client.

So sánh ngắn:

- Browser + LAN server: không cần cáp, không cần ADB, nhưng PC phải phát HTML.
- App nhỏ: không cần cáp, không cần ADB, không cần PC phát HTML.
- ADB reverse: cách cũ, cần cáp, không cần dùng khi đã chạy MQTT.

## Lỗi Thường Gặp

Nếu điện thoại không mở được `http://<PC_LAN_IP>:8000/viewer.html`:

- Kiểm tra điện thoại và PC có cùng Wi-Fi không.
- Kiểm tra IP PC lấy từ `ipconfig` có đúng không.
- Kiểm tra firewall Windows có chặn port `8000` không.
- Kiểm tra `control_server.py` còn đang chạy không.

Nếu viewer báo lỗi MQTT:

- Kiểm tra `host`, `username`, `password`, `session` trong
  `deflecto-viewer-config.js`.
- Kiểm tra `wsPort` của browser là `8884`.
- Kiểm tra HiveMQ Cloud còn hoạt động và user có quyền topic
  `deflectometry/lab1/#`.

Nếu Python báo lỗi MQTT:

- Kiểm tra `.env`.
- Kiểm tra `DEFLECTO_MQTT_PORT=8883`.
- Chạy lại `pip install -r requirements.txt`.
