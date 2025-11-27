import os
import sys

# 1. Basic Smell: Unused import (Pylint: unused-import)
import json

# 2. Basic Smell: Bad naming style (Pylint: invalid-name)
X = 1
y = 2

# 3. Basic Smell: TODO comment (Pylint: fixme)
# TODO: This global variable needs to be moved to a configuration file

def very_long_function_name_that_is_hard_to_read_and_violates_naming_conventions():
    """
    4. Basic Smell: Missing docstring (fixed here), but bad name remains.
    """
    pass

def complex_logic_demo(score):
    """
    5. Advanced Feature Test: High Complexity
    This function is designed to trigger 'too-many-branches' or 'too-many-statements'.
    It should activate the 'Smart Refactoring Suggestion' in the report.
    """
    grade = "F"
    
    # A complex structure to generate a Control Flow Graph (CFG)
    if score >= 90:
        if score >= 95:
            grade = "A+"
            print("Excellent!")
        else:
            grade = "A"
    elif score >= 80:
        if score >= 85:
            grade = "B+"
        else:
            grade = "B"
    elif score >= 70:
        if score >= 75:
            grade = "C+"
        else:
            grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"
        print("Failed")

    # Adding a loop to make the CFG more interesting
    for i in range(5):
        if i % 2 == 0:
            print(f"Processing {i}")
        else:
            print(f"Skipping {i}")

    return grade

def duplicate_code_block_1():
    """6. Basic Smell: Duplicate code"""
    print("This is a block of code")
    print("That is repeated exactly")
    print("In another function")
    return True

def duplicate_code_block_2():
    """Duplicate of block 1"""
    print("This is a block of code")
    print("That is repeated exactly")
    print("In another function")
    return True
