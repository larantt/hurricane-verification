### Python Library to help with Tropical Cyclone track data

TropCy -- contains all the source code  
format_converters -- currently contains single converter for cxml data to atcf adecks  
    -standalone_converter  -- compiled version for linux system  
test_data  -- example cxml file and output adeck  

To convert cxml file to adecks  
`python format_converters/cxml2atcf.py test_data/z_tigge_c_ecmf_20140905120000_ifs_glob_prod_all_glo.xml`

### Edited: Lara Tobias-Tarsh (20th Feb 2023)
Added functionality to parse to .csv and added headers to each csv file.
Now parses a cyclone xml file to a .csv for each individual cyclone at each time.

Currently only has options for the most basic tags but tags could be extended for further
variables if need be.

To run: enter command
'''
python cxml_decode.py z_tigge_c_ecmf_20140912000000_ifs_glob_prod_all_glo.xml
'''



 
