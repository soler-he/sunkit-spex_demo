from pathlib import Path
import os
import csv
from datetime import datetime
import numpy as np

def sanitise_filename(s):
    """    Sanitises a string to be used as a filename by replacing invalid characters.
    
    Args:
        s (str): The string to sanitise.
    
    Returns:
        str: Sanitised string suitable for filenames.
    """
    
    return s.replace(':', '-')

def csv_writer(id, start, rows, delta_time, total_counts, times_dt, total_errors, subfolder=None):
    """    Write the provided data to a CSV file.

    Parameters:
    start: Start time of the data collection
    end: End time of the data collection
    t: List of times in UTC format
    dt: List of delta times in seconds
    counts: List of total counts
    errors: List of total errors

    Returns:
    None
    """

    output_folder = Path(subfolder)
    output_folder.mkdir(parents=True, exist_ok=True)   # ensure folder exists

    filename = f"{start.strftime('%Y-%m-%dT%H-%M-%S')}_{id}.csv"
    output_file = output_folder / filename

    # Write CSV
    with open(output_file, mode="w", newline="") as f:
        writer = csv.writer(f)

        # Write header
        writer.writerow(["", "time", "counts", "time_format", "yerr"])

        # Write data rows
        for row in zip(rows, delta_time, total_counts, times_dt, total_errors):
            writer.writerow(row)

    print(f"CSV file saved to: {output_file}")

def csv_reader(input_file):
    """    Read data from a CSV file and return lists of times, delta times, counts, and errors.

    Parameters:
    input_file: Path to the CSV file to read

    Returns:
    times: List of times in UTC format
    delta_times: List of delta times in seconds
    counts: List of total counts
    errors: List of total errors
    """

    times, delta_times, counts, errors = [], [], [], []
    
    input_file = Path(input_file)
    
    with open(input_file, mode="r", newline="") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        
        for row in reader:
            # Parse each column
            times.append(row[0])  # Time in ISO format
            delta_times.append(row[1])
            counts.append(float(row[2]))
            errors.append(row[3])

    return times, delta_times, counts, errors
