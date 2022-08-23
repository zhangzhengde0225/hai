import setuptools

with open("./gwaihir/README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gwaihir",
    version="0.0.4",
    description="Python package for BCDI data analysis",
    author="David Simonne",
    author_email="david.simonne@universite-paris-saclay.fr",
    download_url="https://pypi.org/project/gwaihir/",
    data_files=[('', ["licence.txt",
                      "gwaihir/scripts/examples/config_postprocessing_sixs.yml",
                      "gwaihir/scripts/examples/config_preprocessing_sixs.yml",
                      "gwaihir/scripts/examples/config_postprocessing_P10.yml",
                      "gwaihir/scripts/examples/config_preprocessing_P10.yml",
                      ])],
    url="https://github.com/DSimonne/gwaihir/tree/master",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    scripts=[
        "gwaihir/scripts/run_init_dir.py",
        "gwaihir/scripts/job_esrf.slurm",
        "gwaihir/scripts/run_slurm_job.sh",
        "gwaihir/scripts/plot_paraview_slices.py",
        "gwaihir/scripts/workflow_cli.sh",
    ],
    keywords=["BCDI", "ipywidgets", "PyNX"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=[
        "numpy",
        "pandas",
        "datetime",
        "argparse",
        "matplotlib",
        "ipywidgets",
        "ipython",
        "ipyvolume",
        "ipyfilechooser",
        "scipy",
        "xrayutilities",
        "tables",
        "h5glance",
        "PyQt5",
        "h5py",
        "jupyter",
        "bokeh",
        "panel",
    ]
)
