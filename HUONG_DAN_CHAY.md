## 5. Quy Trinh Chup

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

### Cach dung dung voi MQTT thuan: deploy viewer len Vercel

Khi sync bang MQTT, dien thoai khong can vao `http://<PC_LAN_IP>:8000`
va khong can ADB reverse nua. PC chi can chay script capture de publish len
HiveMQ; dien thoai mo `viewer.html` da deploy tren Vercel va subscribe lenh
tu HiveMQ qua WebSocket.

Tao file config cho viewer:

```powershell
copy deflecto-viewer-config.example.js deflecto-viewer-config.js
```

Sua `deflecto-viewer-config.js`:

```js
window.DEFLECTO_VIEWER_CONFIG = {
  control: "mqtt",
  T: 40,
  mqtt: {
    host: "xxxxxxxx.s1.eu.hivemq.cloud",
    wsPort: 8884,
    path: "/mqtt",
    scheme: "wss",
    username: "viewer_username",
    password: "viewer_password",
    session: "lab1"
  }
};
```

Neu deploy Vercel bang GitHub/GitLab, file `deflecto-viewer-config.js` dang nam trong
`.gitignore` nen se khong duoc commit. Co 2 cach:

- Commit file config that voi MQTT user rieng, quyen han che theo topic.
- Hoac bo config khoi Git va tiep tuc dung URL param khi test.

Sau khi deploy len Vercel, dien thoai chi can mo:

```text
https://<ten-du-an>.vercel.app/viewer.html
```

hoac:

```text
https://<ten-du-an>.vercel.app/
```

`vercel.json` da rewrite `/` ve `/viewer.html`.

Luu y: credential nam trong browser-side JavaScript thi khong phai bi mat.
Nen tao MQTT user rieng cho viewer va gioi han quyen topic, vi du chi trong
`deflectometry/lab1/#`.

Neu chua muon tao file config, van co the truyen tham so bang URL nhu cu:

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
