#!/bin/bash
#SBATCH --job-name=G5nr_sidecar_creation
#SBATCH --output=output_%j.log
#SBATCH --error=error_%j.log
#SBATCH --constraint=mil
#SBATCH --constraint=cssro
#SBATCH --account=s2826
#SBATCH --time=01:00:00

year=2006

declare -A days_in_month

days_in_month=(
    [1]=31   # January
    [2]=28   # February 
    [3]=31   # March
    [4]=30   # April
    [5]=31   # May
    [6]=30   # June
    [7]=31   # July
    [8]=31   # August
    [9]=30   # September
    [10]=31  # October
    [11]=30  # November
    [12]=31  # December
)

source /gpfsm/dhome/edlang1/.bashrc

pixi shell

for month in {1..12}; do
    for day in $(seq 1 ${days_in_month[$month]}); do
        echo "Year:$year Month:$month Day:$day"
        python generate_sidecar_files.py -y $year -m $month -d $day
    done
done
