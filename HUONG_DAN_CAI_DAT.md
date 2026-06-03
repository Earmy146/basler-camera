# Hướng Dẫn Cài Đặt Môi Trường

Tài liệu này hướng dẫn cách cài Python, tạo môi trường ảo, cài thư viện, ADB, và các phần cần thiết để chạy dự án Deflectometry.

## 1. Yêu Cầu Chung

Máy tính Windows cần có:

- Python 3.11 64-bit.
- Git, nếu muốn quản lý phiên bản.
- ADB, nếu dùng điện thoại Android qua USB.
- Basler pylon runtime, nếu dùng camera Basler.

Phiên bản Python đã kiểm tra chạy được:

```text
Python 3.11.9
```

## 2. Kiểm Tra Python

Mở Command Prompt hoặc PowerShell:

```powershell
python --version
```

Kết quả mong muốn:

```text
Python 3.11.x
```

Kiểm tra `pip`:

```powershell
python -m pip --version
```

Nếu Windows không nhận lệnh `python`, cần cài Python và chọn tùy chọn **Add python.exe to PATH** khi cài.

## 3. Vào Thư Mục Dự Án

```powershell
cd C:\Users\Earmy\Downloads\deflectometry
```

## 4. Tạo Virtual Environment

Chạy:

```powershell
python -m venv .venv
```

Sau đó kích hoạt:

```powershell
.\.venv\Scripts\activate
```

Nếu kích hoạt thành công, PowerShell sẽ có tiền tố kiểu:

```text
(.venv)
```

## 5. Cài Thư Viện Python

Sau khi đã kích hoạt `.venv`, chạy:

```powershell
python -m pip install numpy matplotlib opencv-python pypylon
```

Các thư viện chính:

- `numpy`: tính toán ma trận/ảnh.
- `matplotlib`: hiển thị và lưu kết quả.
- `opencv-python`: mở camera webcam, xử lý ảnh, lưu ảnh.
- `pypylon`: giao tiếp camera Basler.

Nếu chỉ dùng webcam và không dùng Basler, vẫn có thể cài đủ như trên. Không ảnh hưởng tới webcam.

## 6. Kiểm Tra Thư Viện Đã Cài

Chạy:

```powershell
python -c "import cv2, numpy, matplotlib, pypylon; print('OK')"
```

Nếu in ra:

```text
OK
```

thì thư viện Python đã ổn.

Có thể kiểm tra phiên bản:

```powershell
python -c "import cv2, numpy, matplotlib; print(cv2.__version__); print(numpy.__version__); print(matplotlib.__version__)"
```

## 7. Cài ADB Cho Android

ADB cần thiết nếu muốn điện thoại mở cố định:

```text
http://127.0.0.1:8000/viewer.html
```

Khi đó không phụ thuộc IP Wi-Fi của máy tính.

### Cách Cài ADB

Khuyến nghị cài Android Platform Tools từ Google.

Sau khi cài, kiểm tra:

```powershell
adb version
```

Kết quả ví dụ:

```text
Android Debug Bridge version 1.0.41
```

Nếu PowerShell báo không tìm thấy `adb`, cần thêm thư mục `platform-tools` vào PATH.

Ví dụ đường dẫn thường gặp:

```text
C:\Users\<TEN_USER>\AppData\Local\Android\Sdk\platform-tools
```

## 8. Bật USB Debugging Trên Điện Thoại

Trên Android:

1. Mở `Settings`.
2. Vào `About phone`.
3. Bấm nhiều lần vào `Build number` để bật Developer options.
4. Vào `Developer options`.
5. Bật `USB debugging`.
6. Cắm điện thoại vào máy tính bằng USB.
7. Trên điện thoại, bấm cho phép USB debugging nếu có hộp thoại xác nhận.

Kiểm tra máy tính đã thấy điện thoại:

```powershell
adb devices
```

Kết quả tốt sẽ giống:

```text
List of devices attached
XXXXXXXX	device
```

Nếu thấy:

```text
unauthorized
```

hãy mở màn hình điện thoại và bấm cho phép USB debugging.

## 9. Kiểm Tra ADB Reverse

Chạy:

```powershell
adb reverse tcp:8000 tcp:8000
```

Nếu thành công, thường sẽ trả về:

```text
8000
```

Trong dự án này, `capture.py` và `capture_basler.py` đã tự chạy lệnh trên khi bắt đầu chụp. Bước kiểm tra này chỉ để xác nhận máy đã cài ADB đúng.

## 10. Cài Basler Pylon Nếu Dùng Camera Basler

Nếu dùng `capture_basler.py`, cần:

- Cài `pypylon` trong Python.
- Cài Basler pylon Camera Software Suite trên Windows.
- Cắm camera Basler qua USB3 hoặc GigE.
- Kiểm tra camera nhận được trong phần mềm Basler pylon Viewer.

Nếu không dùng Basler, có thể bỏ qua bước này.

## 11. Kiểm Tra Webcam

Nếu dùng webcam thường, không cần driver đặc biệt trong đa số trường hợp.

Chạy:

```powershell
python capture.py
```

Nếu camera không mở được, kiểm tra:

- Camera đã cắm USB chưa.
- Có app khác đang chiếm camera không.
- Windows Privacy Settings có cho app desktop dùng camera không.
- Trong `capture.py`, biến `CAM_INDEX` có đúng không.

Mặc định:

```python
CAM_INDEX = 0
```

Nếu máy có nhiều camera, có thể cần đổi thành:

```python
CAM_INDEX = 1
```

hoặc:

```python
CAM_INDEX = 2
```

## 12. Chạy Thử Xử Lý Ảnh Không Cần Camera

Dự án có sẵn ảnh mẫu trong thư mục `captures/`.

Chạy:

```powershell
python process.py
```

Nếu chạy đúng, chương trình sẽ tạo:

```text
results.png
```

## 13. Lệnh Cài Đặt Nhanh Từ Đầu

Nếu Python và ADB đã có sẵn, có thể setup nhanh:

```powershell
cd C:\Users\Earmy\Downloads\deflectometry
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install numpy matplotlib opencv-python pypylon
python -c "import cv2, numpy, matplotlib, pypylon; print('OK')"
```

Sau đó xem hướng dẫn chạy trong:

```text
HUONG_DAN_CHAY.md
```

## 14. Lỗi Thường Gặp

### Không tìm thấy `cv2`

Chưa cài OpenCV:

```powershell
python -m pip install opencv-python
```

### Không tìm thấy `numpy`

Chưa cài NumPy:

```powershell
python -m pip install numpy
```

### Không tìm thấy `pypylon`

Chưa cài pypylon:

```powershell
python -m pip install pypylon
```

Nếu vẫn không nhận camera Basler, cần cài thêm Basler pylon runtime.

### Không tìm thấy `adb`

ADB chưa được cài hoặc chưa nằm trong PATH.

Kiểm tra:

```powershell
adb version
```

Nếu lỗi, cài Android Platform Tools và thêm `platform-tools` vào PATH.

### Điện thoại không mở được `127.0.0.1:8000`

Kiểm tra:

```powershell
adb devices
adb reverse tcp:8000 tcp:8000
```

Sau đó mở lại trên điện thoại:

```text
http://127.0.0.1:8000/viewer.html
```
