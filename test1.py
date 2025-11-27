import unittest

# 待测试函数：两数相加
def add(a, b):
    return a + b

# 测试用例
class TestAddFunction(unittest.TestCase):
    def test_normal_add(self):
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(-1, 1), 0)
    
    def test_float_add(self):
        self.assertAlmostEqual(add(2.5, 3.5), 6.0)
    
    def test_boundary_add(self):
        self.assertEqual(add(0, 0), 0)
        self.assertEqual(add(9999, -9999), 0)

if __name__ == "__main__":
    unittest.main(verbosity=1)