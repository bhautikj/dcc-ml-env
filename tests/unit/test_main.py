import unittest
from src.main import main

class TestMain(unittest.TestCase):
    def test_main(self):
        # Capture stdout to check print statement
        from io import StringIO
        import sys
        captured_output = StringIO()
        sys.stdout = captured_output
        
        main()
        
        # Reset redirect.
        sys.stdout = sys.__stdout__
        
        self.assertEqual(captured_output.getvalue(), "Hello, World!\n")

if __name__ == '__main__':
    unittest.main()
