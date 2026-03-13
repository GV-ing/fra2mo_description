#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist

class JoyToCmdVel(Node):
    def __init__(self):
        super().__init__('joy_to_cmdvel')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.subscription = self.create_subscription(
            Joy,
            'joy',
            self.joy_callback,
            10)
        self.subscription  
        self.linear_axis = 1  
        self.angular_axis = 0  
        self.linear_scale = 1.0
        self.angular_scale = 1.0

    def joy_callback(self, msg):
        twist = Twist()
        if len(msg.axes) > max(self.linear_axis, self.angular_axis):
            twist.linear.x = msg.axes[self.linear_axis] * self.linear_scale
            twist.angular.z = msg.axes[self.angular_axis] * self.angular_scale
        self.publisher_.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = JoyToCmdVel()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
