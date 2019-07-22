import simplekml
import configParameters as cp
import os
import pandas as pd
import json

def getSRI(station, mm_dd_yyyy):
    filepath= cp.data+"/SRI/"+station+"/"+mm_dd_yyyy[-4:]+".csv"
    if os.path.exists(filepath):
        df= pd.read_csv(filepath, sep=',', index_col=0, names=['daySRI','MaxSRI'])
        return df.loc[mm_dd_yyyy]['daySRI']
    print("\tSRI values for station/year: "+station+"/"+mm_dd_yyyy[-4:]+" do not exist.")
    return -999

def get_Icon( SRI):
#returning url of colored icon according to daily SRI sum intensity
    if SRI==-999:
        return "http://maps.google.com/mapfiles/kml/paddle/wht-circle.png"
    elif SRI<=0:
        return "http://maps.google.com/mapfiles/kml/paddle/grn-circle.png"
    elif SRI<=3:
        return "http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png"
    elif SRI<=9:
        return "http://maps.google.com/mapfiles/kml/paddle/orange-circle.png"
    else:
        return "http://maps.google.com/mapfiles/kml/paddle/red-circle.png"

def alert_output_gen( alert_list):
    #generating output string from alert info
    output_string="Rules fired:\n"
    for alert in alert_list:
        output_string= output_string+"_"+alert["rule_name"]+": "+str(alert['SRI'])+"(sri)\n"
        facts= alert["fact_list"]
        for fact in facts:
            output_string= output_string+"__"+fact["fact_type"]+": "+fact["fuzzyI"]+"("+str(fact["I"])+"), "+fact["fuzzyTod"]+".\n"
    return output_string

def day_alerts_summary( station, mm_dd_yyyy):
    if os.path.exists(cp.alerts+station+"/"+mm_dd_yyyy[-4:]+".json"):
        #importing alert info
        with open(cp.alerts+station+"/"+mm_dd_yyyy[-4:]+".json", 'r') as Afile:
            Alerts= json.load(Afile)
        #sorting through alerts from the year to find alerts matching the specific day
        date_match_alerts= []
        for key in Alerts:
            if key[:10]==mm_dd_yyyy:
                date_match_alerts.append(Alerts[key])
        #generating output string from alert info
        return alert_output_gen( date_match_alerts)
    return "Data not available."

def single_date( mmddyyyy):
    #getting SRI data
    mm_dd_yyyy= mmddyyyy[:2]+"_"+mmddyyyy[2:-4]+"_"+mmddyyyy[-4:]
    mlrSRI= getSRI("mlrf1", mm_dd_yyyy)
    fwySRI= getSRI("fwyf1", mm_dd_yyyy)
    sanSRI= getSRI("sanf1", mm_dd_yyyy)
    smkSRI= getSRI("smkf1", mm_dd_yyyy)
    
    #initialize kml object
    kml = simplekml.Kml()
    kml.document.name = "Fig3_"+mm_dd_yyyy
    
    #generating descriptions for points using alert info
    mlrAlertOutput= mm_dd_yyyy+" SRI: "+ str(mlrSRI)+ "\n"+ day_alerts_summary( "mlrf1", mm_dd_yyyy)
    fwyAlertOutput= mm_dd_yyyy+" SRI: "+ str(fwySRI)+ "\n"+ day_alerts_summary( "fwyf1", mm_dd_yyyy)
    sanAlertOutput= mm_dd_yyyy+" SRI: "+ str(sanSRI)+ "\n"+ day_alerts_summary( "sanf1", mm_dd_yyyy)
    smkAlertOutput= mm_dd_yyyy+" SRI: "+ str(smkSRI)+ "\n"+ day_alerts_summary( "smkf1", mm_dd_yyyy)
    
    #adding points
    #Fowey
    fwyf1= kml.newpoint(name="Fowey Rock Lighthouse, FL",
                        description = fwyAlertOutput,
                        coords= [cp.coorFWY])
    fwyf1.style.iconstyle.icon.href= get_Icon(fwySRI)
    #Molasses Reef
    mlrf1= kml.newpoint(name="Molasses Reef, FL",
                        description = mlrAlertOutput,
                        coords= [cp.coorMLR])
    mlrf1.style.iconstyle.icon.href= get_Icon(mlrSRI)
    #Sand Key, FL 
    sanf1= kml.newpoint(name="Sand Key, FL",
                        description = sanAlertOutput,
                        coords= [cp.coorSAN])
    sanf1.style.iconstyle.icon.href= get_Icon(sanSRI)
    #Sombrero Key, FL
    smkf1= kml.newpoint(name="Sombrero Key, FL",
                        description = smkAlertOutput,
                        coords= [cp.coorSMK])
    smkf1.style.iconstyle.icon.href= get_Icon(smkSRI)
    
    #setting focus point for camera
    fwyf1.lookat= simplekml.LookAt( latitude=24.98506, longitude=-80.74629, range=300000)

    #exporting kml file
    if not(os.path.exists(cp.kml)):
        os.mkdir(cp.kml)
    kml.save(cp.kml+mm_dd_yyyy+".kml")

def range_date(date_list):
    start_date= date_list[0]
    end_date= date_list[1]
    print("\tDate range functionality is not finished yet. Please rerun kmlgen with a single date.")

def main( mmddyyyy):
    if (type(mmddyyyy)==str):
        single_date(mmddyyyy)
    elif((type(mmddyyyy)==list)and(type(mmddyyyy[0])==str)):
        range_date(mmddyyyy)
    else:
        raise ValueError('Argument Should be a single string or list of two strings in the form mmddyyyy')

