import unittest
import random
import string
import sys
import os

# Add parent directory to path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import analyze_file

class FuzzTest(unittest.TestCase):
    def setUp(self):
        self.valid_code = """
import json
def example(a, b):
    if a > b:
        return a
    return b
"""
        self.iterations = 100

    def mutate(self, code):
        """Randomly mutate the code string."""
        mutation_type = random.choice(['delete', 'insert', 'replace', 'flip'])
        code_list = list(code)
        
        if not code_list:
            return code
            
        pos = random.randint(0, len(code_list) - 1)
        
        if mutation_type == 'delete':
            del code_list[pos]
        elif mutation_type == 'insert':
            char = random.choice(string.printable)
            code_list.insert(pos, char)
        elif mutation_type == 'replace':
            char = random.choice(string.printable)
            code_list[pos] = char
        elif mutation_type == 'flip':
            # Bit flip simulation on a character
            char_code = ord(code_list[pos])
            bit_to_flip = 1 << random.randint(0, 6)
            code_list[pos] = chr(char_code ^ bit_to_flip)
            
        return "".join(code_list)

    def test_fuzzing_analyze_file(self):
        """
        Fuzzing Test: Feed mutated code to the analyzer and ensure it doesn't crash.
        It should either return results or handle errors gracefully, but NOT raise unhandled exceptions.
        """
        print(f"\nRunning Fuzzing Test ({self.iterations} iterations)...")
        
        crashes = 0
        for i in range(self.iterations):
            # Mutate
            mutated_code = self.mutate(self.valid_code)
            # Apply multiple mutations sometimes
            if random.random() < 0.3:
                mutated_code = self.mutate(mutated_code)
                
            try:
                # We pass a dummy filename but provide content via stdin simulation
                # The function should handle this without crashing
                analyze_file("fuzzed_input.py", content=mutated_code)
            except Exception as e:
                print(f"CRASH DETECTED at iteration {i}!")
                print(f"Input: {repr(mutated_code)}")
                print(f"Error: {e}")
                crashes += 1
        
        if crashes > 0:
            self.fail(f"Fuzzer found {crashes} crashes in {self.iterations} iterations.")
        else:
            print("Fuzzing completed successfully. No crashes found.")

if __name__ == '__main__':
    unittest.main()
