# Xây dựng hệ thống robot thông minh nhận diện màu sắc và phân loại vật thể tự động

Hệ thống robot Dobot kết hợp camera để tự động nhận diện vật theo màu (đỏ, vàng, xanh lá, xanh dương), gắp và đặt vào hộp tương ứng.

## Luồng hoạt động
1. Cali.py — hiệu chuẩn camera ↔ robot, lưu vị trí 4 hộp màu.
2. gapthietbi.py — robot quét camera, nhận diện màu bằng HSV.
3. Chuyển tọa độ pixel → tọa độ robot → di chuyển, gắp vật bằng gripper.
4. Đặt vật vào hộp đúng màu → lặp lại.

## Công nghệ sử dụng
- Phần cứng: Cánh tay robot Dobot Magician Lite, Gripper, Webcam
- Ngôn ngữ: Python 3
- Thư viện: DobotEDU, OpenCV, NumPy
- Thuật toán: Nhận diện màu HSV, Perspective Transform
- Môi trường: DobotLab
