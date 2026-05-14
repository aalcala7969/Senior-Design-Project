 #!/usr/bin/env python3
import cv2
import os

# Create a folder to hold your new photos
save_dir = "roboflow_dataset"
os.makedirs(save_dir, exist_ok=True)

print("[RGA DATASET] Booting Camera...")
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

# FORCE the exact resolution your robot plays at (Critical for training accuracy)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("[RGA DATASET] CRITICAL ERROR: Could not open the camera port.")
    exit()

img_count = 0
print("\n======================================")
print(" RGA DATASET COLLECTOR ONLINE")
print("======================================")
print(" -> Press SPACEBAR to capture an image.")
print(" -> Press ESC to quit.")
print("======================================\n")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Show the live feed so you can aim the camera
        cv2.imshow("Dataset Collector", frame)

        # Wait for a key press (1ms delay)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # ESC key to exit
            print("[RGA DATASET] Shutting down collector.")
            break
        elif key == 32:  # SPACEBAR to take a photo
            filename = os.path.join(save_dir, f"rga_train_{img_count:04d}.jpg")
            cv2.imwrite(filename, frame)
            print(f"[RGA DATASET] Captured: {filename}")
            img_count += 1

except KeyboardInterrupt:
    print("\n[RGA DATASET] Script interrupted.")
finally:
    cap.release()
    cv2.destroyAllWindows()