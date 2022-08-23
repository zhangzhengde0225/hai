#!/bin/bash -l
#SBATCH --partition=p9gpu
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=2
#SBATCH --ntasks=4
#SBATCH --gres=gpu:2
#SBATCH --time=01:00:00
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=4G
#SBATCH --output=%x-%j.out
#SBATCH --export=NONE

# Script is launched like this:
# job_esrf.slurm gui simonne /data/id01/inhouse/david/SIXS_June_2021/reconstructions/25/Air/B-7/S3116/preprocessing/ true 10

# Arguments needed
reconstruct=$1         # if launched via the gui or terminal
username=$2    # username, if not specified, default to simonne
path=$3      # pynxraw directory with npz files and pynx_run.txt file
modes=$4       # if running modes analysis or not, in that case, run strain
filtering=$5   # if applying standard deviation filter, should be an integer number, less than n_run

echo "################################################################################################################"
echo "Reconstruct data via: " $reconstruct
echo "Username: " $username
echo "Working directory: " $path
echo "Running modes decomposition: " $modes
echo "Filtering reconstructions: " $filtering
echo "################################################################################################################"

env | grep CUDA
scontrol --details show jobs \$SLURM_JOBID |grep RES

# echo `date`  | mail -s " SLURM JOB $SLURM_JOBID has started" <YOUR-EMAIL>

# Moving to pynxraw directory
cd $path
echo "Moved to " $path
# source /data/id01/inhouse/david/p9.stable/bin/activate
# echo "Working with /data/id01/inhouse/david/p9.stable/ environment"

# Running phase retrieval
echo 
echo "################################################################################################################"
echo "Running phase retrieval with PyNX ..."
echo "################################################################################################################"
echo 

## GUI
if [[ $reconstruct = "gui" ]]; then
    echo "################################################################################################################"
    echo "Loading pynx_run_gui.txt arguments..."
    echo "/data/id01/inhouse/david/p9.stable/bin/pynx-id01cdi.py pynx_run_gui.txt |& tee README_pynx_gui.md"
    mpiexec -n $SLURM_NTASKS /data/id01/inhouse/david/p9.stable/bin/pynx-id01cdi.py pynx_run_gui.txt |& tee README_pynx_gui.md

    # Moving the results in gui_run/ sub-directory
    echo "Creating a subdirector gui_run/ and moving all the .cxi files there..."
    mv S*LLK*.cxi gui_run/
    mv README_pynx_gui.md gui_run/
    cd gui_run/
    echo "################################################################################################################"
    echo

## Terminal
elif [[ $reconstruct = "terminal" ]]; then
    echo "################################################################################################################"
    echo "Loading pynx_run.txt arguments..."
    echo "/data/id01/inhouse/david/p9.stable/bin/pynx-id01cdi.py pynx_run.txt |& tee README_pynx_terminal.md"
    mpiexec -n $SLURM_NTASKS /data/id01/inhouse/david/p9.stable/bin/pynx-id01cdi.py pynx_run.txt |& tee README_pynx_terminal.md

    # Moving the results in terminal_run/ sub-directory
    echo "Creating a subdirector terminal_run/ and moving all the .cxi files there..."
    mkdir terminal_run/
    mv S*LLK*.cxi terminal_run/
    mv README_pynx_terminal.md terminal_run/
    cd terminal_run/
    echo "################################################################################################################"
    echo
fi

# Does not exist anymore
# if [[ $filtering == ?(-)+([0-9]) ]]; then # Verify that it is an integer
#     # Apply a standard deviation filter
#     echo "Applying a standard deviation filter"
#     run_std_filter.py $filtering
# fi

if [[ $modes = true ]]; then
    echo "################################################################################################################"
    echo "Running modes decomposition ..."
    echo "/data/id01/inhouse/david/p9.stable/bin/pynx-cdi-analysis.py *LLK* modes=1 modes_output=modes.h5 |& tee README_modes.md"
    /data/id01/inhouse/david/p9.stable/bin/pynx-cdi-analysis.py *LLK* modes=1 modes_output=modes.h5 |& tee README_modes.md
    echo "################################################################################################################"
    echo

    if [[ $reconstruct = "terminal" ]]; then
        # Nothing here yet
        echo "################################################################################################################"
        echo "Running strain analysis"
        # ssh username@rnice9 << EOF
        #     cd $1
        #     run_strain.py $2 $3
            
        #     echo "Strain.py is running ..."
            
        #     exit

        # EOF
        echo "########################################################"
        echo

    fi
fi

# echo `date`  | mail -s " SLURM has finished job: $SLURM_JOBID !! " <YOUR-EMAIL>
