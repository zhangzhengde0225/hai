#/usr/bin/bash
# Use as follows:
#     Arg 1: Data directory
#     Arg 2: Path of target directory (e.g. Pt_Al2O3/) in which the
#         results are saved (subdirectories will be updated/created)
#     Arg 3: Scan number, e.g. 1325
#     Arg 4: Sample name, e.g. S

# You should have the following files in your working directory
# 	config_preprocessing.yml
# 	pynx-run.txt
# 	config_postprocessing.yml

# This file is just here to provide an idea on to how a command line workflow
# would work. However make sure to separate your workflow to make sure that
# your reconstruction_file is of good quality.

echo "##################################################################"
echo "Remember to source your virtual environment"
echo "##################################################################"

echo "##################################################################"
echo "Moving scan to new directory and touching new directories..."
echo run_init_dir.py $1 $2 $3 $4
echo "##################################################################"

echo "##################################################################"
echo "Preprocessing scan..."
echo bcdi_preprocess_BCDI.py --config config_preprocessing.yml --scans $3 --root_folder $2$3/data --save_dir $2$4$3/preprocessing
echo "##################################################################"
bcdi_preprocess_BCDI.py --config config_preprocessing.yml \
	--scans $3 \
	--root_folder $2$3/data \
	--save_dir $2$4$3/preprocessing

# echo "##################################################################"
# echo "Ready to launch phase retrieval with slurm!"
# echo run_slurm_job.sh --reconstruct gui --username simonne --path $2S$3/preprocessing --filtering 20 --modes true
# echo "##################################################################"

echo "##################################################################"
echo "Ready to launch phase retrieval!"
echo pynx-id01cdi.py pynx-run.txt
echo "##################################################################"
# Use filtering method from gwaihir.utilities.filter_reconstructions if needed

echo "##################################################################"
echo "Postprocessing scan..."
echo bcdi_strain.py --scans $3 --root_folder $2$3/data --save_dir $2S$3/preprocessing --data_dir $2S$3/data  --config_file config_postprocessing.yml --reconstruction_file "path\to\solution"
echo "##################################################################"
bcdi_strain.py --config_file config_postprocessing.yml \
	--scans $3 \
	--root_folder $2$3/data \
	--save_dir $2S$3/preprocessing \
	--data_dir $2S$3/data \
	--reconstruction_file "path\to\solutionfile"
