## Python Library to help with Tropical Cyclone track data

TropCy -- contains all the source code  
format_converters -- currently contains single converter for cxml data to atcf adecks  
    -standalone_converter  -- compiled version for linux system  
test_data  -- example cxml file and output adeck  

To convert cxml file to adecks  
`python format_converters/cxml2atcf.py test_data/z_tigge_c_ecmf_20140905120000_ifs_glob_prod_all_glo.xml`

## Edited: Lara Tobias-Tarsh (20th Feb 2023)
Added functionality to parse to .csv and added headers to each csv file.
Now parses a cyclone xml file to a .csv for each individual cyclone at each time.

Currently only has options for the most basic tags but tags could be extended for further
variables if need be.

To run test: enter in terminal
```
$ python cxml2atcf.py /path/to/z_tigge_c_ecmf_20140912000000_ifs_glob_prod_all_glo.xml
```
or more generally:
```
$ python cxml2atcf.py /path/to/file/
```

Example output data can be found for Atlantic TC Isaac (2006) at\n
Isaac-al-09-2006.csv

I also included a month of data from 2006 in a seperate repository for further testing.

Note that the storm name will be contained in the filename and not in the dataframe for redundancy, but this can be changed with some basic edits to the code.

 ### File Variables:
 * **Basin**: NHC code for ocean basin
 * **Number**: Warning centre assigned invest number (e.g. invest 90L)
 * **Time**: Forecast initialisation (YYYY-MM-DD-HH)
 * **tech**: ngl I have no clue but it doesn't matter
 * **model**: the model used. Full code = ensemble mean, numbers = ensemble member
    - ECMF: European Centre for Medium Range Forecasting
    - 
