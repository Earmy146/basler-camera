## Quy trinh chay khong can ADB

Muc tieu cua che do MQTT la bo phu thuoc ADB/cap USB cho viec dong bo pattern.
PC chay script capture va publish len HiveMQ. Dien thoai hien pattern va nhan
lenh tu HiveMQ qua MQTT over WebSocket.

Luon can phan biet 2 viec:

- Nap viewer len dien thoai: mo `viewer.html` bang browser, app, LAN server, hoac cach khac.
- Dieu khien/dong bo pattern: MQTT qua HiveMQ.

Neu dung MQTT, `control_server.py` khong con dieu khien pattern nua. Neu van chay
server tren PC thi no chi de browser tren dien thoai tai file `viewer.html`.

## Chay MQTT voi browser hien tai

1. Cai thu vien MQTT cho Python:

```powershell
pip install -r requirements.txt
```

2. Cau hinh `.env`:

```env
DEFLECTO_CONTROL_MODE=mqtt
DEFLECTO_ADB_REVERSE=0
DEFLECTO_MQTT_HOST=xxxxxxxx.s1.eu.hivemq.cloud
DEFLECTO_MQTT_PORT=8883
DEFLECTO_MQTT_USERNAME=your_hivemq_username
DEFLECTO_MQTT_PASSWORD=your_hivemq_password
DEFLECTO_MQTT_SESSION=lab1
DEFLECTO_PATTERN_T=40

# Neu co nhieu dien thoai va muon cho du so viewer render moi chup:
DEFLECTO_MQTT_EXPECTED_VIEWERS=0
DEFLECTO_MQTT_ACK_TIMEOUT_SEC=2.0
```

3. Tao `deflecto-viewer-config.js` cho browser:

```powershell
copy deflecto-viewer-config.example.js deflecto-viewer-config.js
```

Trong browser, HiveMQ Cloud dung WebSocket TLS port `8884`, khac voi Python
dung MQTT TLS port `8883`.

4. Neu van dung browser va khong deploy/app, chay server tinh de phat file HTML:

```powershell
python control_server.py --host 0.0.0.0 --port 8000
```

Mo tren dien thoai qua Wi-Fi cung mang LAN:

```text
http://<PC_LAN_IP>:8000/viewer.html
```

Buoc nay khong can ADB va khong can cap. Server nay chi de tai file HTML.
Sau khi viewer da mo, viec doi pattern di qua HiveMQ.

5. Chay capture tren PC:

```powershell
python capture.py
```

hoac:

```powershell
python capture_basler.py
```

Khi bam `SPACE`, Python publish len topic:

```text
deflectometry/lab1/cmd
```

Tat ca viewer dang subscribe cung session se doi pattern. Viewer gui ACK ve:

```text
deflectometry/lab1/ack
```

## Khi nao can app nho?

Neu muon khong deploy, khong mo server PC de phat HTML, va khong cam cap, thi
dung mot app nho la huong gon nhat. App do chi can bundle viewer HTML/JS ben
trong WebView hoac viet native MQTT client, roi connect thang HiveMQ.

Noi cach khac:

- Browser + LAN server: khong can cap, nhung PC van phai phat file HTML.
- Browser + deploy: khong can cap, khong can PC phat file HTML.
- App nho: khong can cap, khong can deploy, khong can PC phat file HTML.
- ADB reverse + `http://127.0.0.1:8000`: cach cu, can cap, khong can khi da dung MQTT.

HTML hien tai van co the nhan va xu ly MQTT truc tiep. Khong bat buoc phai build
app moi dieu khien duoc MQTT. App chi giai quyet bai toan dong goi viewer len
dien thoai de khoi phu thuoc server/deploy.

## Luu y bao mat

Neu browser hoac app connect truc tiep HiveMQ thi credential nam phia client,
khong nen xem la bi mat. Nen tao MQTT user rieng cho viewer va gioi han quyen
topic, vi du `deflectometry/lab1/#`.

## Che do cu qua ADB

Chi dung phan nay neu muon quay lai dieu khien HTTP cu.

1. Chay server tren may tinh:

```powershell
python control_server.py --host 0.0.0.0 --port 8000
```

2. Dat `.env`:

```env
DEFLECTO_CONTROL_MODE=http
DEFLECTO_ADB_REVERSE=1
```

3. Cam dien thoai bang USB va mo:

```text
http://127.0.0.1:8000/viewer.html
```

Che do nay moi can ADB reverse/cap USB.
