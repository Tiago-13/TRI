import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from rclpy.qos import qos_profile_sensor_data # <--- Brought this back!
import math

class WallFollower(Node):
    def __init__(self):
        super().__init__('wall_follower')
        
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Uses the correct QoS profile so Gazebo doesn't ignore it
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            qos_profile_sensor_data)
            
        self.get_logger().info("Wall Follower Node has started! Looking for a wall...")

    def scan_callback(self, msg):
        ranges = [x if not math.isnan(x) and not math.isinf(x) and x > 0.15 else 10.0 for x in msg.ranges]
        
        # Make sure we have a full scan before calculating
        if len(ranges) < 360:
            return

        front = min(ranges[150:210])         # Dead ahead (60 degree cone)
        front_right = min(ranges[110:150])   # Angled right
        right = min(ranges[70:110])          # Directly right
        back_right = min(ranges[20:70])      # Looking behind its right shoulder!

        # print the robot's vision to the terminal
        self.get_logger().info(f"F: {front:.2f} | FR: {front_right:.2f} | R: {right:.2f} | BR: {back_right:.2f}")

        cmd = Twist()
        d = 0.5 
        
        if front < d:
            # imminent crash, turn hard left immediately
            cmd.linear.x = 0.0
            cmd.angular.z = 0.6 
            
        elif front_right < d:
            # getting too close to the front-right corner, veer left
            cmd.linear.x = 0.15
            cmd.angular.z = 0.4
            
        elif right < d - 0.1: 
            # scraping the right wall (under 0.4m), veer left
            cmd.linear.x = 0.15
            cmd.angular.z = 0.3
            
        elif right > d + 0.1 and right < 1.0:
            # perfect following range, but drifting slightly away, steer right
            cmd.linear.x = 0.15
            cmd.angular.z = -0.3
            
        elif right >= 1.0 and back_right < 1.5:
            # outside corner, right is empty, but we see the wall behind us
            # just passed the edge, took a sharp right to wrap around the belly
            cmd.linear.x = 0.1
            cmd.angular.z = -0.6
            
        else:
            # open, front is clear, right is empty, back is empty.
            # drive straight ahead to find the wall
            cmd.linear.x = 0.3
            cmd.angular.z = 0.0

        self.publisher_.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    wall_follower = WallFollower()
    try:
        rclpy.spin(wall_follower)
    except KeyboardInterrupt:
        pass
    wall_follower.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()