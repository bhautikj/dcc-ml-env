import unittest
from src.utils.helpers import add

class TestIntegration(unittest.TestCase):
    def test_add(self):
        result = add(10, 5)
        self.assertEqual(result, 15)

if __name__ == '__main__':
    unittest.main()
