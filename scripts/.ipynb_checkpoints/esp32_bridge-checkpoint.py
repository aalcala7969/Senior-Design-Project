#!/usr/bin/env python3

import rospy
import serial
import time
from std_msgs.msg import Int32

def esp32_to_ros():
    #initializing the ROS node
    rospy.init_node('esp32_serial_bridge', anonymous=True) 
    #define the publisher
    pub = rospy.Publisher('/game_state', Int32, queue_size=10)
    
    # Serial config must match esp32.ino Serial.begin(115200).
    # Old 9600 setting silently corrupted reads — they only "worked" because
    # reset_input_buffer() flushed the bad data before each readline().
    serial_port = '/dev/ttyUSB0'
    baud_rate = 115200

    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=1)
        # give the ESP32 a moment to reset after connection
        time.sleep(2)
        rospy.loginfo(f"Connected to ESP32 on {serial_port} @ {baud_rate}")
    except Exception as e:
        rospy.logerr(f"Failed to connect to ESP32: {e}")
        return

    last_state = None
    while not rospy.is_shutdown():
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line.isdigit():
                game_state = int(line)
                # ESP32 now sends on change + 1 Hz heartbeat, but re-publishing
                # the same value every second is harmless and keeps subscribers
                # confident the link is alive.
                pub.publish(game_state)
                if game_state != last_state:
                    rospy.loginfo(f"game_state -> {game_state}")
                    last_state = game_state
        except Exception as e:
            rospy.logwarn(f"Serial read error: {e}")

if __name__ == '__main__':
    try:
        esp32_to_ros()
    except rospy.ROSInterruptException:
        pass
    