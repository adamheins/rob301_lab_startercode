#!/usr/bin/env python
import rospy
from std_msgs.msg import UInt32
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
import numpy as np


class CameraMono(object):
    def __init__(self):
        self.line_idx_pub = rospy.Publisher("line_idx", UInt32, queue_size=1)
        self.camera_subscriber = rospy.Subscriber(
            "raspicam_node/image", Image, self.camera_callback, queue_size=1
        )
        self.bridge = CvBridge()

    def camera_callback(self, data):
        try:
            cv_img = self.bridge.imgmsg_to_cv2(data, "mono8")
        except CvBridgeError as e:
            print(e)

        # average each column (removing some rows): result is a 640 length array
        array = np.mean(cv_img[100:300, :], axis=0)

        # moving window filter
        # TODO can we optimize this?
        new_array = []
        for i in range(5, len(array) - 6):
            new_array.append(np.mean(array[i - 5 : i + 5]))
        index = np.argmax(new_array)

        self.line_idx_pub.publish(index)


def main():
    rospy.init_node("camera_mono")
    camera = CameraMono()
    rospy.spin()


if __name__ == "__main__":
    main()