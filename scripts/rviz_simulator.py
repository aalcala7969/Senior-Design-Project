#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import JointState
import math
import time

class DigitalTwin:
    def __init__(self):
        rospy.init_node('rviz_simulator', anonymous=True)
        
        # Publisher to animate RViz
        self.joint_pub = rospy.Publisher('/joint_states', JointState, queue_size=10)
        
        # Listen to the C++ Engine's math output
        rospy.Subscriber('/rga_arm_ik_trajectory', String, self.trajectory_callback)
        
        # Store current joint positions (Initialize at default 'Stand Up' pose)
        self.current_positions = [
            1.5708,
            0.785,
            -0.785,
            -0.785,
            0.0
        ]

        rospy.loginfo("[DIGITAL TWIN] Online. Holding position...")

        # THE FIX: A 10Hz heartbeat timer to constantly broadcast the joint state
        rospy.Timer(rospy.Duration(0.1), self.publish_current_state)

    def pwm_to_rad(self, pwm):
        """ Reverses the C++ math: PWM -> Degrees -> Radians """
        degrees = (pwm - 2048) / 15.17
        return degrees * (math.pi / 180.0)

    def publish_current_state(self, event=None):
        """ Broadcasts the current angles to RViz to prevent crumbling """
        js = JointState()
        js.header.stamp = rospy.Time.now()
        js.name = ['joint1', 'joint2', 'joint3', 'joint4', 'joint5']
        js.position = self.current_positions
        self.joint_pub.publish(js)

    def trajectory_callback(self, msg):
        """ Catch IK math, update internal positions, and simulate movement delay """
        raw_frames = msg.data.split('|')
        
        for frame_str in raw_frames:
            if not frame_str.strip(): 
                continue
            
            try:
                pwm_array = [int(val) for val in frame_str.split()]
                
                # Update the robot's active memory with the new frame
                self.current_positions = [
                    self.pwm_to_rad(pwm_array[0]),
                    self.pwm_to_rad(pwm_array[1]),
                    self.pwm_to_rad(pwm_array[2]),
                    self.pwm_to_rad(pwm_array[3]),
                    self.pwm_to_rad(pwm_array[4])
                ]
                
                # Simulate the physical 50ms servo transition delay
                time.sleep(0.05) 
                
            except Exception as e:
                pass

if __name__ == '__main__':
    DigitalTwin()
    rospy.spin()
