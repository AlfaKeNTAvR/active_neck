#!/usr/bin/env python3

import rospy
import math
from std_msgs.msg import Float64
from geometry_msgs.msg import PoseStamped

pitch = 0.0
yaw = 0.0

L = 0.2  # distance from base to camera (meters)

def pitch_cb(msg):
    global pitch
    pitch = msg.data

def yaw_cb(msg):
    global yaw
    yaw = msg.data

def main():
    rospy.init_node("camera_pose_publisher")

    rospy.Subscriber("/active_neck/pitch_angle", Float64, pitch_cb)
    rospy.Subscriber("/active_neck/yaw_angle", Float64, yaw_cb)

    pub = rospy.Publisher("/camera_pose", PoseStamped, queue_size=10)

    rate = rospy.Rate(50)

    while not rospy.is_shutdown():
        pose = PoseStamped()

        # Simple forward kinematics
        pose.pose.position.x = L * math.cos(pitch) * math.cos(yaw)
        pose.pose.position.y = L * math.cos(pitch) * math.sin(yaw)
        pose.pose.position.z = L * math.sin(pitch)

        pub.publish(pose)
        rate.sleep()

if __name__ == "__main__":
    main()