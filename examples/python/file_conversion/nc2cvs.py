import xarray as xr
import os
import glob
import time
from pathlib import Path
from tqdm.notebook import tqdm  # For nice progress bars in Jupyter
import pandas as pd

def nc_to_csv_xarray(nc_file, output_dir=None, engine='netcdf4'):
    """
    Convert a NetCDF file to CSV using xarray
    
    Parameters:
    -----------
    nc_file : str
        Path to the NetCDF file
    output_dir : str, optional
        Directory to save CSV files
    engine : str, optional
        Engine to use for opening the NetCDF file. Options: 'netcdf4', 'scipy', 'h5netcdf'
    
    Returns:
    --------
    bool
        True if conversion was successful, False otherwise
    """
    # Create output directory if specified
    if output_dir is None:
        output_dir = os.path.dirname(nc_file)
    os.makedirs(output_dir, exist_ok=True)
    
    # Get base filename without extension
    base_name = os.path.splitext(os.path.basename(nc_file))[0]
    
    try:
        # Open the NetCDF file with xarray, explicitly specifying the engine
        print(f"Opening file with {engine} engine: {nc_file}")
        ds = xr.open_dataset(nc_file)
        
        # Print dataset information
        print(f"NetCDF file information:")
        print(f"Dimensions: {list(ds.dims.keys())}")
        print(f"Variables: {list(ds.variables.keys())}")
        print(f"Data variables: {list(ds.data_vars.keys())}")
        print(f"Coordinates: {list(ds.coords.keys())}")
        
        # Export each data variable to CSV
        for var_name in ds.data_vars:
            print(f"\nProcessing variable: {var_name}")
            var = ds[var_name]
            print(f"Dimensions: {var.dims}")
            print(f"Shape: {var.shape}")
            
            try:
                # Convert to dataframe
                df = var.to_dataframe()
                
                # Reset index to convert multi-index to columns (makes CSV more readable)
                df = df.reset_index()
                
                # Save to CSV
                csv_filename = f"{base_name}_{var_name}.csv"
                csv_path = os.path.join(output_dir, csv_filename)
                df.to_csv(csv_path, index=False)
                print(f"Saved {csv_path}")
                
            except Exception as e:
                print(f"Error processing variable {var_name}: {e}")
        
        # Option to export the entire dataset to a single CSV
        try:
            print("\nAttempting to export full dataset to single CSV...")
            df_all = ds.to_dataframe().reset_index()
            all_csv_path = os.path.join(output_dir, f"{base_name}_all_variables.csv")
            df_all.to_csv(all_csv_path, index=False)
            print(f"Saved complete dataset to {all_csv_path}")
        except Exception as e:
            print(f"Could not export full dataset to single CSV: {e}")
        
        ds.close()
        print(f"\nConversion complete for {nc_file}!")
        return True
        
    except ValueError as e:
        print(f"Error opening the file with {engine} engine: {e}")
        
        # Try alternative engines if the specified one fails
        alternative_engines = ['netcdf4', 'scipy', 'h5netcdf']
        if engine in alternative_engines:
            alternative_engines.remove(engine)
        
        for alt_engine in alternative_engines:
            try:
                print(f"Attempting to open with {alt_engine} engine...")
                ds = xr.open_dataset(nc_file, engine=alt_engine)
                ds.close()
                # If successful, recursively call this function with the working engine
                return nc_to_csv_xarray(nc_file, output_dir, alt_engine)
            except Exception as e2:
                print(f"Failed with {alt_engine} engine: {e2}")
        
        print(f"\nCould not open the NetCDF file {nc_file} with any available engine.")
        return False

def process_directory(input_dir, output_dir=None, engine='netcdf4', file_patterns=None, 
                     recursive=False, max_depth=None, preserve_structure=True):
    """
    Process all files matching patterns in a directory
    
    Parameters:
    -----------
    input_dir : str
        Directory containing files to process
    output_dir : str, optional
        Directory to save CSV files. If None, will create a 'csv_output' subfolder
    engine : str, optional
        Engine to use for opening the files
    file_patterns : list, optional
        List of file patterns to match (default: ["*.nc"])
    recursive : bool, optional
        Whether to search for files recursively in subdirectories
    max_depth : int, optional
        Maximum recursion depth (None for no limit)
    preserve_structure : bool, optional
        Whether to preserve the directory structure in the output
    
    Returns:
    --------
    dict
        Dictionary with statistics about the conversion process
    """
    # Set default file patterns if none provided
    if file_patterns is None:
        file_patterns = ["*.nc"]
    elif isinstance(file_patterns, str):
        file_patterns = [file_patterns]
        
    # Normalize paths
    input_dir = os.path.abspath(input_dir)
    
    if output_dir is None:
        output_dir = os.path.join(input_dir, 'csv_output')
    else:
        output_dir = os.path.abspath(output_dir)
    
    # Make sure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all matching files in the directory
    all_files = []
    
    for pattern in file_patterns:
        if recursive:
            if max_depth is None:
                # No depth limit, use rglob
                matching_files = [str(p) for p in Path(input_dir).rglob(pattern)]
            else:
                # Limited depth recursion
                matching_files = []
                for depth in range(max_depth + 1):
                    parts = ['*'] * depth
                    if parts:
                        search_pattern = os.path.join(input_dir, *parts, pattern)
                    else:
                        search_pattern = os.path.join(input_dir, pattern)
                    matching_files.extend(glob.glob(search_pattern))
        else:
            # Non-recursive, just use glob
            matching_files = glob.glob(os.path.join(input_dir, pattern))
        
        all_files.extend(matching_files)
    
    # Remove duplicates (in case patterns overlap)
    all_files = list(set(all_files))
    
    if not all_files:
        patterns_str = ", ".join(file_patterns)
        print(f"No matching files found in {input_dir} with patterns: {patterns_str}")
        return {"total": 0, "successful": 0, "failed": 0, "time": 0}
    
    print(f"Found {len(all_files)} files to process in {input_dir}")
    
    # Process each file
    successful = 0
    failed = 0
    start_time = time.time()
    
    for i, file_path in enumerate(all_files, 1):
        print(f"\n[{i}/{len(all_files)}] Processing: {os.path.relpath(file_path, input_dir)}")
        
        # Determine the output directory
        if preserve_structure:
            # Keep the same directory structure in the output
            rel_path = os.path.relpath(os.path.dirname(file_path), input_dir)
            file_output_dir = os.path.join(output_dir, rel_path, os.path.splitext(os.path.basename(file_path))[0])
        else:
            # Flatten the structure
            file_output_dir = os.path.join(output_dir, os.path.splitext(os.path.basename(file_path))[0])
        
        if nc_to_csv_xarray(file_path, file_output_dir, engine):
            successful += 1
        else:
            failed += 1
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Print summary
    print("\n" + "="*50)
    print(f"Conversion Summary for {input_dir}:")
    print(f"Total files processed: {len(all_files)}")
    print(f"Successfully converted: {successful}")
    print(f"Failed to convert: {failed}")
    print(f"Time taken: {elapsed_time:.2f} seconds")
    print("="*50)
    
    return {
        "total": len(all_files),
        "successful": successful,
        "failed": failed,
        "time": elapsed_time
    }

def process_specific_files(file_paths, output_base_dir=None, engine='netcdf4', preserve_structure=True):
    """
    Process a list of specific files
    
    Parameters:
    -----------
    file_paths : str or list of str
        Comma-separated string or list of specific files to process
    output_base_dir : str, optional
        Base directory for all outputs
    engine : str, optional
        Engine to use for opening the files
    preserve_structure : bool, optional
        Whether to preserve the directory structure in the output
    
    Returns:
    --------
    dict
        Dictionary with statistics about the conversion process
    """
    # Process file paths (accept both comma-separated string and list)
    if isinstance(file_paths, str):
        file_paths = [f.strip() for f in file_paths.split(',')]
    
    # Make sure all paths are absolute
    file_paths = [os.path.abspath(f) for f in file_paths]
    
    # Filter out non-existent files
    valid_files = [f for f in file_paths if os.path.isfile(f)]
    invalid_files = set(file_paths) - set(valid_files)
    
    if invalid_files:
        print(f"Warning: {len(invalid_files)} specified files do not exist and will be skipped:")
        for f in invalid_files:
            print(f"  - {f}")
    
    if not valid_files:
        print("No valid files to process")
        return {"total": 0, "successful": 0, "failed": 0, "time": 0}
    
    print(f"Found {len(valid_files)} valid files to process")
    
    # Create output base directory if specified
    if output_base_dir is not None:
        os.makedirs(output_base_dir, exist_ok=True)
    
    # Process each file
    successful = 0
    failed = 0
    start_time = time.time()
    
    for i, file_path in enumerate(valid_files, 1):
        print(f"\n[{i}/{len(valid_files)}] Processing: {file_path}")
        
        # Determine the output directory
        if output_base_dir is not None:
            if preserve_structure:
                # Keep partial directory structure
                parent_dir = os.path.basename(os.path.dirname(file_path))
                file_output_dir = os.path.join(output_base_dir, parent_dir, os.path.splitext(os.path.basename(file_path))[0])
            else:
                # Flatten the structure
                file_output_dir = os.path.join(output_base_dir, os.path.splitext(os.path.basename(file_path))[0])
        else:
            # Use same directory as the file
            file_output_dir = os.path.join(os.path.dirname(file_path), os.path.splitext(os.path.basename(file_path))[0] + "_csv")
        
        if nc_to_csv_xarray(file_path, file_output_dir, engine):
            successful += 1
        else:
            failed += 1
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    # Print summary
    print("\n" + "="*50)
    print(f"Specific Files Conversion Summary:")
    print(f"Total files processed: {len(valid_files)}")
    print(f"Successfully converted: {successful}")
    print(f"Failed to convert: {failed}")
    print(f"Time taken: {elapsed_time:.2f} seconds")
    print("="*50)
    
    return {
        "total": len(valid_files),
        "successful": successful,
        "failed": failed,
        "time": elapsed_time
    }

def process_multiple_inputs(input_paths, file_patterns=None, output_base_dir=None, engine='netcdf4', 
                          recursive=False, max_depth=None, preserve_structure=True):
    """
    Process multiple directories, subdirectories and specific files
    
    Parameters:
    -----------
    input_paths : str or list of str
        Comma-separated string or list of paths to process. Can include:
        - Directories to scan for matching files
        - Specific files to process directly
    file_patterns : str or list of str, optional
        Comma-separated string or list of file patterns to match (default: "*.nc")
    output_base_dir : str, optional
        Base directory for all outputs. If None, each input dir will have its own 'csv_output'
    engine : str, optional
        Engine to use for opening the files
    recursive : bool, optional
        Whether to search for files recursively in subdirectories
    max_depth : int, optional
        Maximum recursion depth (None for no limit)
    preserve_structure : bool, optional
        Whether to preserve the directory structure in the output
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with statistics for each directory and file set
    """
    # Process input paths (accept both comma-separated string and list)
    if isinstance(input_paths, str):
        input_paths = [p.strip() for p in input_paths.split(',')]
    
    # Process file patterns (accept both comma-separated string and list)
    if isinstance(file_patterns, str):
        file_patterns = [p.strip() for p in file_patterns.split(',')]
    
    # Separate directories and files
    directories = []
    specific_files = []

    cpath = os.getcwd()
    for path in input_paths:
        path = cpath+"/"+path
        if os.path.isdir(path):
            directories.append(path)
        elif os.path.isfile(path):
            specific_files.append(path)
        else:
            print(f"Warning: Path not found or not accessible: {path}")
    
    start_time = time.time()
    stats = []
    
    # Process directories
    if directories:
        print(f"Processing {len(directories)} directories with patterns: {file_patterns}")
        
        for i, input_dir in enumerate(directories, 1):
            print(f"\n\n{'='*60}")
            print(f"Directory {i}/{len(directories)}: {input_dir}")
            print(f"{'='*60}")
            
            if output_base_dir is not None:
                # Use subdirectory of the base output dir
                dir_name = os.path.basename(os.path.normpath(input_dir))
                output_dir = os.path.join(output_base_dir, dir_name)
            else:
                # Create output directory in each input directory
                output_dir = None
            
            # Process the directory
            dir_stats = process_directory(
                input_dir=input_dir,
                output_dir=output_dir,
                engine=engine,
                file_patterns=file_patterns,
                recursive=recursive,
                max_depth=max_depth,
                preserve_structure=preserve_structure
            )
            
            # Add directory info to stats
            dir_stats['directory'] = input_dir
            stats.append(dir_stats)
    
    # Process specific files if any
    if specific_files:
        print(f"\n\n{'='*60}")
        print(f"Processing {len(specific_files)} specific files")
        print(f"{'='*60}")
        
        file_output_dir = output_base_dir if output_base_dir else None
        file_stats = process_specific_files(
            file_paths=specific_files,
            output_base_dir=file_output_dir,
            engine=engine,
            preserve_structure=preserve_structure
        )
        
        # Add file set info to stats
        file_stats['directory'] = "Specific Files"
        stats.append(file_stats)
    
    # Calculate overall statistics
    total_time = time.time() - start_time
    total_files = sum(s['total'] for s in stats)
    total_successful = sum(s['successful'] for s in stats)
    total_failed = sum(s['failed'] for s in stats)
    
    # Print overall summary
    print("\n\n" + "="*60)
    print("OVERALL CONVERSION SUMMARY:")
    
    if directories:
        print(f"Total directories processed: {len(directories)}")
    if specific_files:
        print(f"Total specific files processed: {len(specific_files)}")
        
    print(f"Total files processed: {total_files}")
    print(f"Total successfully converted: {total_successful}")
    print(f"Total failed: {total_failed}")
    print(f"Total time taken: {total_time:.2f} seconds")
    print("="*60)
    
    # Create a DataFrame with statistics
    stats_df = pd.DataFrame(stats)
    if not stats_df.empty:
        stats_df['success_rate'] = stats_df['successful'] / stats_df['total'] * 100
    
    return stats_df

# Example usage in Jupyter Notebook
if __name__ == "__main__":

    # Ask the user for a folder name
    folder_name = input("Please enter the name of the output folder you want to use: ")

    # Check if the folder already exists
    if os.path.exists(folder_name):
        print(f"The folder '{folder_name}' already exists.")
    else:
        # Create the folder
        try:
            os.makedirs(folder_name)
            print(f"Folder '{folder_name}' has been created successfully!")
        except Exception as e:
            print(f"An error occurred while creating the folder: {e}")
    # Input paths - can include directories and specific files
    input_paths = input("Please enter the names of the input files and folders: ")
    #input_paths = "/home/jovyan/ncin1, /home/jovyan/ncin2, /home/jovyan/ncin3/USM_NGOFS22025042803SALINITY_t054.nc"
    #input_paths = ncin1, ncin2, ncin3/USM_NGOFS22025042803SALINITY_t054.nc
    # File patterns to match (comma-separated string or list)
    file_patterns = "*.nc, *.netcdf, *.NC"

    cpath = os.getcwd()
    # Common output directory for all (optional)
    # common_output_dir = "/home/jovyan/ncout1"
    common_output_dir = cpath+"/"+folder_name
    
    # Process all inputs with specified file patterns
    stats_df = process_multiple_inputs(
        input_paths=input_paths,
        file_patterns=file_patterns,
        output_base_dir=common_output_dir,  # Set to None to use separate output dirs
        engine='scipy',                     # Engine to use
        recursive=True,                     # Search in subdirectories
        max_depth=4,                        # Maximum folder depth for recursion
        preserve_structure=True             # Preserve directory structure in output
    )
    
    # Display the statistics DataFrame
    print(stats_df)
    
    # If running in Jupyter, you can create visualizations
    try:
        import matplotlib.pyplot as plt
        
        # Create a bar chart of successful vs failed conversions
        plt.figure(figsize=(10, 6))
        stats_df.plot(
            x='directory', 
            y=['successful', 'failed'], 
            kind='bar', 
            stacked=True,
            color=['green', 'red']
        )
        plt.title('NetCDF Conversion Results by Directory')
        plt.ylabel('Number of Files')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()
        
        # Create a pie chart of overall success rate
        total_success = stats_df['successful'].sum()
        total_fail = stats_df['failed'].sum()
        
        plt.figure(figsize=(8, 8))
        plt.pie([total_success, total_fail], 
                labels=['Successful', 'Failed'],
                colors=['green', 'red'],
                autopct='%1.1f%%',
                startangle=90,
                explode=(0.05, 0))
        plt.title('Overall NetCDF Conversion Results')
        plt.axis('equal')
        plt.show()
    except ImportError:
        print("Matplotlib not available for visualization.")
