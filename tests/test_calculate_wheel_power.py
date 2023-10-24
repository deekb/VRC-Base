from unittest import TestCase
import math
import sys
import os

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"
)

sys.path.append(src_dir)

from Utilities import calculate_wheel_power


class TestCalculateWheelPower(TestCase):
    def test_wheel_power_equal_angles(self):
        # Test when wheel_angle_rad is equal to movement_angle_rad
        result = calculate_wheel_power(math.radians(0), 1.0, math.radians(0))
        self.assertAlmostEqual(result, 1.0)
        result = calculate_wheel_power(math.radians(45), 1.0, math.radians(45))
        self.assertAlmostEqual(result, 1.0)
        result = calculate_wheel_power(math.radians(90), 1.0, math.radians(90))
        self.assertAlmostEqual(result, 1.0)
        result = calculate_wheel_power(math.radians(180), 1.0, math.radians(180))
        self.assertAlmostEqual(result, 1.0)

    def test_wheel_power_opposite_angles(self):
        # Test when wheel_angle_rad is opposite of movement_angle_rad
        result = calculate_wheel_power(math.radians(0), 1.0, math.radians(180))
        self.assertAlmostEqual(result, -1.0)
        result = calculate_wheel_power(math.radians(45), 1.0, math.radians(225))
        self.assertAlmostEqual(result, -1.0)
        result = calculate_wheel_power(math.radians(90), 1.0, math.radians(270))
        self.assertAlmostEqual(result, -1.0)

    def test_wheel_power_45_degrees_offset(self):
        # Test when wheel_angle_rad is 45 degrees off from movement_angle_rad
        result = calculate_wheel_power(math.radians(0), 1.0, math.radians(45))
        self.assertAlmostEqual(result, math.sqrt(2) / 2)
        result = calculate_wheel_power(math.radians(45), 1.0, math.radians(90))
        self.assertAlmostEqual(result, math.sqrt(2) / 2)
        result = calculate_wheel_power(math.radians(90), 1.0, math.radians(135))
        self.assertAlmostEqual(result, math.sqrt(2) / 2)
        result = calculate_wheel_power(math.radians(135), 1.0, math.radians(180))
        self.assertAlmostEqual(result, math.sqrt(2) / 2)

    def test_wheel_power_90_degrees_offset(self):
        # Test when wheel_angle_rad is 90 degrees off from movement_angle_rad
        result = calculate_wheel_power(math.radians(0), 1.0, math.radians(90))
        self.assertAlmostEqual(result, 0.0)
        result = calculate_wheel_power(math.radians(90), 1.0, math.radians(180))
        self.assertAlmostEqual(result, 0.0)
        result = calculate_wheel_power(math.radians(180), 1.0, math.radians(270))
        self.assertAlmostEqual(result, 0.0)

    def test_negative_movement_speed(self):
        # Test with negative movement_speed, should raise a ValueError
        self.assertRaises(ValueError, calculate_wheel_power, math.radians(0), -1.0, math.radians(0))
        self.assertRaises(ValueError, calculate_wheel_power, math.radians(45), -1.0, math.radians(45))
        self.assertRaises(ValueError, calculate_wheel_power, math.radians(90), -1.0, math.radians(90))
        self.assertRaises(ValueError, calculate_wheel_power, math.radians(180), -1.0, math.radians(180))
