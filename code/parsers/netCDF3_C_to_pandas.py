import configParameters as configP
import netCDF4 as nc
import os
import datetime
import pandas as pd
import pytz

def get_file_datetime( dataSet):
    #convert year and Julian day into standard date
    year= dataSet.ncfilename[:4]
    jul_days= str(int(dataSet.julday)) 
    file_date= datetime.datetime.strptime((year+jul_days), '%Y%j').date()
    #convert msec since 0:00 GMT to ~hh:mm since GMT
    time_hours_min= list(dataSet.variables["time2"][:])[-1]#get last time in list
    time_hours_min*= 0.001 #converting from msec to sec
    time_hours_min/= 3600 #converting from sec to hours
    time_hours, time_min= divmod(time_hours_min, 1) #converting to hours and min as a fraction of hours
    time_min*= 60 #converting min as a fraction of hours to min
    file_time= datetime.datetime.strptime((str(int(time_hours))+str(int(time_min))),'%H%M').time()
    #create datetime
    file_datetime= datetime.datetime.combine( file_date, file_time)
    return file_datetime

def check_for_missing_values( dataSet):
    fill_var= int(dataSet.VAR_FILL)
    null_index_counter= 0
    null_index_list= []
    for i in dataSet.variables["P_1"]:
        if(int(i[0][0][0])==fill_var):
            null_index_list.append(null_index_counter)
        null_index_counter+=1
    null_values=False
    if(null_index_counter):
        null_values=True
    return null_values, null_index_list

def check_file_parsar_compatibility( dataSet):
    dataSet_keys= list(dataSet.variables.keys())
    req_keys= ['time','time2','lat','lon','depth','P_1','D_3','T_28','C_51','S_41','F_903','ptrn_4011','ATTN_55']
    assert dataSet_keys==req_keys, "File does not have required keys, This parser is not designed to handle other data formats."
#    try:
#        assert dataSet_keys==req_keys
#    except AssertionError:
#        print("\tFile "+dataSet.ncfilename+" does not have required keys
#                matching: "+ str(req_keys)+"\n\tThis parser is not designed to
#                handle other data formats.")
#        raise
    return dataSet_keys
    
def sort_key_f( file_name_s):
    num= file_name_s[-5:-3]
    if num[0]=="_":
        num= num[1:]
    return(int(num))

def makedirs():
    #locating files  
    CTDdirs = os.listdir(configP.netCDF)
    #removing possible non-data directory from directory list
    for i in CTDdirs:
        if (i=="INFO"):
            CTDdirs.remove(i)
    #creating directory to store pandas json files that will be created by parser from netCDF3 files
    CTD_json_storage=configP.netCDF[:-16]+"jsons"
    try:
        os.mkdir(CTD_json_storage)
        print("\t"+CTD_json_storage+" directory created.")
    except FileExistsError:
        print("\t"+CTD_json_storage+" directory already exists.")
    #creating sub directory for each year
    for i in CTDdirs:
        newdir= CTD_json_storage+"/"+i[:-9]
        try:
            os.mkdir(newdir)
            print("\t"+newdir+" directory created.")
        except FileExistsError:
             print("\t"+newdir+" directory already exists.")
    #creating standardized path names for location o json storage directories
    jsonpath_0215= CTD_json_storage+"/2015_02"
    jsonpath_0715= CTD_json_storage+"/2015_07"
    return CTDdirs, jsonpath_0215, jsonpath_0715

def get_file_names():
    #making standardized path names for netCDF directory locations
    netCDFpath_0215= configP.netCDF+"/2015_02_CTD_data"
    netCDFpath_0715=configP.netCDF+"/2015_07_CTD_data"
    #getting list of all file names in both netCDF directories
    CTDfiles_0215= [f for f in os.listdir(netCDFpath_0215) if os.path.isfile(os.path.join(netCDFpath_0215, f))]
    CTDfiles_0715= [f for f in os.listdir(netCDFpath_0215) if os.path.isfile(os.path.join(netCDFpath_0215, f))]  
    #sorting list of CTD files in descending order. Using custom sort function to take "_4.nc" file names into account, not having _04.nc confuses basic sort function.
    CTDfiles_0215.sort(key=sort_key_f)
    CTDfiles_0715.sort(key=sort_key_f)
    return CTDfiles_0215, CTDfiles_0715, netCDFpath_0215, netCDFpath_0715

def main( file_list_index=0, a, b, c):
    #identify directory in data file and make corresponding storage directories for parsed files
    CTDdirs, jsonpath_0215, jsonpath_0715=  makedirs()
    
    #getting lists of all file names in directory and generating directory paths variables
    CTDfiles_0215, CTDfiles_0715, netCDFpath_0215, netCDFpath_0715= get_file_names() 
   
    #importing dataset
    dataSet= nc.Dataset(netCDFpath_0215+"/"+CTDfiles_0215[file_list_index]) 
    
    #making the variable information more easily accessible
    dataSet.set_auto_mask(False)

    #checking to make sure dataset will function with parser
    dataSet_keys= check_file_parsar_compatibility( dataSet)

    #checking for missing values
    null_values, null_index_list= check_for_missing_values( dataSet)

    #creating datetime object for file
    file_datetime= get_file_datetime( dataSet)
    #converting datetime from GMT to SST(Standard Samoa Time)
    gmt_zone= pytz.timezone("GMT") 
    sst_zone= pytz.timezone("US/Samoa")
    file_datetime= gmt_zone.localize(file_datetime).astimezone(sst_zone)

    #creating latitude longitude variables
    file_lat= float(dataSet.variables['lat'][:][0])
    file_lon= float(dataSet.variables['lon'][:][0])

    #creating tuples of the form ('MM/DD/YYYY_HH:MM:SS', float(longitude), float(longitude), float(depth in meters)) to be indexes of pandas array
    indexDepths= dataSet.variables['depth'][:]
    file_datetime_s= file_datetime.strftime("%m/%d/%Y_%H:%M:%S")
    indexNames= []
    for i in indexDepths:
        indexTuple= (file_datetime_s, file_lat, file_lon, i)
        indexNames.append(indexTuple)
    columnNames= list(dataSet.variables.keys())[5:]
    
    #initializing empty data frame
    df= pd.DataFrame( index= indexNames, columns= columnNames)
    

    return dataSet, file_datetime, df
