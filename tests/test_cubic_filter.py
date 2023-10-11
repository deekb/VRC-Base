import os
import sys
from unittest import TestCase

src_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"
)

sys.path.append(src_dir)

from Utilities import cubic_filter


class TestCubicFilter(TestCase):
    def test_cubic_filter_zero(self):
        for i in range(0, 100):
            self.assertAlmostEqual(cubic_filter(0, i / 10), 0)

    def test_cubic_filter_one(self):
        for i in range(0, 100):
            self.assertAlmostEqual(cubic_filter(1, i / 10), 1)

    def test_cubic_filter_zero_linearity(self):
        # Test with linearity = 0, the result should be value cubed
        self.assertEqual(cubic_filter(1.0, 0.0), 1.0)

    def test_cubic_filter_negative_linearity(self):
        # Test with negative linearity
        self.assertRaises(ValueError, cubic_filter, -1.0, -0.2)
