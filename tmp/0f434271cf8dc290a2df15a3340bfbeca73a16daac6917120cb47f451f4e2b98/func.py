#!/usr/bin/env python3
"""
Main function processing script
Reads data from input CSV, applies function f(x) = -5*x + 1, and saves to output CSV
"""

import argparse
import os
import sys
import pandas as pd


def apply_function(x):
    """
    Apply the specified function f(x) = -5*x + 1
    
    Args:
        x (float): Input value
        
    Returns:
        float: Output value after applying function
    """
    return -5 * x + 1


def process_data(input_folder, output_folder):
    """
    Process data from input CSV and save results to output CSV
    
    Args:
        input_folder (str): Path to input folder containing data.csv
        output_folder (str): Path to output folder where results will be saved
    """
    # Construct file paths
    input_file = os.path.join(input_folder, "data.csv")
    output_file = os.path.join(output_folder, "data.csv")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    try:
        # Read input data
        with open(input_file, 'r') as f:
            lines = f.readlines()
        
        # Parse data (skip header if exists)
        x_values = []
        for line in lines:
            line = line.strip()
            if line and line != 'x' and line != 'data':  # Skip header rows
                try:
                    x_values.append(float(line))
                except ValueError:
                    print(f"Warning: Skipping invalid data: {line}")
        
        if not x_values:
            print("Error: No valid data found in input file")
            sys.exit(1)
        
        # Apply function to calculate y values
        y_values = [apply_function(x) for x in x_values]
        
        # Save output data
        with open(output_file, 'w') as f:
            f.write("data\n")  # Header according to format specification
            for y in y_values:
                f.write(f"{y}\n")
        
        print(f"Processing completed successfully!")
        print(f"Input: {len(x_values)} values processed")
        print(f"Output saved to: {output_file}")
        
    except Exception as e:
        print(f"Error processing data: {e}")
        sys.exit(1)


def main():
    """
    Main function to handle command line arguments and execute processing
    """
    parser = argparse.ArgumentParser(description="Process CSV data with function f(x) = -5*x + 1")
    parser.add_argument("-i", "--input", required=True, help="Input folder path containing data.csv")
    parser.add_argument("-o", "--output", required=True, help="Output folder path to save results")
    
    args = parser.parse_args()
    
    # Validate input arguments
    if not os.path.exists(args.input):
        print(f"Error: Input folder {args.input} does not exist")
        sys.exit(1)
    
    # Process the data
    process_data(args.input, args.output)


if __name__ == "__main__":
    main()
