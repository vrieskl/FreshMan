import unittest
from TemperatureAverage import TemperatureAverage


class TestTemperatureAverage(unittest.TestCase):

    def test_0(self):
        temp_avg = TemperatureAverage(0)
        self.assertEqual(temp_avg.add_get(20), 20)
        self.assertEqual(temp_avg.add_get(80), 80)

    def test_1(self):
        temp_avg = TemperatureAverage(1)
        self.assertEqual(temp_avg.add_get(20), 20)
        self.assertEqual(temp_avg.add_get(30), 30)

    def test_4(self):
        temp_avg = TemperatureAverage(4)
        self.assertEqual(temp_avg.add_get(20), 20)
        self.assertEqual(temp_avg.add_get(30), 25)
        self.assertEqual(temp_avg.add_get(40), 30)
        self.assertEqual(temp_avg.add_get(10), 25)
        self.assertEqual(temp_avg.add_get(80), 40)
        self.assertEqual(temp_avg.add_get(10), 35)

    def test_float(self):
        temp_avg = TemperatureAverage(3)
        self.assertEqual(temp_avg.add_get(3.25), 3.25)
        self.assertEqual(temp_avg.add_get(7.77), 11.02 / 2)
        self.assertEqual(temp_avg.add_get(6.54), 17.56 / 3)
        self.assertEqual(temp_avg.add_get(3.33), (7.77 + 6.54 + 3.33) / 3)

    def test_much(self):
        temp_avg = TemperatureAverage(3)
        for looper in range(0, 1000):
            for counter in range(0, 2000):
                temp_avg.add_get(counter + 0.132)
        self.assertEqual(temp_avg.add_get(2000.132), (5997.396 / 3))


if __name__ == '__main__':
    unittest.main()