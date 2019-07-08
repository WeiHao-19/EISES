#generate none relative file paths
#sampling rates dictionary of sensors
import os

#PATHS
currentLocation= os.path.dirname(os.path.abspath(__file__))
code= currentLocation
data= currentLocation[:-4]+"data"
netCDF= currentLocation[:-16]+'USGS_Samoa_2015_data/CTD_profile_data'


#CONSTANTS
insitu_samplingRate= 365*24
sri_max_4f= 24*2.5*4
sri_max_3f= 24*2.5*3
sri_max_2f= 24*2.5*2
sri_max_1f= 24*2.5

