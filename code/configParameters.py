#generate none relative file paths
#sampling rates dictionary of sensors
import os

#FILE PATHS
currentLocation= os.path.dirname(os.path.abspath(__file__))
code= currentLocation
head= currentLocation[:-4]
data= currentLocation[:-4]+"data"
alerts= data+"/alerts/"
netCDF= currentLocation[:-16]+'USGS_Samoa_2015_data/CTD_profile_data'
kml= data+"/kml/"


#CONSTANTS
insitu_samplingRate= 365*24
sri_max_4f= 24*2.5*4
sri_max_3f= 24*2.5*3
sri_max_2f= 24*2.5*2
sri_max_1f= 24*2.5

#Coordinates
coorFWY= (-80.097, 25.591)
coorMLR= (-80.376, 25.012)
coorSAN= (-81.877, 24.456)
coorSMK= (-81.109, 24.628)

