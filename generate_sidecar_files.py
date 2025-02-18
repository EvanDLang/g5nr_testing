from pathlib import Path
import argparse
import os
import xarray as xr
from virtualizarr import open_virtual_dataset
from joblib import Parallel, delayed
import glob
from tqdm import tqdm

times = ['0000z', '0030z', '0100z', '0130z', '0200z', '0230z', '0300z', '0330z', '0400z', '0430z', '0500z', '0530z', '0600z', '0630z', '0700z', '0730z', '0800z', '0830z', '0900z', '0930z', '1000z', '1030z', '1100z', '1130z', '1200z', '1230z', '1300z', '1330z', '1400z', '1430z', '1500z', '1530z', '1600z', '1630z', '1700z', '1730z', '1800z', '1830z', '1900z', '1930z', '2000z', '2030z', '2100z', '2130z', '2200z', '2230z', '2300z', '2330z']

def virtualize(pattern, nworkers=-1):
    vds = {}
    for t in tqdm(times):
        files = sorted(glob.glob(str(pattern / f"*{t}.nc4")))
        temp = Parallel(n_jobs=nworkers)(delayed(open_virtual_dataset)(str(fname), loadable_variables=['time'],indexes={}) for fname in files)
        dt = temp[0].time.values[0]
        temp = xr.merge([t.drop_vars('time') for t in temp], compat="override")
        vds[dt] = temp
    print("Concatenating This can take some time!")    
    vds = xr.concat(list(vds.values()), compat="override", coords='minimal', dim='time').assign_coords({"time": list(vds.keys())})
    return vds

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog = "create.py",
            description = "Create parquet references from remote (S3) GOES files"
    )
    
    parser.add_argument("-v", "--variable", type=str, default="*")
    parser.add_argument("-m", "--month", type=int)
    parser.add_argument("-d", "--day", type=int)
    parser.add_argument("-y", "--year", type=int)
    parser.add_argument("-w", "--nworkers", type=int, default=-1)

    argv = parser.parse_args()

    variable = argv.variable
    year = argv.year
    month = argv.month
    day = argv.day

    nworkers = argv.nworkers

    basepath = Path("/nfs3m/css/curated01/g5nr/data/Ganymed/7km/c1440_NR/DATA/0.0625_deg/inst")

    print(f"Parsing files for {year=}, {month=}, {day=}")
    
    pattern = basepath / variable / f"Y{year}"/ f"M{month:02d}"/  f"D{day:02d}"

    output = virtualize(pattern, argv.nworkers)
    print("Generating Sidecar Parquet File. This can take some time!")
    outfile = Path("combined") / f"Y{year}-M{month:02d}-D{day:02d}.parq"
    outfile.parent.mkdir(exist_ok=True, parents=True)
    output.virtualize.to_kerchunk(outfile, format="parquet")

