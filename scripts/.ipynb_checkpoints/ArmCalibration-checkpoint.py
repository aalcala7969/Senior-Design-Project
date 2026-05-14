#!/usr/bin/env python3
#coding=utf-8

import time
from Arm_Lib import Arm_Device

# PWM Pulses:
# 0 degrees = 900
# 90 degrees = 2200
# 180 degrees = 3100
# 163 degrees = 2892

def reset_arm(arm):
    # We still use degrees here for a simple, safe reset
    arm.Arm_serial_set_torque(1)
    time.sleep(3)
    arm.Arm_serial_servo_write6(90, 180, 0, 0, 90, 163, 500)
    time.sleep(1)

def calibration_mode(arm):
    time.sleep(0.1)
    
    print("=======================================")
    print("         CALIBRATION MODE ")
    print("=======================================")
    print("1. The motors are currently ON.")
    print("2. Turning the servo torque OFF in 3 seconds...") 
    
    # Turn off the torque globally for all servos
    arm.Arm_serial_set_torque(0)
    time.sleep(0.1)
    
    print("\nTorque OFF! You can now move the arm freely.")
    print("Move the marker to a Tic-Tac-Toe square.")
    
    with open('output.txt', 'w') as file:
        try:
            # Fallback values changed to roughly 90 degrees in raw pulses
            prev_angles = [0, 2200, 3100, 3100, 900, 2200] 
            while True:
                angles = [0]
                # Read the physical high-resolution raw pulses of all 5 joints
                for i in range(1, 6):
                    pulse = arm.bus_servo_read(i)
                    if pulse is None:
                        pulse = prev_angles[i] # Fallback if I2C drops a frame
                    angles.append(pulse)

                print(f"[{angles[0]}, {angles[1]}, {angles[2]}, {angles[3]}, {angles[4]}, {angles[5]}]")
                file.write(f"{angles[0]} {angles[1]} {angles[2]} {angles[3]} {angles[4]} {angles[5]}\n")
                
                prev_angles = angles
                
                # Lock the recording sampling rate to exactly 150ms
                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("\n\nCalibration stopped.")
        
if __name__ == '__main__':
    arm = Arm_Device()
    reset_arm(arm)
    calibration_mode(arm)