## 5. Quy Trinh Chup

## Cach khuyen dung: HiveMQ thuan, khong can ADB reverse/IP PC

Luồng này đúng với mục tiêu: máy tính chỉ publish lệnh lên HiveMQ, điện thoại chỉ mở
HTML và subscribe từ HiveMQ. Không cần `control_server.py`, không cần
`adb reverse`, không cần lấy IPv4 bằng `ipconfig`.

1. Tren HiveMQ Cloud, tao credential:

```text
Username: deflecto
Password: <mat_khau_hivemq_cua_ban>
Permission: Publish and Subscribe
Topic Filter: deflectometry/#
```

2. Trong `.env`, giu cac gia tri:

```env
DEFLECTO_CONTROL_MODE=mqtt
DEFLECTO_ADB_REVERSE=0
DEFLECTO_MQTT_HOST=09403771044540c8bc18d960af026317.s1.eu.hivemq.cloud
DEFLECTO_MQTT_PORT=8883
DEFLECTO_MQTT_USERNAME=deflecto
DEFLECTO_MQTT_PASSWORD=<mat_khau_hivemq_cua_ban>
DEFLECTO_MQTT_SESSION=lab1
DEFLECTO_PATTERN_T=40
```

3. Dua file `viewer_mqtt.html` len dien thoai va mo file do.

Co the copy file qua USB, Zalo/Telegram, email, Google Drive, hoac host len mot
static site. Sau khi file da mo duoc tren dien thoai thi viec dong bo pattern se
di qua HiveMQ, khong di qua PC.

4. Tren dien thoai, trong form MQTT Viewer:

```text
HiveMQ host: 09403771044540c8bc18d960af026317.s1.eu.hivemq.cloud
Username: deflecto
Password: <mat_khau_hivemq_cua_ban>
Session: lab1
Pattern period T: 40
```

Bam `START`. Cac gia tri se duoc luu tren trinh duyet, lan sau khong can nhap
lai neu van dung dien thoai/trinh duyet do.

5. Tren may tinh, chi can chay capture:

```powershell
python capture_basler.py
```

hoac:

```powershell
python capture.py
```

Khi script chuyen pattern, no publish len `deflectometry/lab1/cmd`.
Moi dien thoai dang mo `viewer_mqtt.html` cung session `lab1` se doi pattern.

## Cach cu: serve viewer qua PC/USB reverse

Phan ben duoi la luong cu neu van muon serve `viewer.html` tu may tinh.

Neu may dang cam nhieu dien thoai/emulator, mo file `.env` roi dien serial ADB.

Lay serial bang:

```powershell
adb devices -l
```

Vi du:

```env
DEFLECTO_ADB_SERIAL=R5CT1234567
DEFLECTO_ADB_PORT=8000
```

Neu chi cam mot dien thoai thi co the de trong:

```env
DEFLECTO_ADB_SERIAL=
```

## Chay sync bang HiveMQ khi co nhieu dien thoai

Cach nay dung HiveMQ de dong bo pattern, nen `capture_basler.py` khong can biet
ADB serial cua tung dien thoai nua.

1. Cai MQTT client cho Python:

```powershell
pip install -r requirements.txt
```

2. Dien `.env`:

```env
DEFLECTO_CONTROL_MODE=mqtt
DEFLECTO_ADB_REVERSE=0
DEFLECTO_MQTT_HOST=xxxxxxxx.s1.eu.hivemq.cloud
DEFLECTO_MQTT_PORT=8883
DEFLECTO_MQTT_USERNAME=your_hivemq_username
DEFLECTO_MQTT_PASSWORD=your_hivemq_password
DEFLECTO_MQTT_SESSION=lab1

# Neu co 2 dien thoai va muon cho ca 2 da render moi cho chup:
DEFLECTO_MQTT_EXPECTED_VIEWERS=2
DEFLECTO_MQTT_ACK_TIMEOUT_SEC=2.0
```

3. Mo viewer tren moi dien thoai voi cung `mqttSession`.

Neu van chay `control_server.py` de serve file HTML qua LAN:

```text
http://<PC_LAN_IP>:8000/viewer.html?control=mqtt&mqttHost=xxxxxxxx.s1.eu.hivemq.cloud&mqttUsername=your_hivemq_username&mqttPassword=your_hivemq_password&mqttSession=lab1
```

Neu mo file HTML truc tiep tren dien thoai thi URL cung can cac tham so tren.
Browser dung MQTT over WebSocket cua HiveMQ Cloud, port mac dinh la `8884`.
Python capture dung MQTT TLS, port mac dinh la `8883`.

4. Chay Basler capture:

```powershell
python capture_basler.py
```

Khi bam `SPACE`, Python publish pattern moi len topic
`deflectometry/lab1/cmd`; tat ca viewer dang subscribe se doi pattern cung luc.
Viewer se gui ACK ve `deflectometry/lab1/ack`.

1. Chay server tren may tinh:

```powershell
python control_server.py --host 0.0.0.0 --port 8000
```

2. Chay script chup tren may tinh:

```powershell
python capture.py
```

hoac:

```powershell
python capture_basler.py
```

3. Cam dien thoai bang USB.

4. Mo tren dien thoai:

```text
http://127.0.0.1:8000/viewer.html
```

5. Bam `START` tren dien thoai.

Mo giao dien camera view, bam `SPACE` de chup, `R` de quay lai, `Q` de thoat chuong trinh.
