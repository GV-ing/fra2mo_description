#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist


class JoyToCmdVel(Node):
    # This node subscribes to joystick inputs 
    # and publishes velocity commands to control the robot in Gazebo Harmonic.
    def __init__(self):
        super().__init__('joy_to_cmdvel')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.subscription = self.create_subscription(
            Joy,
            'joy',
            self.joy_callback,
            10)
        self.subscription  
        #The following parameters define which axes of the joystick
        # control linear and angular velocity, and their respective scales.
        self.linear_axis = 1  
        self.angular_axis = 2
        self.linear_scale = 0.7
        self.angular_scale = 0.7
        self.deadzone = 1e-3

    def joy_callback(self, msg):
        if len(msg.axes) <= max(self.linear_axis, self.angular_axis):
            return

        linear_cmd = msg.axes[self.linear_axis] * self.linear_scale
        angular_cmd = msg.axes[self.angular_axis] * self.angular_scale

        if abs(linear_cmd) <= self.deadzone and abs(angular_cmd) <= self.deadzone:
            return

        twist = Twist()
        twist.linear.x = linear_cmd
        twist.angular.z = angular_cmd
        self.publisher_.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = JoyToCmdVel()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
