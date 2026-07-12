from DobotEDU import *
import cv2
import numpy as np
import time

BASE_DIR = "C:/Users/SANG/OneDrive/May tinh/cach tay"
MATRIX_PATH = BASE_DIR + "/matrix.npy"
BOX_PATH = BASE_DIR + "/box_positions.npy"

matrix = np.load(MATRIX_PATH)
box_positions = np.load(BOX_PATH, allow_pickle=True).item()

SCAN_X, SCAN_Y, SCAN_Z, SCAN_R = 250, 0, 50, 0
PICK_Z = -30
WAIT_WHEN_EMPTY = 1

WINDOW_NAME = "Camera - dang chay chuong trinh"

COLOR_RANGES = {
    "RED":    [((0, 120, 70), (10, 255, 255)), ((170, 120, 70), (180, 255, 255))],
    "YELLOW": [((20, 100, 100), (35, 255, 255))],
    "GREEN":  [((36, 80, 70), (85, 255, 255))],
    "BLUE":   [((90, 80, 70), (130, 255, 255))],
}

COLOR_DISPLAY = {
    "RED": (0, 0, 255),
    "YELLOW": (0, 255, 255),
    "GREEN": (0, 255, 0),
    "BLUE": (255, 0, 0),
}

def detect_colored_object(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    best_color = None
    best_area = 0
    best_center = None

    for color, ranges in COLOR_RANGES.items():
        mask = None
        for lower, upper in ranges:
            m = cv2.inRange(hsv, np.array(lower), np.array(upper))
            mask = m if mask is None else (mask | m)

        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            continue

        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        if area < 300:
            continue

        if area > best_area:
            M = cv2.moments(largest)
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            best_area = area
            best_color = color
            best_center = (cx, cy)

    if best_color is None:
        return None
    return (best_center[0], best_center[1], best_color)

def pixel_to_robot(px, py, matrix):
    point = np.array([[[px, py]]], dtype=np.float32)
    result = cv2.perspectiveTransform(point, matrix)
    return result[0][0]

def show_frame(cap, status_text=""):
    ret, frame = cap.read()
    if not ret or frame is None:
        return None, None
    result = detect_colored_object(frame)
    display = frame.copy()
    if result is not None:
        px, py, color = result
        draw_color = COLOR_DISPLAY.get(color, (255, 255, 255))
        cv2.circle(display, (px, py), 10, draw_color, 2)
        cv2.putText(display, color, (px + 15, py), cv2.FONT_HERSHEY_SIMPLEX, 0.7, draw_color, 2)
    if status_text:
        cv2.putText(display, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.imshow(WINDOW_NAME, display)
    cv2.waitKey(1)
    return result, frame

def wait_and_show(cap, seconds, status_text=""):
    end_time = time.time() + seconds
    while time.time() < end_time:
        show_frame(cap, status_text)
        time.sleep(0.03)

m_lite.set_homecmd()
cap = cv2.VideoCapture(0)
wait_and_show(cap, 3, "Dang ve home...")

item_count = 0
print("Bat dau chay lien tuc. Bam nut Stop (do) trong DobotLab de dung chuong trinh.")

while True:
    m_lite.set_ptpcmd(ptp_mode=0, x=SCAN_X, y=SCAN_Y, z=SCAN_Z, r=SCAN_R)
    wait_and_show(cap, 1.5, "Dang di chuyen den scan pose...")

    result, frame = show_frame(cap, "Dang quet tim vat...")

    if result is None:
        print("Chua thay vat nao, doi", WAIT_WHEN_EMPTY, "giay roi quet lai...")
        wait_and_show(cap, WAIT_WHEN_EMPTY, "Khong thay vat...")
        continue

    px, py, color = result
    robot_x, robot_y = pixel_to_robot(px, py, matrix)
    item_count += 1
    print("Vat so", item_count, "- mau:", color, "- pixel:", (px, py), "- robot:", (round(float(robot_x), 1), round(float(robot_y), 1)))

    if color not in box_positions:
        print("CANH BAO: chua co vi tri hop cho mau", color, ", bo qua vat nay.")
        wait_and_show(cap, WAIT_WHEN_EMPTY, "Chua co hop cho mau " + color)
        continue

    place_x, place_y, place_z = box_positions[color]

    m_lite.set_endeffector_gripper(enable=True, on=False)
    wait_and_show(cap, 0.5, "Mo gripper...")
    m_lite.set_ptpcmd(ptp_mode=0, x=float(robot_x), y=float(robot_y), z=SCAN_Z, r=0)
    wait_and_show(cap, 1, "Di chuyen den phia tren vat " + color + "...")
    m_lite.set_ptpcmd(ptp_mode=0, x=float(robot_x), y=float(robot_y), z=PICK_Z, r=0)
    wait_and_show(cap, 1, "Ha xuong...")
    m_lite.set_endeffector_gripper(enable=True, on=True)
    wait_and_show(cap, 0.8, "Dong gripper - gap vat...")
    m_lite.set_ptpcmd(ptp_mode=0, x=float(robot_x), y=float(robot_y), z=SCAN_Z, r=0)
    wait_and_show(cap, 1, "Nang len...")

    m_lite.set_ptpcmd(ptp_mode=0, x=float(place_x), y=float(place_y), z=SCAN_Z, r=0)
    wait_and_show(cap, 1.5, "Di chuyen den hop " + color + "...")
    m_lite.set_ptpcmd(ptp_mode=0, x=float(place_x), y=float(place_y), z=float(place_z), r=0)
    wait_and_show(cap, 1, "Ha xuong hop...")
    m_lite.set_endeffector_gripper(enable=True, on=False)
    wait_and_show(cap, 0.5, "Nha vat vao hop " + color + "...")
    m_lite.set_ptpcmd(ptp_mode=0, x=float(place_x), y=float(place_y), z=SCAN_Z, r=0)
    wait_and_show(cap, 1, "Nang len khoi hop...")
