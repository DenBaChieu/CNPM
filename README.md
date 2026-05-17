# CNPM

## Yêu cầu

Tối thiểu phải có những thứ này cài sẵn:

- Node.js + npm
- Python 3

Nếu trong quá trình chạy mà có bị báo lỗi thiếu thư viện của python thì chỉ cần dùng "pip install <tên thư viện>".<br>
Nếu trong quá trình chạy Frontend mà bị báo lỗi thiếu thư viện gì thì chỉ cần dùng "npm install <tên thư viện>".

## Thư viện cần

Python:

- apscheduler
- fastapi
- pydantic
- uvicorn

React:

- qrcode.react

## Frontend Setup

1. Tạo 1 terminal mới.
2. Vào folder "Frontend" bằng lệnh "cd Frontend".
3. Chạy lệnh "npm run dev".

## Backend Setup

1. Tạo 1 terminal mới.
2. Vào folder "Backend" bằng lệnh "cd Backend".
3. Chạy file main.py bằng cách dùng VSCode, PyEditor hoặc chạy lệnh "python main.py".

## Thông tin chung

- Folder "Database" là dùng để chứa những file đuôi .db để làm cơ sở dữ liệu cho backend.
- File main.py là nơi tạo ra những Sensor, ParkingSlot, ParkingZone,... và những dữ liệu này được cho trước trong file và không thay đổi được trừ khi khởi động lại server.
- Để tắt server thì chỉ cần ấn CTRL + C, tương tự cho Frontend.
- Frontend sử dụng Vite + React + Tailwind
- Tài khoản admin dùng để kiểm thử:
    - id: 0
    - password: Admin

# Flow

# Tạo tài khoản sinh viên

1. Đăng nhập bằng tài khoản admin.
2. Ấn "Tạo tài khoản".
3. Nhập thông tin sinh viên.
4. Ấn "Tạo".

## Sinh viên gửi xe

1. Sử dụng tài khoản admin, bắt đầu chu kỳ thanh toán.
2. Ấn "Vào cổng" ở trang login.
3. Nhập thông tin, lưu ý: tài khoản sinh viên phải được tạo trước.
4. Ấn "Vào cổng".
5. Nhập mã sensor. Cấu trúc mã sensor: [CS1/CS2]-Sensor[1-150]. Ví dụ: CS1-Sensor50
6. Nhập vào biển số xe như biển số xe lúc xe vào cổng (không là sẽ bị lỗi).
7. Ấn "Gửi dữ liệu" để mô phỏng cảm biến IoT.
8. Xóa dữ liệu biển số xe (lúc này IoT sẽ coi như xe đã rời khỏi chỗ đậu).
9. Ấn "Gửi dữ liệu" để mô phỏng cảm biến IoT.
10. Ở trang "Cổng ra", nhập vào thông tin và ấn "Ra cổng".
11. Đăng nhập vào tài khoản admin và kết thúc chu kỳ thanh toán.

## Khách vãng lai gửi xe

1. Ấn "Vào cổng" ở trang login
2. Nhập thông tin trừ "MSSV" ra.
3. Ấn "Cấp vé tạm".
4. Mô phỏng sensor như ở trên.
5. Khi ấn "Ra cổng" sẽ được di chuyển tới trang "ticket". Mục đích của trang này là để làm giao diện cho việc mô phỏng việc trả tiền gửi xe ở ngoài đời.
6. Ấn trả để mô phỏng việc trả tiền và backend sẽ nhận được thông tin và cập nhật.
7. Ngoài đời thì nhân viên sẽ mở cổng cho khách vãng lai ra ngoài.

## Sinh viên thanh toán phí

1. Sau khi kết thúc chu kỳ thanh toán, đăng nhập vào tài khoản sinh viên.
2. Vào trang thanh toán.
3. Lúc này, trang web sẽ hiện 1 hoặc nhiều hóa đơn đã hoặc chưa thanh toán.
4. Ấn nút thanh toán để mô phỏng việc sinh viên quét mã QR và thanh toán qua BKPay và BKPay gửi API về backend.