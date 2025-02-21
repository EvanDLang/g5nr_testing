# g5nr_testing
Time to generate sidecar files for 1 day: 69m49.437s

## Setup

This uses the [`pixi` package manager](https://pixi.sh/latest/).
To get a shell with all dependencies automatically installed and loaded, run `pixi shell`.

Alternatively, you can run individual scripts with `pixi run python <script.py>`.

If you want to install dependencies manually, refer to the `pyproject.toml` file.

To run create.py see the slurm script (slurm.sh)

Before submitting the script:
- Update the path to your own bashrc file
- Run pixi shell in you local terminal

## Generating Sidecar Files
The sidecar generation script can be ran from the commandline. The user must provide the year, month and day. This will generate a sidecar file for one day with all the variables found in /nfs3m/css/curated01/g5nr/data/Ganymed/7km/c1440_NR/DATA/0.0625_deg/inst

```python
python generate_sidecar_files.py -y 2006 -m 1 -d 10
```

## Changing File Paths to HTTPS

The filepaths in the sidecar files can be update to https paths with the change_paths function. The function will create a copy of the target parquet directory and will use a pattern to update filepaths.

The default arguments look for /nfs3m/css/curated01/g5nr/data/Ganymed/7km/c1440_NR and replace it with https://g5nr.nccs.nasa.gov/data.

The function can also ping each updated https path to make sure that it is valid by setting test_paths to True, This cannot be done on a Discover Node though.

```python
from change_paths import change_paths

change_paths(
    <path_to_parquet_directory>,
    pattern=r"(/nfs3m/css/curated01/g5nr/data/Ganymed/7km/c1440_NR)", 
    updated_root="https://g5nr.nccs.nasa.gov/data", 
    test_updates(True | False)
    )
```

## Bayesian Optimization

This branch has code to run bayseian optimization in an attempt to find chunksizes that minimize the provided benchmarks. In the optimization directory, the run optimization script can be used. If you would like to expand the search, pbounds can be updated. Also, increasing iter_points and n_iters can be used to run the process for longer.

```python
python run_optimization.py
```