# CNPM

## Yêu cầu

Tối thiểu phải có những thứ này cài sẵn:

- Node.js + npm
- Python 3

Nếu trong quá trình chạy mà có bị báo lỗi thiếu thư viện của python thì chỉ cần dùng "pip install <tên thư viện>".<br>
Nếu trong quá trình chạy Frontend mà bị báo lỗi thiếu thư viện gì thì chỉ cần dùng "npm install <tên thư viện>".

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