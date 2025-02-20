import numpy as np
import time
import subprocess
import timeit
import warnings
from pathlib import Path
import xarray as xr
import h5py
import re

def run_rechunking(file_path, chunk_size_elevation, chunk_size_lat, chunk_size_lon):
    command = [
        "bash", "rechunk_v2.sh",
        file_path,
        str(chunk_size_elevation),
        str(chunk_size_lat),
        str(chunk_size_lon)
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    
    # Check if the operation was successful
    if result.returncode == 0:
        # Parse the output to get the file size (last line)
        for line in result.stdout.splitlines():
            if "File size" in line:
                file_size = int(line.split(":")[-1].strip().split()[0])  # Extract file size in KB
                return file_size
    else:
        print(f"Error: {result.stderr}")
        return None

def open_with_props(fname):
    props = {"page_size": (8 * 1024 * 1024)}
    return xr.open_dataset(h5py.File(
        str(fname),
        mode="r",
        page_buf_size = props["page_size"]
    ), engine="h5netcdf")

def do_open(fname):
    with open_with_props(Path(fname)) as _:
        pass

def do_subset_vertical_mean(fname):
    with open_with_props(Path(fname)) as ds:
        ds.T.isel(lat=slice(1200,1305),lon=slice(3438, 3689)).mean(('lon', 'lat')).compute()

def do_spatial_1_vertical(fname):
    with open_with_props(Path(fname)) as ds:
        ds.T.isel(lev=20).mean().compute()

def writeline(fname: Path|str, stuff: list, columns: str) -> None:

    file_exists = fname.exists()

    with open(fname, "a" if file_exists else "w") as of:
        if not file_exists:
            of.write(f"{columns}\n")
        
        linestring = ",".join([str(s) for s in stuff]) + "\n"
        of.write(linestring)

def run_benchmarks(fname, number=40):
    vertical_mean = timeit.timeit(f'do_subset_vertical_mean("{fname}")', globals=globals(), number=number) / number
    spatial_mean = timeit.timeit(f'do_spatial_1_vertical("{fname}")', globals=globals(), number=number) / number

    return vertical_mean, spatial_mean

def objective_function(fname, resultsfile, lev, lat, lon):
    lev = int(lev)
    lat = int(lat)
    lon = int(lon)
   
    file_size = run_rechunking(fname, lev, lat, lon)
    
    vertical_mean, spatial_mean = run_benchmarks(f"experiments/chunked-1x{lev}x{lat}x{lon}.nc")

    # these are hard coded values from previous runs on the original, needs to be added
    file_size_ratio = file_size / 897024
    vertical_mean_ratio = vertical_mean / (16.39718712697504 / 40)
    spatial_mean_ratio = spatial_mean / (15.767129378014943 / 40)

    # we are trying to minimize everything so we want a negative score, 
    # here I add the two benchmarks together and multiple them by negative filesize
    # I can add weights to each benchmark as well
    combined_score = -file_size_ratio * (vertical_mean_ratio + spatial_mean_ratio)

    writeline(Path(resultsfile), 
              [f"chunked-1x{lev}x{lat}x{lon}.nc", file_size, file_size_ratio, vertical_mean, vertical_mean_ratio, spatial_mean, spatial_mean_ratio, combined_score],
              "file_name,file_size,file_size_ratio,vertical_mean,vertical_mean_ratio,spatial_mean,spatial_mean_ratio,combined_score"
             )
    
    return combined_score
