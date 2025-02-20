from bayes_opt import BayesianOptimization
from utils import objective_function
from functools import partial

# Define the parameter space for chunk sizes
pbounds = {
    'lev': (1, 12),
    'lat': (90, 640),
    'lon': (43, 180)
}

fname="/nfs3m/css/curated01/g5nr/data/Ganymed/7km/c1440_NR/DATA/0.0625_deg/inst/inst30mn_3d_T_Nv/Y2006/M06/D15/c1440_NR.inst30mn_3d_T_Nv.20060615_2330z.nc4"
resultsfile = "results.csv"
obj_func = partial(objective_function, fname=fname, resultsfile=resultsfile)

# Initialize Bayesian optimization
optimizer = BayesianOptimization(
    f=obj_func,
    pbounds=pbounds,
    random_state=1
)

# Perform the optimization (you can adjust n_iter for more iterations)
optimizer.maximize(
    init_points=7,  # Number of random initialization points
    n_iter=25,      # Number of optimization iterations
)

# Print the best result
print("Best chunk sizes:")
print("Elevation chunk size:", int(optimizer.max['params']['lev']))
print("Latitude chunk size:", int(optimizer.max['params']['lat']))
print("Longitude chunk size:", int(optimizer.max['params']['lon']))
print("Best combined score (file size, vertical and spatial mean times):", optimizer.max['target'])


