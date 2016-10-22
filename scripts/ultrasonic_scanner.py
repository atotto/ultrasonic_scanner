#!/usr/bin/env python

import rospy
import serial
from sensor_msgs.msg import LaserScan

class UltrasonicScanner():
    def __init__(self):
        rospy.init_node('laser_scan_publisher')

        self.scan_pub = rospy.Publisher('scan', LaserScan, queue_size=50)
        self.num_readings = 90

        self.rate = 1.0

        self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        self.direction = 1.0

    def handleScanner(self):

        scan = LaserScan()
        scan.header.stamp = self.current_time

        self.ser.write("0")
        line = self.ser.readline()
        if len(line) <= 3:
            return
        direction = line[0:2]
        if direction == '+:':
            self.direction = 1.0
        elif direction == '-:':
            self.direction = -1.0
        else:
            return

        rospy.logdebug(line)

        scan.header.frame_id = 'laser_frame'
        scan.angle_min = -1.57 * self.direction
        scan.angle_max = 1.57 * self.direction
        scan.angle_increment = 3.14 / self.num_readings * self.direction
        scan.time_increment = 0.003012 * self.num_readings
        scan.range_min = 0.02  # [m]
        scan.range_max = 4.00  # [m]

        scan.ranges = map(lambda n:1.0*int(n)/1000, line[2:].split(','))

        self.scan_pub.publish(scan)

    def spin(self):
        r = rospy.Rate(self.rate)
        while not rospy.is_shutdown():
            self.current_time = rospy.Time.now()
            self.handleScanner()
            r.sleep()

if __name__ == '__main__':
    scanner = UltrasonicScanner()
    rospy.loginfo("=== run")
    scanner.spin()
    rospy.loginfo("=== end")
