#!/usr/bin/env python3
import rospy
from std_msgs.msg import String, Int32
import torch
import cv2
import time
import os
import math
import sys

import numpy.core.multiarray
sys.modules['numpy._core'] = sys.modules['numpy.core']
sys.modules['numpy._core.multiarray'] = sys.modules['numpy.core.multiarray']

current_waypoint = -1

def waypoint_callback(msg):
    global current_waypoint
    current_waypoint = msg.data

def run_vision():
    rospy.init_node('rga_hm_vision', anonymous=True)
    vision_pub = rospy.Publisher('/vision_detections', String, queue_size=10)
    rospy.Subscriber('/scan_waypoint', Int32, waypoint_callback)
    
    print("[RGA HANGMAN VISION] Loading YOLOv5 Model...")
    yolo_repo_path = os.path.expanduser('~/yolov5')
    model_path = os.path.expanduser('~/yolov5/best.pt') 
    model = torch.hub.load(yolo_repo_path, 'custom', path_or_model=model_path, source='local', force_reload=True)
    model.conf = 0.25 
    model.max_det = 20 # Keep at 20 to read all written letters

    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(1)

    try:
        while not rospy.is_shutdown():
            ret, frame = cap.read()
            
            if not ret:
                cap.release()
                camera_found = False
                target_port = 0
                while not camera_found and not rospy.is_shutdown():
                    time.sleep(1.0)
                    if os.path.exists('/dev/video0'):
                        target_port = 0; camera_found = True
                    elif os.path.exists('/dev/video1'):
                        target_port = 1; camera_found = True
                cap = cv2.VideoCapture(target_port, cv2.CAP_V4L2)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                time.sleep(1.0) 
                continue 

            if current_waypoint == -1:
                continue 

            # ---> HANGMAN IMAGE PROCESSING INJECTION <---
            # Rotate 180 degrees
            frame = cv2.rotate(frame, cv2.ROTATE_180)
            # Spatial Inversion (Mirroring Horizontally)
            frame = cv2.flip(frame, 1)
            
            # Pass modified frame to YOLO
            results = model(frame)
            detections = results.pandas().xyxy[0]
            
            current_frame_data = []
            if not detections.empty:
                for index, row in detections.iterrows():
                    name = row['name']
                    xmin, ymin, xmax, ymax = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
                    
                    box_center_x = (xmin + xmax) / 2
                    box_center_y = (ymin + ymax) / 2
                    distance_from_center = math.sqrt((box_center_x - 320)**2 + (box_center_y - 240)**2)
                    
                    # Wide 250px ROI to catch multiple letters in the zone
                    if distance_from_center < 250:
                        current_frame_data.append(f"{name.upper()}:{current_waypoint}")

            if current_frame_data:
                msg = ",".join(current_frame_data)
                vision_pub.publish(msg)

    except KeyboardInterrupt:
        print("\n[RGA HANGMAN VISION] Shutting Down.")
    finally:
        cap.release()

if __name__ == '__main__':
    run_vision()