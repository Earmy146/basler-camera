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
