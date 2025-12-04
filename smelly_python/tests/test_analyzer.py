import unittest
import ast
import sys
import os

# Add parent directory to path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import generate_cfg, map_pylint_to_smell

class TestSmellyPython(unittest.TestCase):

    def test_map_pylint_to_smell(self):
        """Test that Pylint issues are correctly mapped to our format."""
        pylint_issue = {
            "type": "convention",
            "path": "test.py",
            "line": 10,
            "message": "Line too long",
            "symbol": "C0301"
        }
        
        result = map_pylint_to_smell(pylint_issue)
        
        self.assertEqual(result['severity'], 'Information')
        self.assertEqual(result['line'], 10)
        self.assertIn('Line too long', result['message'])

    def test_cfg_generation_simple(self):
        """Test CFG generation for a simple function."""
        code = """
def simple_func():
    print("Hello")
    return True
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        cfg = generate_cfg(func_node)
        
        self.assertIn("graph TD", cfg)
        self.assertIn("Start((Start: simple_func))", cfg)
        self.assertIn("Return", cfg)
        self.assertIn("End((End))", cfg)

    def test_cfg_generation_with_if(self):
        """Test CFG generation for a function with if statement."""
        code = """
def if_func(x):
    if x > 0:
        print("Positive")
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        cfg = generate_cfg(func_node)
        
        self.assertIn("If Condition", cfg)
        self.assertIn("{", cfg) # Shape for If

if __name__ == '__main__':
    unittest.main()
