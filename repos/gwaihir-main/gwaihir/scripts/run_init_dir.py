#!/usr/bin/python
import shutil
import sys
import ast
import glob
import inspect
import gwaihir.utilities as gutil

"""
Python script to move file from datadir to folder where it will be used by preprocess.bcdi
Also initializes all the folders and the rotate the data if beamline is SixS
    Arg 1: Data directory
    Arg 2: Path of target directory (e.g. Pt_Al2O3/) in which the
        results are saved (subdirectories will be updated/created)
    Arg 3: Scan number, e.g. 1325
    Arg 4: Sample name, e.g. S
"""

# Print help
try:
    print('Data dir:',  sys.argv[1])
    print('Root folder:',  sys.argv[2])
    print('Scan:',  sys.argv[3])
    print('Sample name:',  sys.argv[4])

    data_dir = sys.argv[1]
    root_folder = sys.argv[2]
    scan = sys.argv[3]
    sample_name = sys.argv[4]

except IndexError:
    print("""
        Arg 1: Data directory
        Arg 2: Path of target directory (e.g. Pt_Al2O3/) in which the
            results are saved (subdirectories will be updated/created)
        Arg 3: Scan number, e.g. 1325
        Arg 4: Sample name, e.g. S
        """)
    exit()

scan_name = sample_name + str(scan)

gutil.init_directories(
    scan_name=scan_name,
    root_folder=root_folder,
)

gutil.find_move_sixs_data(
    scan=scan,
    scan_name=scan_name,
    root_folder=root_folder,
    data_dir=data_dir,
)
