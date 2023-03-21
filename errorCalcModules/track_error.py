"""
CREATED: 13/03/2023
AUTHOR: Lara Tobias-Tarsh (laratt@umich.edu)

Summary: Module to calculate TC track and intensity error using IBTrACs and TIGGE data.
Contains a custom parser, functions for calculation of track error and intensity error.

Should act like a wrapper for all data so that instead of reading every file in storm by storm
You just list a directory containing TIGGE files and call a function to generate a dictionary
Of objects containing all the data necessary for processing TC track.

References:

TO DO:
Add ensemble data class (not for 323)
Implement functions (pseudocode in place)
How to initialise track error...
Jupyter notebook tutorial on how to access attributes of a cyclone
"""
# Imports
from dataclasses import dataclass, field
import datetime as dt
import os # if i cba to fix the directory structures dependencies lol
from typing import List
from math import asin, cos, radians, sin, sqrt
import numpy as np
import hurdat2parser

#############
## GLOBALS ##
#############

# fill out with the models you intend to use
MEMBERS = ['EMCF','GEFS']

# path to hurdat2 file
ATL = hurdat2parser.Hurdat2('errorCalcModules/HURDAT2.txt')

###############
## FUNCTIONS ##
###############
def extract_position_data(filepath):
    """ Helper for position function

    Reads in csv file containing TIGGE data. Parses for use in a Position object.
    Probably used by listing filepaths within larger Cyclone constructor.
    Uses np.genfromtext() for class usability. Future versions could implement a 
    custom csv reader in base python for speed. Good for real time applications.

    Parameters
    ----------
        filepath : str
            path to csv file
    
    Returns
    -------
        time : dt.datetime 
            time of forecast
        coords : tuple 
            Tuple containing latitude and longitude data (lat,lon)
        mslp : float 
            Mean Sea Level Pressure at TC centre
        vmax :float 
            Maximum sustained windspeed
    
    Note that these variables are stored in a list
    """
    # convert to datetime
    tconvert = lambda x: dt.datetime.strptime(str(x), '%Y%m%d%H')
    # read in file w genfromtext, use headers, skip whitespace, time = %Y%m%d%H
    np.genfromtxt(fname=filepath,delimiter=',',converters={2:tconvert})
    # find index of ensemble member in df['model']
    # generate list of forecast hours in df['forecastHr']
    # iterate through forecast hours and extract variables
    # Construct a Position
    # Calculate track error
    # Calculate intensity error
    # return list of Forecasts
    pass

def parse_hurdat(name,year):
    """ Default constructor for HURDAT2 best track data
    
    Uses the HURDAT2 parser python module to generate a best track for 
    a TC object from the HURDAT2 database. This requires you to have the 
    HURDAT2.txt file in your directory and the HURDAT2 parser installed.
    If you run the yaml file install (see README), then it should install
    via pip, although it isn't included. If not run:

    pip install hurdat2parser in your laptop's command line

    Parameters
    ----------
        name : string
            NHC assigned cyclone name, parsed from cxml filename
        year : string
            Year of cyclone, parsed from cxml filename

    Returns
    --------
        best_track : Track
            Track object containing best track data

    """
    # Open HURDAT2.txt
    # Generate tupled coord list: ATL[str(year)][str(name)].gps
    # store in list
    # return list
    pass

def generate_cyclone(dir_list):
    """ Function initialises a cyclone object from a list of csvs

    Iterates through a list of csv files in a directory and constructs a
    cyclone object. Generates variables by parsing the name of the file.
    Requires following modified TropCy naming conventions. 
    Each TC's csv files should be contained in its own directory:
    e.g. ~/cyclones/Isaac-2006/

    Parameters
    ----------
        Name : string
            NHC assigned cyclone name
        bestTrack : Track 
            HURDAT2 best track

    Returns
    -------
        storm : Cyclone
            Cyclone object for storm in directory
    """
    # open first csv in directory
    # extract storm name and year from file
    # create best track object with parse_hurdat()
    # For file in list:
    #   Index in and get model
    #   tracks = Default construct Track()
    #   [for forecast in tracks calculate track error, intensity error]
    #   run = tracks
    #   if model == gfs:
    #        append run to gfs list
    #   if model == ecmf:
    #       append to ecmf list
    # default construct cyclone object
    pass

#############
## CLASSES ##
#############

@dataclass
# Initialse a best track as purely a track of positions
class Position:
    """ TC object containing positional and intensity information

    Base class containing all positional and intensity information for a given forecast hour.
    Valid for best tracks and forecast objects.

    Attributes
    -----------
        time : dt.datetime
            UTC time associated with forecast member.
        lat : float
            Latitude of TC centre
        lon : float
            Longitude of TC centre
        mslp : float
            Mean Sea Level Pressure at TC centre
        vmax : float
            Maximum sustained windspeed
    """
    time: dt.datetime
    lat: float
    lon: float
    mslp: float
    vmax: float

    # function to get haversine distacne as a class member?
    def great_circle(self, other):
        """ Calculates great circle distance between two points using the haversine formula
        
        Generally used to calculate the track error, but useful to have as an attribute as
        this can be used to calculate distances between storms and so could be helful
        for investigating other TC interactions such as the Fujiwhara effect.
        
        Parameters
        ----------
        self : Position
            Existing Position object containing latitude and longitude information
        other : Position
            Position object containing latitude and longitude information

        Returns
        --------
        gcd : float
            Great circle distance between two Position objects

        """
        radius = 6371  # Earth radius in kilometers
        lam_1, lam_2 = radians(self.lon), radians(other.lon)
        phi_1, phi_2 = radians(self.lat), radians(other.lat)
        h_inside = (sin((phi_2 - phi_1) / 2)**2
             + cos(phi_1) * cos(phi_2) * sin((lam_2 - lam_1) / 2)**2)
        gcd = 2 * radius * asin(sqrt(h_inside))
        return gcd
    
    # function for intensity error
    def intensity_error(self, other):
        """Calculates intensity difference between two TCs

        Calculates the difference in intensity between the mean sea level pressure (MSLP) 
        at one TC centre and another TC centre.
        Generally used for calculating the intensity error between a modelled TC
        and the TC best track but can be useful for analysing other parameters when
        TC interaction is an important factor therefore is included as an attr.

        Parameters
        ----------
        self : Position
            Existing position object containing central MSLP in mbar
        other : Position
            Position object containing central MSLP in mbar

        Returns
        -------
         : float
            difference in central MSLP between the two systems
        
        """
        return self.mslp - other.mslp


@dataclass
class Forecast(Position):
    """ TC object containing positional and intensity information

    Inhereted class from a position object used for ensemble members.
    Adds data for error calculations at each position.

    Attributes
    ----------
        position : Position 
            Positional data for TC
        track_error : float 
            Great circle distance between modelled TC centre and best track
        intensity_error : float
            Difference in mean sea level pressure between modelled TC centre and best track

    """
    track_error: float = field(init=False)
    intensity_error: float = field(init=False)

    # alternate potential syntax (TEST ME!)
    # track_error: float = field(default_factory=generate_cyclone)
    # intensity_error: float = field(default_factory=generate_cyclone)

    def __post__init__(self,other):
        # don't know if this is even necessary if I am just forcing initialisation in cyclone init.
        #self.track_error = self.great_circle(bestTrack)
        self.intensity_error = self.intensity_error()

        # alternate potential syntax (TEST ME!)
        # self.track_error = generate_cyclone(self,other)
        # self.intensity_error = generate_cyclone(self,other)


@dataclass
class Track:
    """ TC object containing all forecast hours of a track

    Attributes
    -----------
        forecasts : List 
            List of Forecast objects for each point along track
    
    """
    forecasts: List[Position] = field(default_factory=extract_position_data)


@dataclass
# TBC: do we start from best track formation or model detection...?
class Run:
    """ TC object containing full track and error data for each model run

    Class holds each entire forecast for a given lead time. 
    E.g. run1 will be the first time the model detects TC, 
    runN will be the closest run to dissipation time.

    Attributes
    ----------
        tracks : List 
            List of all model generated tracks up to dissipation
        mean_terror : float
            Average track error across whole forecast
        mean_ierror : float 
            Average intensity error across whole forecast
        along_track_bias : float 
            TBA
        cross_track_bias : float 
            TBA

    """
    tracks: List[Track]
    mean_terror: float = field(init=False)
    mean_ierror: float = field(init=False)
    along_track_bias: float = field(init=False)
    cross_track_bias: float = field(init=False)

    def __post__init__(self):
        # add with added functions
        pass


@dataclass
class Model:
    # add functionality to create initial conditions forecast map from model data
    """ TC Object containing all data for a given model

    Class holds all runs from formation to dissipation for a given model ensemble.

    Attributes
    ----------
        runs : Run 
            List of all runs corresponding to model
        brier_skill_score: 
            TBA
    """
    runs: List[Run]
    brier_skill_score: float = field(init=False)

    def brier_skill(self):
        """TBA"""
        return []

    def __post__init__(self):
        self.brier_skill_score = self.brier_skill()


@dataclass
class Cyclone:
    # I want the constructor for this to be just passing a list of files in a directory
    # Should be able to iterate through a list of directories and initialise all Cyclones for season
    """ Main TC object containing all information wrt a TC
    
    Class contains all information that is used in tracking TCs for
    organisational purposes, as well as key TC information that can
    be used as a metric for comparison.

    Attributes
    ----------
        name : str 
            NHC assigned storm name
        ecmwf : Model 
            ECMWF model object
        gfs : Model 
            GFS model object
        number : int 
            Number of storm in season
        formation_date : dt.datetime
            Date of formation in best track
        synoptic_classif : TBA
            TBA - probably user input?
        best_track : List
            List containing best track data
        
    """
    name: str
    ecmwf: Model
    gfs: Model
    #number: int = field(init=False)
    best_track: Track = field(default_factory=parse_hurdat)
    formation_date: dt.datetime = field(init=False)

    def __post__init__(self):
        # Sets formation date to the first time in the best track
        self.formation_date = self.best_track.forecasts[0].time                    

####################
## main() OUTLINE ##
####################
# initialise storm via constructor:
# look for csv for system
# parse into cyclone object

# list directory containing all storms
# initialise the best track
# initialise the track
# initialise the run
# initialise the model
# initialise the Cyclone
# store cyclone in a dictionary

######################
## FUNCTIONS NEEDED ##
######################
# cross-track error
# along-track error
# brier skill score
