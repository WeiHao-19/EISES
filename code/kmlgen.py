import simplekml
import configParameters as cp
import os
import pandas as pd

def getSRI(station, mm_dd_yyyy):
    filepath= cp.data+"/SRI/"+station+"/"+mm_dd_yyyy[-4:]+".csv"
    if os.path.exists(filepath):
        df= pd.read_csv(filepath, sep=',', index_col=0, names=['daySRI','MaxSRI'])
        return df.loc[mm_dd_yyyy]['daySRI']
    print("\tSRI values for station/year: "+station+"/"+mm_dd_yyyy[-4:]+" do not exist.")
    return -999

def get_Icon( SRI):
    if SRI<=0:
        return "http://maps.google.com/mapfiles/kml/paddle/grn-circle.png"
    elif SRI<=3:
        return "http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png"
    elif SRI<=9:
        return "http://maps.google.com/mapfiles/kml/paddle/orange-circle.png"
    else:
        return "http://maps.google.com/mapfiles/kml/paddle/red-circle.png"

def main( mmddyyyy):
    #getting SRI data
    mm_dd_yyyy= mmddyyyy[:2]+"_"+mmddyyyy[2:-4]+"_"+mmddyyyy[-4:]
    mlrSRI= getSRI("mlrf1", mm_dd_yyyy)
    fwySRI= getSRI("fwyf1", mm_dd_yyyy)
    sanSRI= getSRI("sanf1", mm_dd_yyyy)
    smkSRI= getSRI("smkf1", mm_dd_yyyy)
    
    #initialize kml object
    kml = simplekml.Kml()
    kml.document.name = "Fig3_"+mm_dd_yyyy
    
    #adding points
    #Fowey
    fwyf1= kml.newpoint(name="Fowey Rock Lighthouse, FL",
                        description = "SRI="+str(fwySRI)+" for "+mm_dd_yyyy+". MCB forecast rules fired [X]",
                        coords= [cp.coorFWY])
    fwyf1.style.iconstyle.icon.href= get_Icon(fwySRI)
    #Molasses Reef
    mlrf1= kml.newpoint(name="Molasses Reef, FL",
                        description = "SRI="+str(mlrSRI)+" for "+mm_dd_yyyy+". MCB forecast rules fired [X]",
                        coords= [cp.coorMLR])
    mlrf1.style.iconstyle.icon.href= get_Icon(mlrSRI)
    #Sand Key, FL 
    sanf1= kml.newpoint(name="Sand Key, FL",
                        description = "SRI="+str(sanSRI)+" for "+mm_dd_yyyy+". MCB forecast rules fired [X]",
                        coords= [cp.coorSAN])
    sanf1.style.iconstyle.icon.href= get_Icon(sanSRI)
    #Sombrero Key, FL
    smkf1= kml.newpoint(name="Sombrero Key, FL",
                        description = "SRI="+str(smkSRI)+" for "+mm_dd_yyyy+". MCB forecast rules fired [X]",
                        coords= [cp.coorSMK])
    smkf1.style.iconstyle.icon.href= get_Icon(smkSRI)
    
    #setting focus point for camera
    fwyf1.lookat= simplekml.LookAt( latitude=24.98506, longitude=-80.74629, range=300000)

    #exporting kml file
    if not(os.path.exists(cp.kml)):
        os.mkdir(cp.kml)
    kml.save(cp.kml+mm_dd_yyyy+".kml")
