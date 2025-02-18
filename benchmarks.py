#!/usr/bin/env python

import timeit
import warnings
from pathlib import Path
import xarray as xr
import h5py
import re

# def writeline(fname: Path|str, stuff: list) -> None:
#     linestring = ",".join([str(s) for s in stuff]) + "\n"
#     with open(fname, "a") as of:
#         of.write(linestring)


def writeline(fname: Path|str, stuff: list) -> None:

    file_exists = fname.exists()

    with open(fname, "a" if file_exists else "w") as of:
        if not file_exists:
            of.write("filename,open,vertical_mean,spatial_mean\n")
        
        linestring = ",".join([str(s) for s in stuff]) + "\n"
        of.write(linestring)


def parse_fname(fname):
    # fname = Path("experiments/e5303_m21c_jan18.aer_inst_1hr_glo_C360x360x6_v72.2018-01-31T0000Z/cNone_p1048576.nc4")
    stem = fname.stem
    m = re.match(r"c(.*?)_p([0-9]+)", stem)
    if not m:
        raise ValueError(f"Invalid file name: {fname}")
    chunking = m.group(1)
    if chunking == "None":
        chunking = None
    psize = m.group(2)
    if psize == "None":
        psize = None
    else:
        psize = int(psize)
    return {"chunking": chunking, "page_size": psize}

def open_with_props(fname):
    # props = parse_fname()
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

if __name__ == "__main__":
    experiment_dir = Path("experiments")
    fnames = sorted(experiment_dir.glob("*.nc"))
    resultfile =  experiment_dir / "chunk-size.csv"
    # fname = experiment_dir / "chunked-1x2x67x120.nc"
    # fnames = [experiment_dir / fname for fname in ["chunked-1x2x67x160.nc", "chunked-1x2x67x144.nc", "chunked-1x2x121x192.nc", "chunked-1x2x144x240.nc"]]
    for fname in fnames:
        print(fname)
        # Note: Ignore xarray duplicate dimension warnings...
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            topen = timeit.timeit(f'do_open("{fname}")', globals=globals(), number=40)
            ttimeseries = timeit.timeit(f'do_subset_vertical_mean("{fname}")', globals=globals(), number=40)
            tspatial = timeit.timeit(f'do_spatial_1_vertical("{fname}")', globals=globals(), number=40)
        writeline(resultfile, [fname.stem, topen, ttimeseries, tspatial])
