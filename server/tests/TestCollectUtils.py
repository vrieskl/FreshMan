import unittest
from server.classes.CollectUtils import DeltaDetect, Helpers


class TestDeltaDetect(unittest.TestCase):

    def test_delta_detect_float(self):
        delta = DeltaDetect(1.0)
        self.assertTrue(delta.set('A', 7.0))
        self.assertTrue(delta.set('B', -17.0))
        self.assertFalse(delta.set('A', 7.9))
        self.assertFalse(delta.set('B', -17.99))
        self.assertTrue(delta.set('A', 8.0))
        self.assertTrue(delta.set('B', -18.0))
        self.assertFalse(delta.set('A', 8.9))
        self.assertFalse(delta.set('B', -18.99))
        self.assertTrue(delta.set('A', 9.0))
        self.assertTrue(delta.set('B', -19.0))

    def test_delta_detect_dict_simple(self):
        delta = DeltaDetect(1.0)
        self.assertEqual({'a': 1.0}, delta.check({'a': 1.0}))
        self.assertEqual({}, delta.check({'a': 1.0}))
        self.assertEqual({}, delta.check({'a': 1.99}))
        self.assertEqual({'a': 2.0}, delta.check({'a': 2.0}))

    def test_delta_detect_dict_two(self):
        delta = DeltaDetect(1.0)
        self.assertEqual({'a': 1.0, 'b': 7.4}, delta.check({'a': 1.0, 'b': 7.4}))
        self.assertEqual({}, delta.check({'a': 1.0}))
        self.assertEqual({}, delta.check({'b': 7.4}))
        self.assertEqual({'a': 2.0}, delta.check({'a': 2.0}))
        self.assertEqual({'b': 9.4}, delta.check({'b': 9.4}))


class TestHelpers(unittest.TestCase):

    def test_split_message(self):
        self.assertEqual({'aaa': 1.2, 'bbb': 4.5}, Helpers.split_message('1|aaa:1.2;bbb:4.5;'))

if __name__ == '__main__':
    unittest.main()
