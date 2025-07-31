#!/usr/bin/env python3
"""
Test code for the data processing system
Tests the functionality of func.py and lib.py modules
"""

import os
import tempfile
import shutil
import sys
from lib import read_csv_file, display_csv_data, read_output_folder_csv, get_data_summary
from func import apply_function, process_data


def create_test_data(test_folder):
    """
    Create test data for testing
    
    Args:
        test_folder (str): Path to create test data in
    """
    test_data_path = os.path.join(test_folder, "data.csv")
    
    # Create test data based on specification example
    test_values = [1, 3, 5, 56, 23, 664]
    
    with open(test_data_path, 'w') as f:
        f.write("data\n")
        for value in test_values:
            f.write(f"{value}\n")
    
    print(f"Created test data at: {test_data_path}")
    return test_values


def test_function():
    """
    Test the apply_function with known values
    """
    print("=== Testing apply_function ===")
    test_cases = [
        (1, -4),    # f(1) = -5*1 + 1 = -4
        (3, -14),   # f(3) = -5*3 + 1 = -14
        (5, -24),   # f(5) = -5*5 + 1 = -24
        (0, 1),     # f(0) = -5*0 + 1 = 1
        (-2, 11),   # f(-2) = -5*(-2) + 1 = 11
    ]
    
    all_passed = True
    for x, expected in test_cases:
        result = apply_function(x)
        passed = result == expected
        all_passed = all_passed and passed
        status = "PASS" if passed else "FAIL"
        print(f"f({x}) = {result}, expected = {expected} [{status}]")
    
    return all_passed


def test_lib_functions(output_folder):
    """
    Test the library functions
    
    Args:
        output_folder (str): Path to output folder for testing
    """
    print("\n=== Testing lib.py functions ===")
    
    # Test read_output_folder_csv
    print("\n--- Testing read_output_folder_csv ---")
    read_output_folder_csv(output_folder)
    
    # Test get_data_summary
    csv_path = os.path.join(output_folder, "data.csv")
    if os.path.exists(csv_path):
        print("\n--- Testing get_data_summary ---")
        summary = get_data_summary(csv_path)
        if summary:
            print(f"Summary statistics:")
            print(f"  Count: {summary['count']}")
            print(f"  Min: {summary['min']}")
            print(f"  Max: {summary['max']}")
            print(f"  Mean: {summary['mean']:.2f}")


def run_full_test():
    """
    Run complete test of the system
    """
    print("Starting comprehensive test of the data processing system...")
    
    # Create temporary directories for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        input_folder = os.path.join(temp_dir, "input")
        output_folder = os.path.join(temp_dir, "output")
        
        os.makedirs(input_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)
        
        try:
            # Step 1: Test the function
            function_test_passed = test_function()
            
            # Step 2: Create test data
            print(f"\n=== Creating test data ===")
            original_values = create_test_data(input_folder)
            
            # Step 3: Process data
            print(f"\n=== Processing data ===")
            process_data(input_folder, output_folder)
            
            # Step 4: Verify results
            print(f"\n=== Verifying results ===")
            output_file = os.path.join(output_folder, "data.csv")
            
            if os.path.exists(output_file):
                processed_values = read_csv_file(output_file)
                
                # Check if processing was correct
                expected_values = [apply_function(x) for x in original_values]
                
                if len(processed_values) == len(expected_values):
                    all_correct = all(abs(p - e) < 1e-10 for p, e in zip(processed_values, expected_values))
                    
                    if all_correct:
                        print("✓ Data processing verification PASSED")
                    else:
                        print("✗ Data processing verification FAILED")
                        print("Expected:", expected_values)
                        print("Got:", processed_values)
                else:
                    print(f"✗ Length mismatch: expected {len(expected_values)}, got {len(processed_values)}")
            
            # Step 5: Test library functions
            test_lib_functions(output_folder)
            
            # Final summary
            print(f"\n=== Test Summary ===")
            print(f"Function test: {'PASSED' if function_test_passed else 'FAILED'}")
            print(f"Data processing: {'COMPLETED' if os.path.exists(output_file) else 'FAILED'}")
            print(f"Library functions: TESTED")
            
        except Exception as e:
            print(f"Test failed with error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    run_full_test()
