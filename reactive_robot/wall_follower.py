import rclpy
import numpy as np
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from rclpy.qos import qos_profile_sensor_data # <--- Brought this back!
import math
import time 



class WallFollower(Node):
    def detect_circle(self, ranges, angles):
        wall_threshold = 5.0  # big enough to capture the full belly

        wall_x = []
        wall_y = []

        for i, r in enumerate(ranges):
            if r < wall_threshold:
                wall_x.append(r * math.cos(angles[i]))
                wall_y.append(r * math.sin(angles[i]))

        # Need enough wall points for a meaningful fit, but not too many
        # (too many = we're in a corridor, not a belly)
        wall_ratio = len(wall_x) / len(ranges)
        if wall_ratio < 0.3 or wall_ratio > 0.85:
            return False, 0.0, 0.0

        # --- Least-squares circle fit ---
        # Finds center (a, b) and radius R that best fits the wall points
        wall_x = np.array(wall_x)
        wall_y = np.array(wall_y)

        # Build the system:  x^2 + y^2 = 2*a*x + 2*b*y + (R^2 - a^2 - b^2)
        A = np.column_stack([2 * wall_x, 2 * wall_y, np.ones(len(wall_x))])
        b_vec = wall_x**2 + wall_y**2
        result, residuals, _, _ = np.linalg.lstsq(A, b_vec, rcond=None)

        cx = result[0]  # center x relative to robot
        cy = result[1]  # center y relative to robot
        R = math.sqrt(result[2] + cx**2 + cy**2)

        # --- Validate the fit ---
        # Check how well points actually lie on the fitted circle
        distances_to_circle = np.sqrt((wall_x - cx)**2 + (wall_y - cy)**2)
        fit_error = np.std(distances_to_circle - R)

        # Check the arc span: what angular range of the circle do wall points cover?
        point_angles = np.arctan2(wall_y - cy, wall_x - cx)
        angle_range = np.ptp(point_angles)  # peak-to-peak angular span

        self.get_logger().info(
            f"CIRCLE_CHECK: R={R:.2f} fit_err={fit_error:.2f} arc={math.degrees(angle_range):.0f}deg")

        # It's a circle if:
        # - Radius is reasonable (not a tiny bump or a huge open space)
        # - Points actually lie on the fitted circle (low fit error)
        # - Arc spans at least 120 degrees (not just a slightly curved wall)
        if R < 0.5 or R > 4.0:
            return False, 0.0, 0.0
        if fit_error > 0.2:
            return False, 0.0, 0.0
        if angle_range < math.radians(120):
            return False, 0.0, 0.0
        dist_to_center = math.sqrt(cx**2 + cy**2)
        if dist_to_center > R:
            return False, 0.0, 0.0
        return True, cx, cy

    def __init__(self):
        super().__init__('wall_follower')
        
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Uses the correct QoS profile so Gazebo doesn't ignore it
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            qos_profile_sensor_data)

        self.desired_distance = 0.5
        self.kp = 6.0
        self.ki = 0.0
        self.kd = 4.0
        
        self.prev_error = 0.0
        self.integral = 0.0
        self.prev_time = time.time()    

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

        now = time.time()
        dt = now - self.prev_time
        self.prev_time = now
        if dt <= 0.0:
            dt = 0.001

        cmd = Twist()
        angles = [msg.angle_min + i * msg.angle_increment for i in range(len(ranges))]
        is_circle, cx, cy = self.detect_circle(ranges, angles)

        if is_circle:
            dist_to_center = math.sqrt(cx**2 + cy**2)
            angle_to_center = math.atan2(cy, cx)
            
            if dist_to_center < 0.1:
                # We're at the center, stop
                cmd.linear.x = 0.0
                cmd.angular.z = 0.0
            else:
                # Drive toward centroid
                cmd.linear.x = min(0.15, dist_to_center)
                cmd.angular.z = 0.5 * angle_to_center
        
        # Safety override: obstacle dead ahead
        elif front < 0.5:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.6
            self.integral = 0.0
            self.prev_error = 0.0

        elif right > 1.5:
            # --- Wall-seeking mode: no wall nearby on the right ---
            self.integral = 0.0
            self.prev_error = 0.0

            min_dist = min(ranges)
            if min_dist >= 9.9:
                # Totally blind — spin to sweep
                cmd.linear.x = 0.5
                cmd.angular.z = 0.5
            else:
                closest_idx = ranges.index(min_dist)
                if 150 <= closest_idx <= 210:
                    # Wall is ahead — drive toward it
                    cmd.linear.x = 0.3
                    cmd.angular.z = 0.0
                elif closest_idx < 180:
                    # Wall is to the right — spin right
                    cmd.linear.x = 0.0
                    cmd.angular.z = -0.5
                else:
                    # Wall is to the left — spin left
                    cmd.linear.x = 0.0
                    cmd.angular.z = 0.5

        else:
            # --- PID computation ---
            error = self.desired_distance - right  # positive = too close

            self.integral += error * dt
            # Anti-windup clamp
            self.integral = max(-1.0, min(1.0, self.integral))

            derivative = (error - self.prev_error) / dt
            self.prev_error = error

            angular_z = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)

            # Clamp output
            angular_z = max(-1.5, min(1.5, angular_z))

            # Slow down in proportion to how hard we're turning
            cmd.linear.x = max(0.05, 0.25 - 0.1 * abs(angular_z))
            cmd.angular.z = angular_z

        self.publisher_.publish(cmd)
        self.get_logger().info(
            f"R: {right:.2f} | err: {self.desired_distance - right:.2f} | ang_z: {cmd.angular.z:.2f}")

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