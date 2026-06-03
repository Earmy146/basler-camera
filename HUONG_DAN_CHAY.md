# Huong dan chay he thong Deflectometry

Tai lieu nay mo ta cach chay du an theo che do dong bo: may tinh dieu khien frame tren dien thoai, sau do camera chup tung anh.

## 1. Chuan bi thiet bi

- May tinh Windows da cai Python va da co thu muc du an nay.
- Dien thoai/tablet dung de hien thi pattern.
- Camera that gan vao may tinh:
  - Webcam: chay `capture.py`
  - Basler: chay `capture_basler.py`
- Dien thoai va may tinh nen o cung mang Wi-Fi.

Khong can deploy len server online. He thong chi can server local chay tren may tinh.

## 2. Mo server tren may tinh

Mo PowerShell trong thu muc du an:

```powershell
cd C:\Users\Earmy\Downloads\deflectometry
.\.venv\Scripts\activate
python control_server.py --host 0.0.0.0 --port 8000
```

Giu cua so nay dang chay. Day la server dieu khien `viewer.html`.

## 3. Mo viewer tren dien thoai

Neu dien thoai va may tinh cung Wi-Fi, mo trinh duyet tren dien thoai va vao:

```text
http://192.168.1.8:8000/viewer.html
```

Neu IP may tinh thay doi, kiem tra bang lenh:

```powershell
ipconfig
```

Tim dong `IPv4 Address` cua card `Wi-Fi`, roi thay vao URL:

```text
http://<IP_MAY_TINH>:8000/viewer.html
```

Vi du:

```text
http://192.168.1.8:8000/viewer.html
```

Sau khi trang mo len, bam `START` tren dien thoai.

## 4. Cai dat man hinh dien thoai truoc khi chup

Truoc khi chup that, nen cai dat tren dien thoai:

- Brightness MAX.
- Tat Adaptive brightness.
- Tat Eye comfort shield / Night light.
- Tat Dark mode.
- Tat Always-On Display.
- Xoay ngang landscape.
- Giu man hinh sang trong luc chup.

## 5. Chay chup anh bang webcam

Mo PowerShell moi trong thu muc du an:

```powershell
cd C:\Users\Earmy\Downloads\deflectometry
.\.venv\Scripts\activate
python capture.py
```

Khi cua so camera hien len:

- Can chinh vat the, camera, va man hinh dien thoai.
- Bam `SPACE` de chup anh hien tai.
- Sau moi lan bam `SPACE`, dien thoai se tu nhay sang pattern tiep theo.
- Bam `R` de chup lai pattern truoc do.
- Bam `Q` de thoat som.

Thu tu chup tu dong:

```text
V0 -> V1 -> V2 -> V3 -> H0 -> H1 -> H2 -> H3
```

File anh se duoc luu vao thu muc:

```text
captures/
```

Vi du:

```text
captures/V0.png
captures/V1.png
captures/V2.png
captures/V3.png
captures/H0.png
captures/H1.png
captures/H2.png
captures/H3.png
```

## 6. Chay chup anh bang Basler

Neu dung camera Basler, can cai Basler pylon driver/runtime tren Windows truoc.

Sau do chay:

```powershell
cd C:\Users\Earmy\Downloads\deflectometry
.\.venv\Scripts\activate
python capture_basler.py
```

Cach bam phim giong webcam:

- `SPACE`: chup anh hien tai.
- `R`: chup lai pattern truoc.
- `Q`: thoat som.

## 7. Xu ly anh sau khi chup

Sau khi da co du 8 anh trong `captures/`, chay:

```powershell
cd C:\Users\Earmy\Downloads\deflectometry
.\.venv\Scripts\activate
python process.py
```

Ket qua se duoc luu thanh:

```text
results.png
```

## 8. Test dong bo frame khong can camera

Khi server dang chay va dien thoai da mo `viewer.html`, co the test doi frame bang PowerShell:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/set?idx=0"
Invoke-RestMethod "http://127.0.0.1:8000/api/set?idx=1"
Invoke-RestMethod "http://127.0.0.1:8000/api/set?idx=2"
```

Neu dien thoai doi pattern theo cac lenh tren, phan dong bo da hoat dong.

Map index:

```text
idx=0 -> V0
idx=1 -> V1
idx=2 -> V2
idx=3 -> V3
idx=4 -> H0
idx=5 -> H1
idx=6 -> H2
idx=7 -> H3
```

## 9. Tang thoi gian cho man hinh on dinh

Mac dinh sau khi doi frame, script cho khoang `0.35s`.

Neu can cho lau hon:

```powershell
$env:DEFLECTO_SETTLE_SEC="0.7"
python capture.py
```

Hoac voi Basler:

```powershell
$env:DEFLECTO_SETTLE_SEC="0.7"
python capture_basler.py
```

## 10. Dung qua USB ADB neu khong muon dung Wi-Fi

Neu dung Android va da cai ADB:

```powershell
adb reverse tcp:8000 tcp:8000
```

Sau do tren dien thoai mo:

```text
http://127.0.0.1:8000/viewer.html
```

Scrcpy co the dung de thao tac tren dien thoai tu may tinh, vi du bam `START`, nhung viec dong bo frame van do `control_server.py` va script chup thuc hien.

## 11. Tom tat thao tac hang ngay

May tinh:

```powershell
cd C:\Users\Earmy\Downloads\deflectometry
.\.venv\Scripts\activate
python control_server.py --host 0.0.0.0 --port 8000
```

Dien thoai:

```text
Mo http://<IP_MAY_TINH>:8000/viewer.html
Bam START
```

May tinh, cua so PowerShell khac:

```powershell
cd C:\Users\Earmy\Downloads\deflectometry
.\.venv\Scripts\activate
python capture.py
```

Sau khi chup xong:

```powershell
python process.py
```
