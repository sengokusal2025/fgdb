#!/usr/bin/env python3
"""
Library functions for reading and displaying CSV data
Contains functions to read output CSV files and display them to stdout
"""

import os
import sys


def read_csv_file(file_path):
    """
    Read CSV file and return data as a list
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        list: List of data values from the CSV file
        
    Raises:
        FileNotFoundError: If the specified file does not exist
        ValueError: If the file contains invalid data
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    data_values = []
    
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Parse data (skip header if exists)
        for line in lines:
            line = line.strip()
            if line and line != 'data' and line != 'x':  # Skip header rows
                try:
                    data_values.append(float(line))
                except ValueError:
                    print(f"Warning: Skipping invalid data: {line}")
        
        return data_values
        
    except Exception as e:
        raise ValueError(f"Error reading file {file_path}: {e}")


def display_csv_data(file_path):
    """
    Read CSV file from output folder and display contents to stdout
    
    Args:
        file_path (str): Path to the CSV file to display
    """
    try:
        data_values = read_csv_file(file_path)
        
        if not data_values:
            print("No data found in the file")
            return
        
        print(f"=== Contents of {file_path} ===")
        print("data")  # Header
        for value in data_values:
            print(value)
        print(f"=== Total: {len(data_values)} values ===")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def read_output_folder_csv(output_folder):
    """
    Read data.csv from the specified output folder and display to stdout
    
    Args:
        output_folder (str): Path to the output folder containing data.csv
    """
    csv_file_path = os.path.join(output_folder, "data.csv")
    display_csv_data(csv_file_path)


def get_data_summary(file_path):
    """
    Get summary statistics of the data in CSV file
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        dict: Dictionary containing summary statistics
    """
    try:
        data_values = read_csv_file(file_path)
        
        if not data_values:
            return {"count": 0, "min": None, "max": None, "mean": None}
        
        return {
            "count": len(data_values),
            "min": min(data_values),
            "max": max(data_values),
            "mean": sum(data_values) / len(data_values)
        }
        
    except Exception as e:
        print(f"Error calculating summary: {e}")
        return None


if __name__ == "__main__":
    # Simple test when run directly
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        print(f"Testing with file: {test_file}")
        display_csv_data(test_file)
    else:
        print("Usage: python lib.py <csv_file_path>")
