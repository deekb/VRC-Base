import sys
import os

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"
)
print(f"Source Directory is: {src_dir}")

sys.path.append(src_dir)

from unittest import TestCase
from LinearRegressor import LinearRegressor
import math


class TestLinearRegressor(TestCase):
    def test_pass_bad_values(self):
        self.assertRaisesRegex(
            ValueError,
            "The number of unique data points must be greater than 1.",
            LinearRegressor().smart_fit,
            [],
        )
        self.assertRaisesRegex(
            ValueError,
            "The number of unique data points must be greater than 1.",
            LinearRegressor().smart_fit,
            [(0, 0)],
        )
        self.assertRaisesRegex(
            ValueError,
            "The number of unique data points must be greater than 1.",
            LinearRegressor().smart_fit,
            [(0, 0), (0, 0)],
        )
        self.assertRaisesRegex(
            ValueError,
            "The number of unique data points must be greater than 1.",
            LinearRegressor().smart_fit,
            [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
        )
        self.assertRaisesRegex(
            ValueError,
            "The number of unique data points must be greater than 1.",
            LinearRegressor().smart_fit,
            [(5, 10), (5, 10)],
        )

    def test_horizontal_smart_fit(self):
        linear_regressor = LinearRegressor().smart_fit([(0.0, 0.0), (1.0, 0.0)])
        self.assertEqual(linear_regressor.slope, 0.0)
        self.assertEqual(linear_regressor.y_intercept, 0.0)
        self.assertEqual(linear_regressor.x_intercept, 0.0)

        linear_regressor = LinearRegressor().smart_fit([(0.0, 5.0), (1.0, 5.0)])
        self.assertEqual(linear_regressor.slope, 0.0)
        self.assertEqual(linear_regressor.y_intercept, 5.0)
        self.assertIsNone(linear_regressor.x_intercept)

    def test_imperfect_horizontal_smart_fit(self):
        linear_regressor = LinearRegressor().smart_fit(
            [
                (-1, -1),
                (
                    1,
                    1,
                ),
                (1, -1),
                (-1, 1),
            ]
        )
        self.assertIn(linear_regressor.slope, (0, math.inf))
        self.assertEqual(linear_regressor.y_intercept, 0.0)
        self.assertEqual(linear_regressor.x_intercept, 0.0)

    def test_vertical_smart_fit(self):
        linear_regressor = LinearRegressor().smart_fit([(0.0, 0.0), (0.0, 1.0)])
        self.assertEqual(linear_regressor.slope, math.inf)
        self.assertEqual(linear_regressor.y_intercept, 0.0)
        self.assertEqual(linear_regressor.x_intercept, 0.0)

        linear_regressor = LinearRegressor().smart_fit([(5.0, 0.0), (5.0, 1.0)])
        self.assertEqual(linear_regressor.slope, math.inf)
        self.assertIsNone(linear_regressor.y_intercept)
        self.assertEqual(linear_regressor.x_intercept, 5.0)

    def test_slope_of_1_smart_fit(self):
        linear_regressor = LinearRegressor().smart_fit([(0.0, 0.0), (1.0, 1.0)])
        self.assertEqual(linear_regressor.slope, 1.0)
        self.assertEqual(linear_regressor.y_intercept, 0.0)
        self.assertEqual(linear_regressor.x_intercept, 0.0)

        linear_regressor = LinearRegressor().smart_fit(
            [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0), (3.0, 3.0)]
        )
        self.assertEqual(linear_regressor.slope, 1.0)
        self.assertEqual(linear_regressor.y_intercept, 0.0)
        self.assertEqual(linear_regressor.x_intercept, 0.0)
