# CLIMATE 323 PROJECT LOG
Lara Tobias-Tarsh, Nick Dewhirst, Claire Sheeren, Ryan Pohlman
Google Drive: https://drive.google.com/drive/folders/1PdQvzxRMCL0q9U4QIkF02pyXJhxSnXBe?usp=sharing
## TO DO:
### add to file: 
* RSME function
* Along-track and cross-track error
* Fourier transform code of TC track error data
* Make sure all CSVs for the storm get read in
* Add download bash script with directory organisation

## Git and GitHub
I have no clue how to use the git GUI, but here is a pretty comprehensive guide on command line git:
https://eecs280staff.github.io/tutorials/setup_git.html#create-a-local-repository (skip create and go to workflow)
I would at least initialise and install Git.

You can always just download the zip file for the current code versions using the green 'code' block
in the upper right corner if you don't want to do all the pulling and pushing stuff.

## Dependencies:
### TropCy:
* pandas, numpy
### General:
* pandas, numpy, matplotlib, xarray, hurdat2parser, metpy, scipy

Either create a conda environment in terminal:
```
$ conda install nb_conda_kernels    # this lets you use jupyter notebooks with the environment
$ conda create -n climate323final python=3.11 pandas numpy matplotlib xarray metpy, scipy, ipykernel
```
Or pip install it:
```
$ pip install pandas numpy matplotlib xarray metpy, scipy
```
I think whatever happens you will need to pip install the hurdat2parser
```
$ pip install hurdat2parser
```

I also included a .yml file with all of my anaconda environment variables:
```
$ conda env create -f tcVerification.yml
```

## Data Sources:
### THORPEX TIGGE TC Tracks
* THORPEX Grand Global Ensemble contains model TC track and intensity information
* Stored in cyclone XML format (more info: http://www.bom.gov.au/cyclone/cxmlinfo/index.shtml)
* Best access through the UCAR RDA archive - will require account registration
    - https://rda.ucar.edu/datasets/ds330.3/
    - a download script which prompts an RDA login should be included soon (see above)
### HURDAT2
* Observed TC tracks for Atlantic and NE + NC Pacific from the National Hurricane Centre for 1851 - ongoing
* .txt file containing comma-delimited, text format with 6hr location, maximum winds + central pressure
    - Atlantic Hurricanes: https://www.nhc.noaa.gov/data/hurdat/hurdat2-1851-2021-100522.txt
    - NE/NC Pac Hurricanes: https://www.nhc.noaa.gov/data/hurdat/hurdat2-nepac-1949-2021-091522.txt
* Need to download the whole file and then store locally to use with the parser library (soooo much easier)

## Progress Log:
* 20th Feb 2023 -- modified TropCy to parse to .csv files instead of .dat, added header to file
* 21st Feb 2023 -- initial git push, included example parsed files
* 15th March 2023 -- cyclone objects completed and mostly tested


