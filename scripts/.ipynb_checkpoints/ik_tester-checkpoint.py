#!/usr/bin/env python3
import rospy
from std_msgs.msg import String

def run_tester():
    rospy.init_node('ik_manual_tester', anonymous=True)
    pub = rospy.Publisher('/rga_ik_command', String, queue_size=10)
    
    # Wait a second for the ROS network to connect the publisher
    rospy.sleep(1)

    print("\n=========================================")
    print(" RGA MANUAL IK TESTER ")
    print(" Coordinate System (Meters):")
    print(" X: Width (Negative = Left, Positive = Right)")
    print(" Y: Depth (Distance outward from wall)")
    print(" Z: Handled automatically by State")
    print("=========================================\n")

    while not rospy.is_shutdown():
        try:
            print("\n--- Enter New Trajectory (Ctrl+C to quit) ---")
            start_x = input("Start X (m) [e.g., 0.0]: ")
            start_y = input("Start Y (m) [e.g., 0.10]: ")
            end_x   = input("End X (m)   [e.g., 0.10]: ")
            end_y   = input("End Y (m)   [e.g., 0.15]: ")
            state   = input("State (1=Draw, 0=Hover): ")

            # Construct the exact string the C++ node expects
            command = f"LINE,{start_x},{start_y},{end_x},{end_y},{state}"
            
            print(f"\n[TESTER] Firing command: {command}")
            pub.publish(command)
            
            # Brief pause to let the C++ node catch the message
            rospy.sleep(0.5)

        except ValueError:
            print("[ERROR] Invalid input. Please enter numbers only.")
        except KeyboardInterrupt:
            print("\n[TESTER] Shutting down.")
            break
        except rospy.ROSInterruptException:
            break

if __name__ == '__main__':
    run_tester()