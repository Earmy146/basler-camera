# Hướng Dẫn Chạy Hệ Thống Deflectometry

Tài liệu này hướng dẫn cách chạy dự án theo chế độ đồng bộ: máy tính điều khiển frame đang hiển thị trên điện thoại, sau đó camera chụp đúng frame đó.

## Tóm Tắt

Khuyến nghị dùng **cáp USB + ADB reverse**.

Khi dùng cách này, điện thoại luôn mở cùng một địa chỉ:

```text
http://127.0.0.1:8000/viewer.html
```

Wi-Fi máy tính đổi, IPv4 máy tính đổi, hoặc chuyển sang mạng khác đều không ảnh hưởng.

## 1. Chuẩn Bị

- Máy tính Windows có thư mục dự án:

```text
C:\Users\Earmy\Downloads\deflectometry
```

- Điện thoại/tablet Android để hiển thị pattern.
- Cáp USB nối điện thoại với máy tính.
- Bật **USB debugging** trên điện thoại.
- Nếu muốn điều khiển điện thoại từ máy tính, có thể dùng `scrcpy`.
- Camera thật gắn vào máy tính:
  - Webcam thường: dùng `capture.py`
  - Camera Basler: dùng `capture_basler.py`

## 2. Máy Tính Cần Mở File Gì?

Máy tính cần mở 2 cửa sổ PowerShell:

1. Cửa sổ server:

```powershell
cd C:\Users\Earmy\Downloads\deflectometry
.\.venv\Scripts\activate
python control_server.py --host 0.0.0.0 --port 8000
```

Giữ cửa sổ này chạy. Đây là server phục vụ `viewer.html` và nhận lệnh đổi frame.

2. Cửa sổ chụp ảnh:

Webcam:

```powershell
cd C:\Users\Earmy\Downloads\deflectometry
.\.venv\Scripts\activate
python capture.py
```

Basler:

```powershell
cd C:\Users\Earmy\Downloads\deflectometry
.\.venv\Scripts\activate
python capture_basler.py
```

Khi chạy file chụp, script sẽ tự chạy:

```powershell
adb reverse tcp:8000 tcp:8000
```

Vì vậy nếu điện thoại đang cắm USB và đã bật USB debugging, bạn không cần tự nhập lệnh `adb reverse`.

## 3. Điện Thoại Cần Mở Gì?

Sau khi server trên máy tính đã chạy, mở trình duyệt trên điện thoại và vào:

```text
http://127.0.0.1:8000/viewer.html
```

Sau đó bấm `START`.

Lưu ý: địa chỉ này chỉ dùng được khi đã có ADB reverse qua USB. Script chụp sẽ tự chạy ADB reverse, nhưng nếu bạn mở viewer trước khi chạy script chụp thì có thể chạy thủ công một lần:

```powershell
adb reverse tcp:8000 tcp:8000
```

## 4. Cài Đặt Màn Hình Điện Thoại

Trước khi chụp thật:

- Kéo brightness lên MAX.
- Tắt Adaptive brightness.
- Tắt Eye comfort shield / Night light.
- Tắt Dark mode.
- Tắt Always-On Display.
- Xoay ngang landscape.
- Giữ màn hình sáng trong lúc chụp.

## 5. Quy Trình Chụp

1. Chạy server trên máy tính:

```powershell
python control_server.py --host 0.0.0.0 --port 8000
```

2. Cắm điện thoại bằng USB.

3. Mở trên điện thoại:

```text
http://127.0.0.1:8000/viewer.html
```

4. Bấm `START` trên điện thoại.

5. Chạy script chụp trên máy tính:

```powershell
python capture.py
```

hoặc:

```powershell
python capture_basler.py
```

6. Khi cửa sổ camera hiện lên, bấm `SPACE` để chụp từng ảnh.

Mỗi lần bấm `SPACE`:

```text
chụp frame hiện tại -> lưu ảnh -> điện thoại tự nhảy sang frame tiếp theo
```

Thứ tự frame:

```text
V0 -> V1 -> V2 -> V3 -> H0 -> H1 -> H2 -> H3
```

Các phím:

- `SPACE`: chụp frame hiện tại.
- `R`: quay lại và chụp lại frame trước.
- `Q`: thoát sớm.

## 6. Ảnh Được Lưu Ở Đâu?

Ảnh chụp được lưu trong thư mục:

```text
captures/
```

Tên file:

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

## 7. Xử Lý Ảnh Sau Khi Chụp

Sau khi đã chụp đủ 8 ảnh, chạy:

```powershell
python process.py
```

Kết quả được lưu thành:

```text
results.png
```

## 8. Test Đồng Bộ Không Cần Camera

Khi server đang chạy và điện thoại đã mở `viewer.html`, có thể test đổi frame bằng PowerShell:

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/set?idx=0"
Invoke-RestMethod "http://127.0.0.1:8000/api/set?idx=1"
Invoke-RestMethod "http://127.0.0.1:8000/api/set?idx=2"
```

Nếu điện thoại đổi pattern theo các lệnh trên thì phần đồng bộ đã hoạt động.

Bảng index:

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

## 9. Nếu Điện Thoại Không Mở Được 127.0.0.1

Kiểm tra lần lượt:

- Điện thoại đã cắm USB chưa.
- Đã bật USB debugging chưa.
- Trên điện thoại đã bấm cho phép debug từ máy tính chưa.
- Máy tính có nhận lệnh `adb` chưa:

```powershell
adb devices
```

Nếu thấy thiết bị ở trạng thái `unauthorized`, mở màn hình điện thoại và bấm cho phép USB debugging.

Nếu không muốn dùng USB, có thể dùng Wi-Fi bằng địa chỉ IP máy tính:

```text
http://<IP_MAY_TINH>:8000/viewer.html
```

Nhưng cách Wi-Fi sẽ phải đổi URL nếu IPv4 máy tính thay đổi.

## 10. Tăng Thời Gian Chờ Màn Hình Ổn Định

Mặc định sau khi đổi frame, script chờ khoảng `0.35s`.

Nếu cần chờ lâu hơn:

```powershell
$env:DEFLECTO_SETTLE_SEC="0.7"
python capture.py
```

Hoặc với Basler:

```powershell
$env:DEFLECTO_SETTLE_SEC="0.7"
python capture_basler.py
```

## 11. Tắt ADB Reverse Tự Động

Mặc định script chụp tự chạy `adb reverse`.

Nếu muốn tắt:

```powershell
$env:DEFLECTO_ADB_REVERSE="0"
python capture.py
```

## 12. Quy Trình Ngắn Gọn Hằng Ngày

PowerShell 1:

```powershell
cd C:\Users\Earmy\Downloads\deflectometry
.\.venv\Scripts\activate
python control_server.py --host 0.0.0.0 --port 8000
```

Điện thoại:

```text
Mở http://127.0.0.1:8000/viewer.html
Bấm START
```

PowerShell 2:

```powershell
cd C:\Users\Earmy\Downloads\deflectometry
.\.venv\Scripts\activate
python capture.py
```

Sau khi chụp xong:

```powershell
python process.py
```
