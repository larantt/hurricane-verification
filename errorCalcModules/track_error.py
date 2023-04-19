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
import pandas as pd
import hurdat2parser
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib as mpl
import traceback

#############
## GLOBALS ##
#############

# fill out with the models you intend to use
MEMBERS = ['ECMF','GEFS']

# path to hurdat2 file
ATL = hurdat2parser.Hurdat2('/Users/laratobias-tarsh/Documents/clim323-final/errorCalcModules/HURDAT2.txt')

###############
## FUNCTIONS ##
###############

def check_greek_alphabet(name):
    """ Checks if a storm is a greek alphabet storm
    
    Hurdat2Parser.py checks storm entries by first letter
    of the storm only and so will break the best track assignment
    for greek alphabet storms.

    Because the greek alphabet is retired and TIGGE data is not available
    for 2005, which is the only other year it was used, we are safe to
    hardcode these here.

    Parameters
    -----------
    name : string
        storm name
    
    Returns
    -------
    id : string
        unique identifier for storm
    """
    if name == "Alpha" :
        return 'AL242020'
    if name == "Beta" :
        return 'AL222020'
    if name == "Gamma" :
        return 'AL252020'
    if name == "Delta" :
        return 'AL262020'
    if name == "Epsilon" :
        return 'AL272020'
    if name == "Zeta":
        return 'AL282020'
    if name == "Eta":
        return 'AL292020'
    if name == "Theta" :
        return 'AL302020'
    if name == "Iota" :
        return 'AL312020'
    else:
        pass 


def name_from_string(filepath):
    """ Parses name from the TC filepath name
    
    File must follow modified TropCy.py naming convention
    Parameters
    -----------
    filepath : string
        path to file containing TIGGE data

    Returns
    --------
    name : string
        Name of TC
    year : string
        Year of TC
    """
    name = filepath.split('/')[-1].split('-')[0]
    year = filepath.split('/')[-1].split('-')[1]
    return name, year

def parse_hurdat(filepath):
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
    # Generate tupled coord list: ATL[str(year)][str(name)].gps
    name, year = name_from_string(filepath)
    storm = ATL[year][name]
    if name in ["Alpha"  , "Beta" , "Gamma" , "Delta" , "Epsilon" , "Zeta" , "Eta", "Theta" , "Iota" ]:
        storm = ATL[check_greek_alphabet(name)]
    if name == "Teddy":
        storm = ATL["AL202020"]
    best_track = [Position(entry.entrytime,entry.lat,entry.lon,entry.mslp,entry.wind) for entry in storm]
    return best_track
    
def get_errors(best_track,forecast_pos):
    """ Calculates track errors for a TC
    
    Parameters
    -----------
    best_track : Position
        Position object containing HURDAT2 track data
    forecast_pos : Position
        Position object containing ensemble TIGGE data

    Returns
    --------
    t_error : float
        Great circle distance between observations and model data
    i_error : float
        Difference in intensity between observations and model data
    """

    current_time = forecast_pos.time
    for pos in best_track:
        if pos.time == current_time:
            t_error = forecast_pos.trackError(pos)
            i_error = forecast_pos.intensityError(pos)
    return t_error, i_error

        

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
        forecasts : Forecast
            Forecast object containing all assesment metrics for a TC
        model : string
            Name of model being used
    
    Note that these variables are stored in a list
    """
    # read in file, convert datetime, extract ensemble
    try :
        df = pd.read_csv(filepath,skipinitialspace=True)
        ens = df.loc[df.model.isin(MEMBERS)]
        model = ens.model.values[0]
        # Parse filename and use HURDAT2 to get best track
        best_track = parse_hurdat(filepath)
            # iterate through forecast hours and extract variables and waste memory
        positions = [Position((pd.to_datetime(ens.time.values[ix],format='%Y%m%d%H')+pd.DateOffset(hours=int(ens.forecastHr.values[ix]))),
                                ens.lat.values[ix],ens.lon.values[ix],ens.mslp.values[ix],ens.vmax.values[ix]) for (ix,en) in enumerate(ens.time)]
        # Discard times not in best track for sake of simplicity
        bt = Track(best_track)
        positions = [pos for pos in positions if pos.time in bt.return_times()]
        
        forecasts = []
            # Iterate through positions and create forecast objects
        for pos in positions:
            t_e,i_e = get_errors(best_track,pos)
            forecasts.append(Forecast(pos.time,pos.lat,pos.lon,pos.mslp,pos.vmax,t_e,i_e))

            # return list of Forecasts
        return forecasts,model, Track(best_track)
    except:
        pass


def generate_cyclone(dirpath):
    """ Function initialises a cyclone object from a list of csvs

    Iterates through a list of csv files in a directory and constructs a
    cyclone object. Generates variables by parsing the name of the file.
    Requires following modified TropCy naming conventions. 
    Each TC's csv files should be contained in its own directory:
    e.g. ~/cyclones/Isaac-2006/

    Parameters
    ----------
        dirpath : str
            path to directory containing cyclone csvs

    Returns
    -------
         : Cyclone
            Cyclone object for storm in directory
    """
    # For file in list:
    # this is so hacky - need to come up with a better way of making vars on the fly...
    #gfs = []
    ecmf = []
    for filename in sorted(os.listdir(dirpath)):
        print(f'reading file: {filename}')
        name, year = name_from_string(filename)
        try:
            fcasts, model, best_track = extract_position_data(dirpath+"/"+filename)
        except:
            break
        tracks = Track(fcasts)
        if model == "ECMF":
            ecmf.append(tracks)
        #if model == "GFS":
           # gfs.append(tracks)
    try:
        return Cyclone(name,int(year),Model(ecmf),best_track)
    except:
        pass


def colorFader(c1,c2,mix=0):
    """ Fades two matplotlib colors together into a gradient """
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)


#############
## CLASSES ##
#############

@dataclass
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
            Great circle distance between two Position objects in km

        """
        radius = 6371  # Earth radius in kilometers
        lam_1, lam_2 = radians(self.lon), radians(other.lon)
        phi_1, phi_2 = radians(self.lat), radians(other.lat)
        h_inside = (sin((phi_2 - phi_1) / 2)**2
             + cos(phi_1) * cos(phi_2) * sin((lam_2 - lam_1) / 2)**2)
        gcd = 2 * radius * asin(sqrt(h_inside))
        return gcd
    
    def intensityError(self, other):
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
        #real_mslp = [entry for (index,entry) in enumerate(other) if other[index].time == self.time][0]
        return self.mslp - other.mslp
    
    def trackError(self,other):
        """ Calculates a TC track error between one storm and another
        
        Performs a time based indexing scheme then calculates great circle distance
        between two tracks. 

        Parameters
        ----------
        self : Position
            Existing Position object containing latitude and longitude information
        other : Position
            Position object containing latitude and longitude information

        Returns
        --------
         : float
            Track error distance between two Position objects
        """
        # check start time of position object
        #real_position = [entry for (index,entry) in enumerate(other) if other[index].time == self.time][0]
        return self.great_circle(other)


@dataclass
class Forecast(Position):
    """ TC object containing positional and intensity information

    Inhereted class from a position object used for ensemble members.
    Adds data for error calculations at each position.

    Attributes
    ----------
        position : Position (inhereted)
            Positional data for TC
        track_error : float 
            Great circle distance between modelled TC centre and best track
        intensity_error : float
            Difference in mean sea level pressure between modelled TC centre and best track

    """

    track_error: float
    intensity_error: float

@dataclass
class Track:
    """ TC object containing all forecast hours of a track

    Attributes
    -----------
        forecasts : List 
            List of Forecast objects for each point along track
        mean_terror : float
            Average track error across whole forecast
        mean_ierror : float 
            Average intensity error across whole forecast

        ADD AFTER 323 FOR ASSESSING AN ENSEMBLE
        along_track_bias : float 
            TBA
        cross_track_bias : float 
            TBA

    
    """
    forecasts : List[Position] 
    mean_terror: float = field(init=False)
    mean_ierror: float = field(init=False)

     
    def __post_init__(self):
        if type(self.forecasts[0]) == Forecast:
            t_err = i_err = 0
            for i, fcst in enumerate(self.forecasts):
                t_err = t_err + self.forecasts[i].track_error
                i_err = i_err + self.forecasts[i].intensity_error
        
            self.mean_terror = (t_err / len(self.forecasts))
            self.mean_ierror = (i_err / len(self.forecasts))
        else:
            self.mean_terror = self.mean_ierror = 0   

    def return_coords(self):
        """ Gives a list of (lat,lon) pairs for a given track
        
        Parameters
        -----------
        self : Track
            track object containing positional and temporal TC data

        Returns
        --------
            : List
            List of tuples containing coordinates of TC position for easy mapping
        """
        return [(self.forecasts[idx].lon,self.forecasts[idx].lat) for (idx,fcst) in enumerate(self.forecasts)]
    
    def return_lons(self):
        """ Returns a list of longitudes in a given track
        
        Parameters
        -----------
        self : Track

        Returns
        --------
            : List
            List of longitudes for the TC track
        """
        return [self.forecasts[idx].lon for (idx,fcst) in enumerate(self.forecasts)]
    
    def return_lats(self):
        """ Returns a list of latitudes in a given track
        
        Parameters
        -----------
        self : Track

        Returns
        --------
            : List
            List of latitudes for the TC track """
        return [self.forecasts[idx].lat for (idx,fcst) in enumerate(self.forecasts)]
    
    def return_times(self):
        """ Returns a list of times in a given track
        
        Parameters
        -----------
        self : Track

        Returns
        --------
            : List
            List of times for the TC track """
        return [self.forecasts[idx].time for (idx,fcst) in enumerate(self.forecasts)]
    
    def return_TE(self):
        """ Returns a list of longitudes in a given track
        
        Parameters
        -----------
        self : Track

        Returns
        --------
            : List
            List of longitudes for the TC track
        """
        return [self.forecasts[idx].track_error for (idx,fcst) in enumerate(self.forecasts)]
    
    def return_IE(self):
        """ Returns a list of longitudes in a given track
        
        Parameters
        -----------
        self : Track

        Returns
        --------
            : List
            List of longitudes for the TC track
        """
        return [self.forecasts[idx].intensity_error for (idx,fcst) in enumerate(self.forecasts)]


@dataclass
class Model:
    """ TC Object containing all data for a given model

    Class holds all runs from formation to dissipation for a given model ensemble.

    Attributes
    ----------
        runs : Run 
            List of all runs corresponding to model
        brier_skill_score: 
            TBA
    """
    runs : List[Track]
    brier_skill_score: float = field(init=False)
    errors : List[float] = field(init=False)

    def brier_skill(self):
        """TBA"""
        return []
    
    def mean_errors(self):
        """TBA"""
        t_ers = []
        i_ers = []
        for tr in self.runs:
            t_ers.append(tr.mean_terror)
            i_ers.append(tr.mean_ierror)
        return ((np.mean(t_ers)), (np.mean(i_ers)))

    def __post_init__(self):
        self.brier_skill_score = self.brier_skill()
        self.errors = self.mean_errors()


@dataclass
class Cyclone:
    """ Main TC object containing all information wrt a TC
    
    Class contains all information that is used in tracking TCs for
    organisational purposes, as well as key TC information that can
    be used as a metric for comparison.

    Attributes
    ----------
        name : str 
            NHC assigned storm name
        year : int
            Year of storm occurrence
        ecmwf : Model 
            ECMWF model object
        gfs : Model 
            GFS model object
        number : int 
            Number of storm in season
        formation_date : dt.datetime
            Date of formation in best track
        best_track : List
            List containing best track data
        
    """
    name: str
    year : int
    ecmwf: Model
    best_track: Track
    formation_date: dt.datetime = field(init=False)
    dissipation_date: dt.datetime = field(init=False)

    def __post_init__(self):
        # Sets formation date to the first time in the best track
        self.formation_date = self.best_track.forecasts[0].time 
        self.dissipation_date = self.best_track.forecasts[-1].time  

    def print_summary(self):
        """ Returns a short summary of statistics for a TC """
        print(f'Tropical Cyclone {self.name}:')
        print(f'formation date: {self.formation_date.strftime("%Y-%m-%d, %H:%M")}')
        print(f'dissipation date: {self.dissipation_date.strftime("%Y-%m-%d, %H:%M")}')
        print(f'Best Track: {self.best_track.return_coords()}')
        print(f'ECMWF Mean Total Track Error: {self.ecmwf.errors[0]}') 
        #print(f'GFS Mean Total Track Error: {self.gfs.errors[0]}')
        print(f'ECMWF Mean Total Intensity Error: {self.ecmwf.errors[1]}') 
        #print(f'GFS Mean Total Intensity Error: {self.gfs.errors[1]}')

    def track_map(self):
        """ Creates a quick track map for TC"""
        print(f"Best track map for TC {self.name}: ")
        # Extract coords
        lons = self.best_track.return_lons()
        lats = self.best_track.return_lats()
        ax = plt.axes(projection=ccrs.PlateCarree())
        # Auto crop map
        ax.set_extent([min(lons)-15, max(lons)+15, min(lats)-15, max(lats)+15], crs=ccrs.PlateCarree())
        ax.stock_img()
        ax.coastlines()
        ax.plot(lons,lats,transform=ccrs.PlateCarree())

    def track_map_spec_run(self,run_num):
        """ Creates a quick track map for TC at specified run"""
        print(f"Best track map for TC {self.name}: ")
        # Extract coords
        lons = self.ecmwf.runs[run_num].return_lons()
        lats = self.ecmwf.runs[run_num].return_lats()
        ax = plt.axes(projection=ccrs.PlateCarree())
        # Auto crop map
        ax.set_extent([min(lons)-15, max(lons)+15, min(lats)-15, max(lats)+15], crs=ccrs.PlateCarree())
        ax.stock_img()
        ax.coastlines()
        ax.scatter(lons,lats,transform=ccrs.PlateCarree())

    def track_map_fcast_evolution(self):
        """ Creates a map showing the track forecast evolution across
            model runs """
        fig = plt.figure(figsize=(10,8))
        ax = plt.axes(projection=ccrs.PlateCarree())
        min_lon = min(self.ecmwf.runs[0].return_lons())
        max_lon = max(self.ecmwf.runs[0].return_lons())
        min_lat = min(self.ecmwf.runs[0].return_lats())
        max_lat = max(self.ecmwf.runs[0].return_lats())
        
        for (idx,run) in enumerate(self.ecmwf.runs):
            lons = run.return_lons()
            lats = run.return_lats()
            init = min(run.return_times())

            if min(lons) < min_lon : min_lon = min(lons)
            if max(lons) < max_lon : max_lon = max(lons)
            if min(lats) < min_lat : min_lon = min(lats)
            if max(lats) < max_lat : min_lat = min(lats)

            ax.scatter(lons,lats,transform=ccrs.PlateCarree(), 
                       color=colorFader('red','blue',idx/len(self.ecmwf.runs)),alpha=0.5,label=init)

        bt_lons = self.best_track.return_lons()
        bt_lats = self.best_track.return_lats()
        ax.plot(bt_lons,bt_lats,transform=ccrs.PlateCarree(),c='k',lw=0.6,label='Best Track')
        ax.legend(prop={'size':6})
        ax.set_extent([min(bt_lons)-15, max(bt_lons)+15, min(bt_lats)-15, max(bt_lats)+15], crs=ccrs.PlateCarree())
        ax.stock_img()
        ax.coastlines()
        ax.set_title(f'ECMWF Forecast Evolution for TC {self.name}')

    def track_map_fcast_evolution_int(self,type):
        """ Creates a map showing the track forecast evolution across
            model runs """
        fig = plt.figure(figsize=(10,8))
        ax = plt.axes(projection=ccrs.PlateCarree())
        min_lon = min(self.ecmwf.runs[0].return_lons())
        max_lon = max(self.ecmwf.runs[0].return_lons())
        min_lat = min(self.ecmwf.runs[0].return_lats())
        max_lat = max(self.ecmwf.runs[0].return_lats())
        
        for (idx,run) in enumerate(self.ecmwf.runs):
            lons = run.return_lons()
            lats = run.return_lats()
            init = min(run.return_times())

            if min(lons) < min_lon : min_lon = min(lons)
            if max(lons) < max_lon : max_lon = max(lons)
            if min(lats) < min_lat : min_lon = min(lats)
            if max(lats) < max_lat : min_lat = min(lats)

            if type == "TE":
                errorScale = run.return_TE()
                title = 'Track Error (km)'

            if type == "IE":
                errorScale = run.return_IE()
                title = 'Intensity Error (hPa)'

            sc = ax.scatter(lons,lats,transform=ccrs.PlateCarree(), c = errorScale,cmap='seismic',alpha=0.5,label=init)

        bt_lons = self.best_track.return_lons()
        bt_lats = self.best_track.return_lats()
        ax.plot(bt_lons,bt_lats,transform=ccrs.PlateCarree(),c='k',lw=0.6,label='Best Track')
        ax.set_extent([min(bt_lons)-15, max(bt_lons)+15, min(bt_lats)-15, max(bt_lats)+15], crs=ccrs.PlateCarree())
        ax.stock_img()
        ax.coastlines()
        ax.set_title(f'ECMWF Forecast Evolution of {title} for TC {self.name}')
        cbar = fig.colorbar(sc)
        cbar.set_label(f'{title}')
        fig.tight_layout()

def track_maps(cyclones, ens = True):
    """ Creates a track or ensemble map for a list of Cyclone objects

    Parameters
    -----------
    cyclones : List
        List of cyclone objects to be mapped
    ens : Bool
        Defines if plot should be of the ensembles or not

    Returns
    --------
    Map of specified TCs
    """
    fig = plt.figure(figsize=(10,8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    for cyclone in cyclones:
        
        for (idx,run) in enumerate(cyclone.ecmwf.runs):
            lons = run.return_lons()
            lats = run.return_lats()
            init = min(run.return_times())

            ax.scatter(lons,lats,transform=ccrs.PlateCarree(), 
                       color=colorFader('red','blue',idx/len(cyclone.ecmwf.runs)),alpha=0.3,label=init)
        bt_lons = cyclone.best_track.return_lons()
        bt_lats = cyclone.best_track.return_lats()
        ax.plot(bt_lons,bt_lats,transform=ccrs.PlateCarree(),c='k',lw=0.8,label='Best Track')
    
    #ax.legend(prop={'size':6})
    ax.set_extent([-103.086719,-1.390229,-4.214844,57.401515], crs=ccrs.PlateCarree())
    ax.stock_img()
    ax.coastlines()
    ax.set_title('ECMWF Ensemble forecasts for 2020 Atlantic Hurricane Season')
    
    

                   