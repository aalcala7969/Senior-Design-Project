#!/usr/bin/env python3
import rospy
from std_msgs.msg import String, Int32, Bool
from Arm_Lib import Arm_Device
import time
import os
import threading

class ArmController:
    def __init__(self):
        rospy.init_node('rga_arm_controller', anonymous=True)
        # Initialize the hardware EXACTLY ONCE
        self.arm = Arm_Device()
        time.sleep(0.1)
        self.arm.Arm_serial_set_torque(1)
        
        self.is_waving = False
        self.wave_thread = None
        
        # Listen for commands from the games
        rospy.Subscriber('/rga_arm_command', String, self.command_callback)
        rospy.Subscriber('/rga_arm_ik_trajectory', String, self.ik_trajectory_callback)
        self.waypoint_pub = rospy.Publisher('/scan_waypoint', Int32, queue_size=10)
        self.status_pub = rospy.Publisher('/rga_arm_status', String, queue_size=10)
        # Latched so a late-joining vision node still sees the current state.
        # Keeps the camera fully released between scans — biggest USB win.
        self.camera_enable_pub = rospy.Publisher(
            '/vision_camera_enable', Bool, queue_size=10)
        self.camera_enable_pub.publish(False)
        
        rospy.loginfo("[ARM CONTROLLER] Online and ready.")
        
    @staticmethod
    def _smooth_trajectory(frames):
        """Two-pass 1:2:1 weighted blur on joints 1-5.

        A single IK branch-switch can produce a waypoint that is 50-100 PWM
        units away from its neighbours.  One pass of this kernel halves the
        spike; two passes reduce it to ~6 % of the original — invisible on
        the servo.  Joint 6 (marker lock at 2892) is left untouched.
        """
        for _ in range(2):
            n = len(frames)
            if n < 3:
                break
            blurred = []
            for i in range(n):
                p = frames[max(0, i - 1)]
                c = frames[i]
                q = frames[min(n - 1, i + 1)]
                blurred.append(
                    [(p[j] + 2 * c[j] + q[j]) // 4 for j in range(5)] + [c[5]]
                )
            frames = blurred
        return frames

    def ik_trajectory_callback(self, msg):
        rospy.loginfo("[ARM CONTROLLER] Received IK Trajectory. Executing...")

        # ── 1. Parse ────────────────────────────────────────────────────
        frames = []
        for frame_str in msg.data.split('|'):
            if not frame_str.strip():
                continue
            try:
                frames.append([int(v) for v in frame_str.split()])
            except Exception as e:
                rospy.logerr(f"[ARM CONTROLLER] Bad IK frame: {e}")

        if not frames:
            self.status_pub.publish("done")
            return

        # ── 2. Smooth ───────────────────────────────────────────────────
        # Remove any IK discontinuity spikes before they reach the servos.
        frames = self._smooth_trajectory(frames)

        # ── 3. Execute ──────────────────────────────────────────────────
        # 60 ms transition keeps motion fast and fluid; sleep 55 ms so the
        # command stream stays just ahead of the servo without overrunning it.
        for pwm_array in frames:
            self.arm.bus_servo_control_array6(pwm_array, 60)
            time.sleep(0.055)

        rospy.loginfo("[ARM CONTROLLER] IK Trajectory Complete.")
        self.status_pub.publish("done")

    def command_callback(self, msg):
        command = msg.data.split(',')
        action = command[0]

        if action != "wave":
            self.stop_waving()
        if action == "reset":
            self.reset_arm()
        elif action == "scan":
            self.execute_board_scan()
        elif action == "scan_hangman":
            self.execute_hangman_scan()
        elif action == "draw":
            filename = command[1]
            self.draw_shape(filename)
        elif action == "wave":
            self.start_waving()
        elif action == "sleep":
            self.sleep_arm()

    def reset_arm(self):
        rospy.loginfo("[ARM CONTROLLER] Returning to Baseline Posture...")

        self.arm.Arm_serial_servo_write6(90, 180, 0, 0, 90, 163, 1000) 
        
        time.sleep(1.2)
        self.status_pub.publish("done")

    def execute_hangman_scan(self):
        time.sleep(0.1)
        rospy.loginfo("[RGA SYSTEM] Moving to Hangman Scanning Zone...")

        # The PWM coordinates for the Hangman observation zone
        look_zone_pwm = [2062, 3262, 715, 1152, 1997, 2892]

        # Wake the camera and let MJPG warm up before staring.
        self.camera_enable_pub.publish(True)
        time.sleep(1.5)

        self.waypoint_pub.publish(-1) # Close Shutter

        # 1. Move to the zone
        self.arm.bus_servo_control_array6(look_zone_pwm, 1000)
        time.sleep(1.2) # Allow for physical travel to settle

        # 2. OPEN Shutter (Waypoint '99' indicates the Hangman Zone)
        self.waypoint_pub.publish(99)

        # 3. Stare for 2.5 seconds to give YOLO plenty of time
        time.sleep(2.5)

        # 4. CLOSE Shutter and release the camera off the USB hub.
        self.waypoint_pub.publish(-1)
        self.camera_enable_pub.publish(False)

        rospy.loginfo("[RGA SYSTEM] Scan Complete. Returning to baseline.")
        self.reset_arm() # Automatically returns to the C++ Ready Posture and publishes "done"
        
    def execute_board_scan(self):
        time.sleep(0.1)
        print("[RGA SYSTEM] Initiating Raster Board Scan...")

        # Wake the camera. Vision opens the device and warms up MJPG/AE
        # in ~1.5 s; we sleep that long before the first cell so the
        # initial frames aren't underexposed garbage.
        self.camera_enable_pub.publish(True)
        time.sleep(1.5)

        scan_waypoints = {
        6: [2352, 3177, 701, 839, 1996, 2892], # Row 3: Bottom Left
        7: [1999, 3176, 692, 839, 1998, 2892], # Row 3: Bottom Middle
        8: [1702, 3176, 691, 840, 2000, 2892], # Row 3: Bottom Right
        
        5: [1714, 3262, 754, 887, 2000, 2892], # Row 2: Mid Right
        4: [2021, 3262, 754, 888, 1996, 2892], # Row 2: Mid Center
        3: [2353, 3263, 756, 888, 1996, 2892], # Row 2: Mid Left
        
        0: [2384, 3262, 747, 1083, 1996, 2892], # Row 1: Top Left
        1: [2062, 3262, 715, 1152, 1997, 2892], # Row 1: Top Middle
        2: [1723, 3262, 668, 1155, 2000, 2892]  # Row 1: Top Right
        }

        # The optimal 'Snake' pattern array
        snake_path = [6, 7, 8, 5, 4, 3, 0, 1, 2]

        for cell in snake_path:
            pwm_array = scan_waypoints[cell]

            # 1. Move to the cell while the vision shutter is CLOSED
            self.arm.bus_servo_control_array6(pwm_array, 400) 
            time.sleep(0.45) 

            # 2. Publishes to /scan_waypoint while we are in cell
            self.waypoint_pub.publish(cell)

            # 3. Let YOLO read the clean, still frames
            time.sleep(1.2) 

            # 4. CLOSE the shutter again before the next move to reduce overlapping scanning
            self.waypoint_pub.publish(-1)

        # Release the camera before any other USB activity. Vision will
        # close the V4L2 device on receipt — between scans the bus carries
        # only the ESP32 heartbeat and HID traffic.
        self.camera_enable_pub.publish(False)

        print("[RGA SYSTEM] Scan Complete. Returning to baseline.")
        self.reset_arm()
        time.sleep(0.2)
        self.status_pub.publish("done")

    def draw_shape(self, filename, offset_j1=0, offset_j2=0):
        """
        Reads a kinesthetically taught shape file and draws it.
        Applies dynamic offsets to Joints 1 & 2 to place the shape anywhere on the board.
        
        """
        if not os.path.exists(filename):
            print(f"ERROR: Trajectory file '{filename}' not found.")
            return

        raw_frames = []

        # Load the file joint angles into a buffer
        with open(filename, 'r') as file:
            try:
                for line in file:
                    data = line.strip().split()
                    if len(data) == 6:
                        # Apply the dynamic offset so the arm draws in the correct grid location
                        j1 = int(data[1]) + offset_j1
                        j2 = int(data[2]) + offset_j2

                        # 2892 is the exact PWM pulse for 163 degrees (Marker Locked)
                        raw_frames.append([j1, j2, int(data[3]), int(data[4]), int(data[5]), 2892])   
            except Exception as e:
                print(f"Error reading file: {e}")
                return

        # Execute the joint angles
        print(f"Drawing {filename} with offsets (J1:{offset_j1}, J2:{offset_j2})...")
        for frame in raw_frames:
            self.arm.bus_servo_control_array6(frame, 200)
            # Sleep slightly less than the command time to keep motion fluid
            time.sleep(0.05)

        print("Drawing Complete!")
        self.status_pub.publish("done")
        
    def start_waving(self):
        """ Starts the infinite wave in a background thread """
        if not self.is_waving:
            self.is_waving = True
            self.wave_thread = threading.Thread(target=self.wave_loop)
            self.wave_thread.start()
            
    def stop_waving(self):
        """Safely kills the wave thread before moving to the next command"""
        if self.is_waving:
            rospy.loginfo("[ARM CONTROLLER] Thank you for playing!")
            self.is_waving = False
            if self.wave_thread is not None:
                self.wave_thread.join() # Wait for arm to finish current swing

    def wave_loop(self):
        """The infinite loop that runs in the background."""
        rospy.loginfo("[ARM CONTROLLER] Waving continuously...")
        
        # 1. Stand up tall ONCE
        self.arm.Arm_serial_servo_write6(90, 180, 90, 90, 90, 163, 1000)
        time.sleep(1.0)
        
        # 2. Infinite Waving Loop
        while self.is_waving and not rospy.is_shutdown():
            self.arm.Arm_serial_servo_write(5, 130, 400) # Wrist Left
            self.breakable_sleep(0.4) 
            
            if not self.is_waving: break # Safety check mid-wave
            
            self.arm.Arm_serial_servo_write(5, 50, 400) # Wrist Right
            self.breakable_sleep(0.4)
            
    def breakable_sleep(self, duration):
        """ Allows time.sleep to be instantly interrupted by Kivy button."""
        # ---> BUG 5 FIXED: Divide by 0.05, not 0.5
        steps = int(duration / 0.05) 
        for _ in range(steps):
            if not self.is_waving:
                break
            time.sleep(0.05)
        
    def sleep_arm(self):
        rospy.loginfo("[ARM CONTROLLER] Folding into sleep position...")
        self.arm.Arm_serial_servo_write6(90, 180, 0, 0, 90, 163, 1500)
        time.sleep(0.5)

if __name__ == '__main__':
    controller = ArmController()
    controller.reset_arm()
    rospy.spin() # Keep the script alive forever