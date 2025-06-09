# NetCDF to CSV Converter Tool

A robust Python utility for converting NetCDF files to CSV format using the xarray library.

## Overview

This tool provides a flexible and powerful solution for converting scientific NetCDF (Network Common Data Form) files to more widely accessible CSV format. It uses the xarray library for efficient data handling and supports various conversion options including:

- Converting individual NetCDF files
- Batch processing directories of NetCDF files
- Recursive directory scanning
- Preserving directory structures
- Supporting multiple NetCDF engine types (netcdf4, scipy, h5netcdf)

## Features

- **Comprehensive Variable Export**: Extracts all variables from NetCDF files into separate CSV files
- **Automatic Engine Selection**: Falls back to alternative engines if the primary engine fails
- **Structured Output Organization**: Maintains directory structure in output if desired
- **Detailed Progress Reporting**: Provides real-time progress updates and summary statistics
- **Flexible Input Options**: Process individual files, directories, or mixed input paths
- **Visualization Support**: Generates charts showing conversion statistics (when run in Jupyter)

## Requirements

- Python 3.x
- xarray
- pandas
- tqdm (for progress bars in Jupyter)
- matplotlib (optional, for visualization)

## Installation

```bash
# Install required packages
pip install xarray pandas tqdm matplotlib

# NetCDF engines (install at least one)
pip install netCDF4 scipy h5netcdf
```

## Usage Examples

### Basic Command Line Usage

```python
# Import the module
from netcdf_to_csv import process_multiple_inputs

# Process files and directories
stats_df = process_multiple_inputs(
    input_paths="path/to/directory1, path/to/file1.nc, path/to/directory2",
    file_patterns="*.nc, *.netcdf",
    output_base_dir="path/to/output",
    engine='netcdf4',
    recursive=True,
    max_depth=2,
    preserve_structure=True
)

# Display statistics
print(stats_df)
```

### Interactive Usage

```python
# Ask for user input
folder_name = input("Please enter the name of the output folder: ")
input_paths = input("Please enter the names of the input files and folders: ")

# Process the inputs
stats_df = process_multiple_inputs(
    input_paths=input_paths,
    file_patterns="*.nc, *.netcdf, *.NC",
    output_base_dir=folder_name,
    engine='scipy',
    recursive=True,
    max_depth=2,
    preserve_structure=True
)
```

## Function Reference

### `nc_to_csv_xarray(nc_file, output_dir=None, engine='netcdf4')`

Converts a single NetCDF file to CSV format.

**Parameters:**
- `nc_file`: Path to the NetCDF file
- `output_dir`: Directory to save CSV files (defaults to same directory as input)
- `engine`: Engine to use for opening the NetCDF file ('netcdf4', 'scipy', 'h5netcdf')

**Returns:**
- `bool`: True if conversion was successful, False otherwise

### `process_directory(input_dir, output_dir=None, engine='netcdf4', file_patterns=None, recursive=False, max_depth=None, preserve_structure=True)`

Processes all files matching patterns in a directory.

**Parameters:**
- `input_dir`: Directory containing files to process
- `output_dir`: Directory to save CSV files
- `engine`: Engine to use for opening files
- `file_patterns`: List of file patterns to match (default: ["*.nc"])
- `recursive`: Whether to search recursively in subdirectories
- `max_depth`: Maximum recursion depth
- `preserve_structure`: Whether to preserve directory structure in output

**Returns:**
- `dict`: Statistics about the conversion process

### `process_specific_files(file_paths, output_base_dir=None, engine='netcdf4', preserve_structure=True)`

Processes a list of specific files.

**Parameters:**
- `file_paths`: List or comma-separated string of specific files
- `output_base_dir`: Base directory for outputs
- `engine`: Engine to use
- `preserve_structure`: Whether to preserve directory structure

**Returns:**
- `dict`: Statistics about the conversion process

### `process_multiple_inputs(input_paths, file_patterns=None, output_base_dir=None, engine='netcdf4', recursive=False, max_depth=None, preserve_structure=True)`

Processes multiple directories, subdirectories, and specific files.

**Parameters:**
- `input_paths`: List or comma-separated string of paths (directories and files)
- `file_patterns`: File patterns to match
- `output_base_dir`: Base directory for all outputs
- `engine`: Engine to use
- `recursive`: Whether to search recursively
- `max_depth`: Maximum recursion depth
- `preserve_structure`: Whether to preserve directory structure

**Returns:**
- `pd.DataFrame`: Statistics for each directory and file set

## Output Format

For each NetCDF file, the tool creates:

1. Individual CSV files for each variable in the NetCDF file
2. A combined CSV file with all variables where possible

## Visualization

When running in a Jupyter environment with matplotlib available, the tool automatically generates:

- Bar charts showing successful vs. failed conversions by directory
- Pie charts showing the overall success rate

## Error Handling

The tool includes robust error handling:
- Automatically attempts alternative engines if the primary engine fails
- Provides detailed error messages for troubleshooting
- Continues processing other files even if some fail
