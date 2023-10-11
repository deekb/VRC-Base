from unittest import TestCase
import sys
import os

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"
)

sys.path.append(src_dir)

from Utilities import apply_deadzone


class TestApplyDeadzone(TestCase):
    def test_apply_deadzone_zero(self):
        for i in range(-100, 100):
            self.assertAlmostEqual(
                apply_deadzone(i / 100, 0, 1), i / 100
            )  # Applying a deadzone of zero should return the input
