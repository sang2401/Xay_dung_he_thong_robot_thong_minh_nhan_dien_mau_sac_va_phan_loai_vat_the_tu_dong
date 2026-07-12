from DobotEDU import *
import cv2
import numpy as np
import time
import os

BASE_DIR = "C:/Users/SANG/OneDrive/May tinh/cach tay"
SAVE_PATH = BASE_DIR + "/matrix.npy"
IMG_PATH = BASE_DIR + "/calib_frame.jpg"
BOX_PATH = BASE_DIR + "/box_positions.npy"

os.makedirs(BASE_DIR, exist_ok=True)

SCAN_X, SCAN_Y, SCAN_Z, SCAN_R = 250, 0, 50, 0

m_lite.set_homecmd()
time.sleep(3)

m_lite.set_ptpcmd(ptp_mode=0, x=SCAN_X, y=SCAN_Y, z=SCAN_Z, r=SCAN_R)
time.sleep(1.5)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Khong mo duoc camera.")
else:
    print("Dang hien thi camera xem truoc. Nhan phim 'q' de dong va tiep tuc chup anh calib.")
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Khong doc duoc frame.")
            break
        cv2.imshow("Xem truoc camera - nhan q de dong va chup anh calib", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
print("Da dong xem truoc. Tiep tuc chup anh calib...")

time.sleep(1)
for i in range(5):
    cap.read()
    time.sleep(0.1)

ret, frame = cap.read()
if not ret or frame is None:
    print("Khong doc duoc frame, kiem tra lai camera.")
else:
    cv2.imwrite(IMG_PATH, frame)
    print("Da luu anh calib_frame.jpg, kich thuoc:", frame.shape)

cap.release()

img = cv2.imread(IMG_PATH)
pixel_points = []

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel_points.append((x, y))
        print("Diem pixel so", len(pixel_points), ":", (x, y))
        cv2.circle(img, (x, y), 6, (0, 255, 0), -1)
        cv2.imshow("Click 4 diem moc theo thu tu", img)

cv2.imshow("Click 4 diem moc theo thu tu", img)
cv2.setMouseCallback("Click 4 diem moc theo thu tu", click_event)
print("Click lan luot 4 diem moc tren anh, nho dung thu tu.")
cv2.waitKey(0)
cv2.destroyAllWindows()

if len(pixel_points) != 4:
    print("LOI: phai click dung 4 diem! So diem da click:", len(pixel_points))
else:
    print("")
    print("===== DO TOA DO THAT CHO 4 DIEM MOC (calibrate ma tran) =====")
    robot_points = []
    for i in range(4):
        input("Da dua tay den diem moc so " + str(i + 1) + " chua? Nhan Enter de doc toa do...")
        pose = m_lite.get_pose()
        rx, ry = pose['x'], pose['y']
        robot_points.append((rx, ry))
        print("Da luu diem so", i + 1, ":", (rx, ry))

    src = np.float32(pixel_points)
    dst = np.float32(robot_points)
    matrix = cv2.getPerspectiveTransform(src, dst)
    np.save(SAVE_PATH, matrix)
    print("Da luu ma tran calibrate vao", SAVE_PATH)
    print(matrix)

    print("")
    print("===== DAY VI TRI 4 HOP DUNG THEO MAU =====")
    print("Voi tung hop, nhan giu nut Unlock, keo tay den dung vi tri phia tren hop, tha Unlock,")
    print("roi nhan Enter de doc va luu toa do.")
    print("")

    colors = ["RED", "YELLOW", "GREEN", "BLUE"]
    box_positions = {}

    for color in colors:
        input("Da dua tay den hop mau " + color + " chua? Nhan Enter de doc toa do...")
        pose = m_lite.get_pose()
        bx, by, bz = pose['x'], pose['y'], pose['z']
        box_positions[color] = (bx, by, bz)
        print("Da luu vi tri hop", color, ":", (bx, by, bz))

    np.save(BOX_PATH, box_positions, allow_pickle=True)
    print("")
    print("Da luu vi tri 4 hop vao", BOX_PATH)
    print(box_positions)
