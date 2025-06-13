# Demonstration of sunkit-spex
Demonstration of the development version of sunkit-spex, a Python package for solar X-ray spectroscopy

#### Sunkit-spex is currently under active development and does not yet have a stable release version.

There are currently two versions of sunkit-spex, the legacy and the development version. 

The legacy version has more functionality than the development version, however is no loger supported due to active work on the development version which has adopted a new API. The development version is based around the Astropy model class API and supports fitting with both the Astropy and Scipy fitting frameworks. 

This demonstration is intended to display the progress made on the sunkit-spex development version, and currently relies on a custom fork of both astropy and sunkit-spex. 

## Usage

You can run the Jupyter Notebooks either on the project's JupyterHub server or locally on your computer. If you are new to Jupyter Notebooks, the official documentation will give you more info about [What is the Jupyter Notebook?](https://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/What%20is%20the%20Jupyter%20Notebook.html) and [Running Code](https://jupyter-notebook.readthedocs.io/en/stable/examples/Notebook/Running%20Code.html) with it.

### On SOLER's JupyterHub

You can run the Notebooks online on SOLER's JupyterHub (more info at [soler-horizon.eu/hub](https://soler-horizon.eu/hub)). For this you only need a [free GitHub account](https://github.com/signup) for verification. There, open the *.ipynb* files within the separate folders for the specific tools.

### Locally

#### Install locally

1. These tools require a recent Python (>=3.10) installation. [Following SunPy's approach, we recommend installing Python via miniforge (click for instructions).](https://docs.sunpy.org/en/stable/tutorial/installation.html#installing-python)
2. [Download this file](https://github.com/soler-he/MSc-course-2025/archive/refs/heads/main.zip) and extract to a folder of your choice (or clone the repository [https://github.com/soler-he/sunkit-spex_demo/](https://github.com/soler-he/sunkit-spex_demo/) if you know how to use `git`).
3. Open a terminal or the miniforge prompt and move to the directory where the code is.
4. Create a new virtual environment (e.g., `conda create --name sunkit-spex python=3.12`).
5. Activate the just created virtual environment (e.g., `conda activate sunkit-spex`).
6. If you **don't** have `git` installed (try executing it), install it with `conda install conda-forge::git`.
7. Install the Python dependencies from the *requirements.txt* file with `pip install -r requirements.txt`

#### Use locally

Activate the created virtual environment in the terminal (step 5. of [Install locally](#install-locally)), go to the folder where the tools have been extracted to, and run `jupyter-lab`. This will open the default web-browser. There, open the *.ipynb* files within the separate folders for the specific tools.
