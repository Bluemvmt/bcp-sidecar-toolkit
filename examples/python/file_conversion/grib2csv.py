#!/usr/bin/env python3
"""
GRIB File to CSV Converter
Extracts observation time and all measured variables from GRIB files
and saves them in CSV format with columns: day, time, variable1, variable2, etc.
"""

import pygrib
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

def extract_grib_to_csv(grib_file_path, output_csv_path, lat_point=None, lon_point=None):
    """
    Extract data from GRIB file and save to CSV
    
    Parameters:
    - grib_file_path: Path to the GRIB file
    - output_csv_path: Path for the output CSV file
    - lat_point: Specific latitude point to extract (optional)
    - lon_point: Specific longitude point to extract (optional)
    
    If lat_point and lon_point are None, extracts data for all grid points
    """
    
    try:
        # Open GRIB file
        grbs = pygrib.open(grib_file_path)
        
        # Dictionary to store all data
        data_dict = {}
        
        # Process each message/variable in the GRIB file
        for grb in grbs:
            # Extract time information
            valid_date = grb.validDate
            day = valid_date.strftime('%Y-%m-%d')
            time = valid_date.strftime('%H:%M:%S')
            
            # Get variable name and level info
            var_name = grb.name
            level = getattr(grb, 'level', 0)
            type_of_level = getattr(grb, 'typeOfLevel', 'surface')
            
            # Create unique variable identifier
            if type_of_level == 'surface' or level == 0:
                var_id = var_name
            else:
                var_id = f"{var_name}_{level}_{type_of_level}"
            
            # Extract data values
            if lat_point is not None and lon_point is not None:
                # Extract data for specific point
                data, lats, lons = grb.data()
                # Find nearest grid point
                lat_idx = np.argmin(np.abs(lats[:, 0] - lat_point))
                lon_idx = np.argmin(np.abs(lons[0, :] - lon_point))
                value = data[lat_idx, lon_idx]
            else:
                # Extract all grid points (flatten to 1D array)
                data = grb.values.flatten()
                # For CSV, we'll take the mean value across all grid points
                # You can modify this to suit your needs
                value = np.mean(data[~np.isnan(data)])
            
            # Store in dictionary
            time_key = f"{day} {time}"
            if time_key not in data_dict:
                data_dict[time_key] = {'day': day, 'time': time}
            
            data_dict[time_key][var_id] = value
        
        grbs.close()
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(data_dict, orient='index')
        
        # Ensure day and time are first columns
        cols = ['day', 'time'] + [col for col in df.columns if col not in ['day', 'time']]
        df = df[cols]
        
        # Sort by day and time
        df = df.sort_values(['day', 'time'])
        
        # Save to CSV
        df.to_csv(output_csv_path, index=False)
        
        print(f"Successfully extracted data from {grib_file_path}")
        print(f"Saved to {output_csv_path}")
        print(f"Variables found: {list(df.columns[2:])}")
        print(f"Time range: {df['day'].min()} to {df['day'].max()}")
        print(f"Total records: {len(df)}")
        
        return df
        
    except Exception as e:
        print(f"Error processing GRIB file: {e}")
        return None

def batch_process_grib_files(input_directory, output_directory):
    """
    Process multiple GRIB files in a directory
    """
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    grib_files = [f for f in os.listdir(input_directory) 
                  if f.lower().endswith(('.grib', '.grib2', '.grb', '.grb2'))]
    
    for grib_file in grib_files:
        input_path = os.path.join(input_directory, grib_file)
        output_file = os.path.splitext(grib_file)[0] + '.csv'
        output_path = os.path.join(output_directory, output_file)
        
        print(f"\nProcessing: {grib_file}")
        extract_grib_to_csv(input_path, output_path)

def explore_grib_file(grib_file_path):
    """
    Explore the contents of a GRIB file to understand its structure
    """
    try:
        grbs = pygrib.open(grib_file_path)
        
        print(f"GRIB File: {grib_file_path}")
        print("=" * 50)
        
        variables = {}
        dates = set()
        
        for i, grb in enumerate(grbs):
            var_name = grb.name
            level = getattr(grb, 'level', 0)
            type_of_level = getattr(grb, 'typeOfLevel', 'surface')
            valid_date = grb.validDate
            
            dates.add(valid_date)
            
            var_key = f"{var_name} ({type_of_level}: {level})"
            if var_key not in variables:
                variables[var_key] = 0
            variables[var_key] += 1
        
        print(f"Total messages: {i + 1}")
        print(f"Unique dates: {len(dates)}")
        print(f"Date range: {min(dates)} to {max(dates)}")
        print("\nVariables found:")
        for var, count in variables.items():
            print(f"  {var}: {count} records")
        
        grbs.close()
        
    except Exception as e:
        print(f"Error exploring GRIB file: {e}")

# Example usage
if __name__ == "__main__":
    # Example 1: Extract data from a single GRIB file
    grib_file = "North55.37West165.76South51.19East179.95.grib"  # Replace with your GRIB file path
    csv_file = "weather_data.csv"
    
    # Explore the GRIB file first (optional)
    if os.path.exists(grib_file):
        explore_grib_file(grib_file)
        
        # Extract data to CSV
        df = extract_grib_to_csv(grib_file, csv_file)
        
        if df is not None:
            print("\nFirst few rows of extracted data:")
            print(df.head())
    
    # Example 2: Extract data for a specific location
    # df = extract_grib_to_csv(grib_file, "weather_data_point.csv", 
    #                         lat_point=40.7128, lon_point=-74.0060)  # NYC coordinates
    
    # Example 3: Batch process multiple GRIB files
    # batch_process_grib_files("input_grib_files/", "output_csv_files/")
