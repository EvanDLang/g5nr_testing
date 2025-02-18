import os
import re
import pandas as pd
import fastparquet
from tqdm import tqdm
import shutil
import requests


def change_paths(root_file_dir, pattern=r"(/nfs3m/css/curated01/g5nr/data/Ganymed/7km/c1440_NR)", updated_root="https://g5nr.nccs.nasa.gov/data", test_updates=True)
    # root_file_dir = "combined/Y2006-M01-D01.parq"

    root, ext = os.path.splitext(root_file_dir)
    dst_dir = f"{root}_https{ext}"
    
    # pattern = r"(/nfs3m/css/curated01/g5nr/data/Ganymed/7km/c1440_NR)"
    # updated_root = "https://g5nr.nccs.nasa.gov/data"
    
    path_mapping = {}
    
    if not os.path.exists(dst_dir):
        shutil.copytree(root_file_dir, dst_dir)
    
    # for entry in os.listdir(comb):
        # entry_path = os.path.join(root_file_dir, entry)
        # print(entry)
    for root, dirs, files in os.walk(root_file_dir):
        for file in files:
            if file.endswith('.parquet') or file.endswith('.parq'):
                path = os.path.join(root, file)
                df = pd.read_parquet(path)
                paths = df['path'].dropna().unique()
    
                for p in paths:
                    if 'https' in p:
                        continue
                    match = re.search(pattern, p)
                
                    if match:
                        new_path = p.replace(match.group(1), updated_root)
                        if test_updates:
                            if requests.head(new_path).status_code==200:
                                path_mapping[p] = new_path
                            else:
                                raise Exception(f" {new_path} Does not exist in {updated_root}")
                        else:
                            path_mapping[p] = new_path
                    else:
                        print(path)
                        raise Exception(f"No match found for: {p}")
             
    # print(path_mapping)    
    # for entry in os.listdir(root_file_dir):
        # entry_path = os.path.join(root_file_dir, entry)
    for root, dirs, files in tqdm(os.walk(dst_dir)):
        for file in files:
            if file.endswith('.parquet') or file.endswith('.parq'):
                path = os.path.join(root, file)
                df = pd.read_parquet(path)
                df['path'] = df['path'].map(path_mapping).fillna(df['path'])
                fastparquet.write(path, df, compression='SNAPPY')