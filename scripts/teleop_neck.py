#!/usr/bin/env python3
"""
Implements 2-axis active neck control via teleoperation using keyboard.

Author(s):
    Divam Trivedi <dtrivedi@wpi.edu>

Affiliation:
    Human-Inspired Robotics (HiRo) Lab
    Worcester Polytechnic Institute (WPI)

Year:
    2026
"""

import rospy
import sys
import termios
import tty
import select
from std_msgs.msg import Float64

PITCH_TOPIC = "/active_neck/pitch_velocity_fraction"
YAW_TOPIC   = "/active_neck/yaw_velocity_fraction"

VELOCITY = 0.04   # change this to go faster/slower

from geometry_msgs.msg import PoseStamped

def headset_pose_callback(msg):
    pos = msg.pose.position
    ori = msg.pose.orientation
    print(f"Headset Pose -> Position: ({pos.x:.2f}, {pos.y:.2f}, {pos.z:.2f}), "
          f"Orientation: ({ori.x:.2f}, {ori.y:.2f}, {ori.z:.2f}, {ori.w:.2f})")

def get_key(timeout=0.1):
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return key

def stop(pub_pitch, pub_yaw):
    pub_pitch.publish(Float64(0.0))
    pub_yaw.publish(Float64(0.0))

def main():
    rospy.init_node("neck_teleop_keyboard")
    rospy.Subscriber("/headset_feedback/pose", PoseStamped, headset_pose_callback)
    pub_pitch = rospy.Publisher(PITCH_TOPIC, Float64, queue_size=1)
    pub_yaw   = rospy.Publisher(YAW_TOPIC, Float64, queue_size=1)

    rospy.sleep(0.5)

    print("""
            W/S : Pitch up/down
            A/D : Yaw left/right
            SPACE : Stop
            Q : Quit
            """)
    rate = rospy.Rate(200)
    try:
        while not rospy.is_shutdown():
            key = get_key()

            if key is None:
                rate.sleep()
                continue

            pitch = 0.0
            yaw = 0.0

            if key == 'w':
                pitch = +VELOCITY
            elif key == 's':
                pitch = -VELOCITY
            elif key == 'a':
                yaw = +VELOCITY
            elif key == 'd':
                yaw = -VELOCITY
            elif key == ' ':
                stop(pub_pitch, pub_yaw)
                continue
            elif key == 'q':
                break

            pub_pitch.publish(Float64(pitch))
            pub_yaw.publish(Float64(yaw))

            rate.sleep()

    finally:
        stop(pub_pitch, pub_yaw)
        print("\nTeleop stopped.")

if __name__ == "__main__":
    main()

