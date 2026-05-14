#!/usr/bin/env python3
import rospy
from std_msgs.msg import String, Int32, Bool
import torch
import cv2
import numpy as np
import time
import os
import math

import sys
import numpy.core.multiarray
sys.modules['numpy._core'] = sys.modules['numpy.core']
sys.modules['numpy._core.multiarray'] = sys.modules['numpy.core.multiarray']

current_waypoint = -1
camera_enabled = False

def waypoint_callback(msg):
    global current_waypoint
    current_waypoint = msg.data

def camera_enable_callback(msg):
    global camera_enabled
    camera_enabled = bool(msg.data)

CAMERA_SYMLINK = '/dev/rga_cam'


def open_camera():
    """Open the camera using the standard video0 path.
    Since the powered hub prevents brownouts, the camera will not device-hop.
    """
    cam_path = '/dev/video0'
    
    # Quick fallback just in case it initialized weirdly on boot
    if not os.path.exists(cam_path):
        if os.path.exists('/dev/video1'):
            cam_path = '/dev/video1'
        else:
            return None

    print(f"[RGA VISION] Opening camera on {cam_path}...")
    cap = cv2.VideoCapture(cam_path, cv2.CAP_V4L2)
    
    if not cap.isOpened():
        print(f"[RGA VISION] CRITICAL: cannot open {cam_path}")
        return None

    # Request the optimal settings (The Hub may override these, which is fine)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    time.sleep(1.0)

    # Read back what the Hub/Driver actually gave us
    fourcc_int = int(cap.get(cv2.CAP_PROP_FOURCC))
    fourcc_str = "".join(chr((fourcc_int >> (8 * i)) & 0xFF) for i in range(4))
    actual_w   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"[RGA VISION] Camera Locked In: {fourcc_str} {actual_w}x{actual_h} @ {actual_fps:.1f} fps")
    
    if fourcc_str != "MJPG":
        print(f"[RGA VISION] Note: Running in {fourcc_str} mode via USB Hub. Bandwidth is higher, but power is stable.")

    return cap


def run_vision():
    rospy.init_node('rga_vision', anonymous=True)
    vision_pub = rospy.Publisher('/vision_detections', String, queue_size=10)
    rospy.Subscriber('/scan_waypoint', Int32, waypoint_callback)
    rospy.Subscriber('/vision_camera_enable', Bool, camera_enable_callback)

    print("[RGA VISION] Loading YOLOv5 Model...")
    yolo_repo_path = os.path.expanduser('~/yolov5')
    model_path = os.path.expanduser('~/yolov5/best.pt')
    model = torch.hub.load(yolo_repo_path, 'custom', path_or_model=model_path, source='local', force_reload=True)
    model.conf = 0.25
    model.max_det = 20

    # Default state: camera CLOSED. Arm controller publishes True on
    # /vision_camera_enable when a scan starts, False when it ends. This
    # is the entire point of the rewrite — between scans the camera is
    # off the USB hub completely, freeing bandwidth for the ESP32 and
    # touchscreen and preventing the chronic UVC drops.
    cap = None
    print("[RGA VISION] Idle. Waiting for scan trigger on /vision_camera_enable...")

    try:
        while not rospy.is_shutdown():
            # ── DISABLED PATH ────────────────────────────────────────
            # No scan in progress: ensure the device is released and
            # spin slowly. Polling at 10 Hz is plenty — open latency
            # already dominates (~1 s warmup).
            if not camera_enabled:
                if cap is not None:
                    print("[RGA VISION] Scan complete — releasing camera.")
                    cap.release()
                    cap = None
                time.sleep(0.1)
                continue

            # ── ENABLED, NEED-TO-OPEN ────────────────────────────────
            if cap is None:
                cap = open_camera()
                if cap is None:
                    # Symlink missing or device busy. Back off and retry
                    # while the scan window is still open.
                    time.sleep(0.5)
                    continue

            # ── ENABLED, SHUTTER CLOSED ──────────────────────────────
            # Camera is open and streaming, but the arm hasn't reached
            # a scan cell yet. Drain one frame to keep the buffer fresh,
            # don't run YOLO. No retry-to-reopen burst here — the next
            # cap.read() will catch a drop.
            if current_waypoint == -1:
                cap.grab()
                time.sleep(0.02)
                continue

            # ── ENABLED, SHUTTER OPEN — run YOLO ─────────────────────
            ret, frame = cap.read()
            if not ret:
                print("[RGA VISION] Frame read failed mid-scan — camera dropped.")
                cap.release()
                cap = None
                time.sleep(0.5)
                continue

            results = model(frame)
            detections = results.pandas().xyxy[0]

            current_frame_data = []
            if not detections.empty:
                for _, row in detections.iterrows():
                    name = row['name']
                    xmin, ymin, xmax, ymax = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])

                    box_center_x = (xmin + xmax) / 2
                    box_center_y = (ymin + ymax) / 2
                    distance_from_center = math.sqrt((box_center_x - 320) ** 2 + (box_center_y - 240) ** 2)

                    if distance_from_center < 180:
                        current_frame_data.append(f"{name.upper()}:{current_waypoint}")

            if current_frame_data:
                vision_pub.publish(",".join(current_frame_data))

    except KeyboardInterrupt:
        print("\n[RGA VISION] Shutting Down.")
    finally:
        if cap is not None:
            cap.release()

def load_model():
    print("[RGA VISION] Loading YOLOv5 Model...")
    yolo_repo_path = os.path.expanduser('~/yolov5')
    model_path = os.path.expanduser('~/yolov5/best.pt') 
    model = torch.hub.load(yolo_repo_path, 'custom', path_or_model=model_path, source='local', force_reload=True)
    model.conf = 0.25 
    model.max_det = 20
    return model

def run_debug_vision():
    #"""DEBUG MODE: Saves annotated frames to a folder, bypassing GTK errors."""
    model = load_model()

    print("[RGA DEBUG] Starting Headless Debug Camera...")
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(1)

    if not cap.isOpened():
        print("[RGA DEBUG] CRITICAL ERROR: Could not open the camera port.")
        return

    # Create the debug directory
    save_dir = os.path.join(os.path.dirname(__file__), "debug_output")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "latest_frame.jpg")

    print("=========================================")
    print(" RGA VISION HEADLESS DEBUG ONLINE ")
    print(f" -> Saving live frames to: {save_path}")
    print(" -> Press Ctrl+C in the terminal to quit.")
    print("=========================================")

    try:
        while True:
            ret, frame = cap.read()
            if not ret: continue

            # Pass frame to AI
            results = model(frame)
            detections = results.pandas().xyxy[0]
            
            # --- Draw the 350px ROI boundary circle for visual debugging ---
            cv2.circle(frame, (320, 240), 150, (0, 255, 255), 2) # Yellow circle

            # Parse Detections and Draw Bounding Boxes
            if not detections.empty:
                for index, row in detections.iterrows():
                    name = row['name']
                    conf = row['confidence']
                    xmin, ymin, xmax, ymax = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
                    
                    # ROI Check for Debug Mode Colors
                    box_center_x = (xmin + xmax) / 2
                    box_center_y = (ymin + ymax) / 2
                    distance_from_center = math.sqrt((box_center_x - 320)**2 + (box_center_y - 240)**2)
                    
                    if distance_from_center < 150:
                        # Choose a color: Green for 'X', Blue for 'O' (BGR format)
                        color = (0, 255, 0) if name.upper() == 'X' else (255, 0, 0)
                    else:
                        # Grey out shapes that are outside the ROI
                        color = (128, 128, 128) 
                    
                    # Draw Rectangle
                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
                    
                    # Draw Label & Confidence
                    label = f"{name} {conf:.2f}"
                    cv2.putText(frame, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # Overwrite the latest frame (NO cv2.imshow!)
            cv2.imwrite(save_path, frame)
            
            # Print a terminal heartbeat so you know it's working
            print(f"[RGA DEBUG] Frame updated at {time.strftime('%H:%M:%S')} - Detections: {len(detections)}")

            # Wait 2 seconds before grabbing the next frame
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\n[RGA DEBUG] Shutting Down.")
    finally:
        cap.release()


if __name__ == '__main__':
    run_vision()         # Use this when playing the actual game
    #run_debug_vision()   # Use this to test your best.pt model