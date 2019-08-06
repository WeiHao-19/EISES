import simplekml
import configParameters as cp
import os
import pandas as pd
import json
import datetime

def getSRI(station, mm_dd_yyyy):
    filepath= cp.data+ "/SRI/"+station+"/"+mm_dd_yyyy[-4:]+".csv"
    if os.path.exists(filepath):
        df= pd.read_csv(filepath, sep=',', index_col=0, names=['daySRI','MaxSRI'])
        return df.loc[mm_dd_yyyy]['daySRI']
    print("\tSRI values for station/year: "+station+"/"+mm_dd_yyyy[-4:]+" do not exist.")
    return -999

def getSRI_sum( station, s_mm_dd_yyyy, e_mm_dd_yyyy):
    #creating list of every date inf range given
    year_range= list( range( int(s_mm_dd_yyyy[-4:]), int(e_mm_dd_yyyy[-4:])+1))
    s_yyyy_mm_dd= s_mm_dd_yyyy[-4:]+"-"+s_mm_dd_yyyy[:2]+"-"+s_mm_dd_yyyy[3:5]
    e_yyyy_mm_dd= e_mm_dd_yyyy[-4:]+"-"+e_mm_dd_yyyy[:2]+"-"+e_mm_dd_yyyy[3:5]
    date_range= pd.date_range( s_yyyy_mm_dd, e_yyyy_mm_dd).to_pydatetime().tolist()  
    
    #iterating through every year in date range, opening each year csv, and appending sri data to DataFrame
    i= 0
    missing_dates= [] #for listing missing data warning in point description later
    df= pd.DataFrame(columns=['daySRI', "MaxSRI"])
    while i < len(year_range):
        filepath= cp.data+"/SRI/"+station+"/"+str(year_range[i])+".csv"
        if os.path.exists( filepath):
            df1= pd.read_csv( filepath, sep=",", index_col=0, names=['daySRI', "MaxSRI"])
            df= df.append(df1)
            i+=1
        else:
            print("\tSRI values for the station/year: "+station+"/"+str(year_range[i])+" not available.")
            missing_dates.append(year_range[i])
            i+=1

    #iterating through each date and adding SRI to sum    
    SRI=0
    key_error_count=[]
    for j in date_range:
        try: 
            SRI+= df.loc[j.strftime('%m_%d_%Y')]['daySRI']
        except KeyError:
            missing_dates.append(j.strftime("%m_%d_%Y"))
    return SRI, missing_dates

def get_Icon( SRI, missing_dates):
#ret urning url of colored icon a according to daily SRI sum intensity
    if SRI==-999 or missing_dates:
        return "https://drive.google.com/uc?export=download&id=11KZkQ-sF5gjk0diBxbrXIfPQO_R7KjkQ"
    elif SRI<=0:
        return "https://drive.google.com/uc?export=download&id=1dSftNvFbZeiVpR2nfegktq3IcWGV8AVC" #bottom 20%
    elif SRI<=3:
        return "https://drive.google.com/uc?export=download&id=1WrBqUbgpyuJlNOPdOxsge9Js9TwpIEfC" #next 30%
    elif SRI<=9:
        return "https://drive.google.com/uc?export=download&id=1QzwD8KfZgLESPtzRLZJWAnwxjud3Wuqc" #next 30%
    else:
        return "https://drive.google.com/uc?export=download&id=1i8uoQxTQw1g14nlEgFN7y3jachXboeM4" #top 20%

def daily_output_gen( alert_list):
    #generating  output string from alert info
    output_string="Rules fired:\n"
    for alert in alert_list:
        output_string= output_string+"_"+alert["rule_name"]+": "+str(alert['SRI'])+"(sri)\n"
        facts= alert["fact_list"]
        for fact in facts:
            output_string= output_string+"__"+fact["fact_type"]+": "+fact["fuzzyI"]+"("+str(fact["I"])+"), "+fact["fuzzyTod"]+".\n"
    return output_string

def range_output_gen( alert_list):
    #generating  output string from alert info
    output_string="Rules fired:\n"
    for alert in alert_list:
        date= alert[:10]
        date= date[:2]+"/"+date[3:5]+"/"+date[-2:]
        output_string= output_string+"_"+date+": "+alert_list[alert]["rule_name"]+"("+str(alert_list[alert]['SRI'])+")\n"
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
        return daily_output_gen( date_match_alerts)
    return "Data not available."

def range_alerts_summary( station, s_mm_dd_yyyy, e_mm_dd_yyyy):
    #calculating years in date range to upload files with 
    year_range= list( range( int(s_mm_dd_yyyy[-4:]), int(e_mm_dd_yyyy[-4:])+1))
   
    #generating a dictionary containing all recorded alert information from time frame
    i=0
    alert_dict= {}
    while i < len(year_range):
        filepath= cp.alerts+station+"/"+str(year_range[i])+".json"
        if os.path.exists( filepath):
            with open(filepath, 'r') as Afile:
                alert_dict1= json.load( Afile)
                alert_dict.update( alert_dict1)
            i+=1
        else:
            print("\tAlert information for the station/year: "+station+"/"+str(year_range[i])+" not available.")
            missing_dates.append(year_range[i])
            i+=1    

    #deleting entries from dictionary that are not in date  range    
    s_dt= datetime.datetime.strptime( s_mm_dd_yyyy, '%m_%d_%Y')
    e_dt= datetime.datetime.strptime( e_mm_dd_yyyy, '%m_%d_%Y')
    se_alert_dict= {}
    for key in alert_dict:
        key_dt= datetime.datetime.strptime(key[:10], '%m_%d_%Y')
        if( (key_dt >= s_dt) and (key_dt <= e_dt) ):
            se_alert_dict[key]= alert_dict[key]   

    return range_output_gen( se_alert_dict)

def addScreenOverlays( kml):
    stationIndex = kml.newscreenoverlay(name='Station Index')
    stationIndex.icon.href = 'https://drive.google.com/uc?export=download&id=1ij8aLRhTZ6GdrRCPF05l83Ocd9Y5A9XC'
    stationIndex.overlayxy = simplekml.OverlayXY( x=1.1, y=0, xunits=simplekml.Units.fraction, yunits=simplekml.Units.fraction)
    stationIndex.screenxy = simplekml.ScreenXY( x=1, y=0.2, xunits=simplekml.Units.fraction, yunits=simplekml.Units.fraction)
    stationIndex.size.x = 0
    stationIndex.size.y = 0
    stationIndex.size.xunits = simplekml.Units.fraction
    stationIndex.size.yunits = simplekml.Units.fraction
    
    noaaLogo = kml.newscreenoverlay(name='NOAA Logo')
    noaaLogo.icon.href = 'https://drive.google.com/uc?export=download&id=1WgGiA-APPPgV8Zv2FMtvQYHtWug2l_Mo'
    noaaLogo.overlayxy = simplekml.OverlayXY( x=0, y=1, xunits=simplekml.Units.fraction, yunits=simplekml.Units.fraction)
    noaaLogo.screenxy = simplekml.ScreenXY( x=0, y=1, xunits=simplekml.Units.fraction, yunits=simplekml.Units.fraction)
    noaaLogo.size.x = 150
    noaaLogo.size.y = 146
    noaaLogo.size.xunits = simplekml.Units.pixel
    noaaLogo.size.yunits = simplekml.Units.pixel


def single_date( mm_dd_yyyy):
    #getting SRI data 
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
    fwyf1.style.iconstyle.icon.href= get_Icon(fwySRI, [])
    fwyf1.style.iconstyle.scale = 2
    #Molasses Reef
    mlrf1= kml.newpoint(name="Molasses Reef, FL",
                        description = mlrAlertOutput,
                        coords= [cp.coorMLR])
    mlrf1.style.iconstyle.icon.href= get_Icon(mlrSRI, [])
    mlrf1.style.iconstyle.scale = 2
    #Sand Key, FL 
    sanf1= kml.newpoint(name="Sand Key, FL",
                        description = sanAlertOutput,
                        coords= [cp.coorSAN])
    sanf1.style.iconstyle.icon.href= get_Icon(sanSRI, [])
    sanf1.style.iconstyle.scale = 2
    #Sombrero Key, FL
    smkf1= kml.newpoint(name="Sombrero Key, FL",
                        description = smkAlertOutput,
                        coords= [cp.coorSMK])
    smkf1.style.iconstyle.icon.href= get_Icon(smkSRI, [])
    smkf1.style.iconstyle.scale = 2
 
    #add kml screen overlays
    addScreenOverlays( kml)

    #exporting kml file
    if not(os.path.exists(cp.kml)):
        os.mkdir(cp.kml)
    filename= cp.kml+mm_dd_yyyy+".kml"
    kml.save(filename)
    return filename   

def range_date(date_list):
    s_mm_dd_yyyy= date_list[0]
    e_mm_dd_yyyy= date_list[1]
     
    #getting SRI data
    mlrSRI, missing_dates= getSRI_sum("mlrf1", s_mm_dd_yyyy, e_mm_dd_yyyy)
    fwySRI, missing_dates= getSRI_sum("fwyf1", s_mm_dd_yyyy, e_mm_dd_yyyy)
    sanSRI, missing_dates= getSRI_sum("sanf1", s_mm_dd_yyyy, e_mm_dd_yyyy)
    smkSRI, missing_dates= getSRI_sum("smkf1", s_mm_dd_yyyy, e_mm_dd_yyyy)
    
    #initialize kml object
    kml = simplekml.Kml()
    kml.document.name = "Fig3_"+s_mm_dd_yyyy+'-'+e_mm_dd_yyyy
    
    #generating descriptions for points using alert info
    mlrAlertOutput= s_mm_dd_yyyy+"-"+e_mm_dd_yyyy+" SRI: "+ str(mlrSRI)+ "\n"+ range_alerts_summary( "mlrf1", s_mm_dd_yyyy, e_mm_dd_yyyy)
    fwyAlertOutput= s_mm_dd_yyyy+"-"+e_mm_dd_yyyy+" SRI: "+ str(fwySRI)+ "\n"+ range_alerts_summary( "fwyf1", s_mm_dd_yyyy, e_mm_dd_yyyy)
    sanAlertOutput= s_mm_dd_yyyy+"-"+e_mm_dd_yyyy+" SRI: "+ str(sanSRI)+ "\n"+ range_alerts_summary( "sanf1", s_mm_dd_yyyy, e_mm_dd_yyyy)
    smkAlertOutput= s_mm_dd_yyyy+"-"+e_mm_dd_yyyy+" SRI: "+ str(smkSRI)+ "\n"+ range_alerts_summary( "smkf1", s_mm_dd_yyyy, e_mm_dd_yyyy)
    
    #adding points
    #Fowey
    fwyf1= kml.newpoint(name="Fowey Rock Lighthouse, FL",
                        description = fwyAlertOutput,
                        coords= [cp.coorFWY])
    fwyf1.style.iconstyle.icon.href= get_Icon(fwySRI, missing_dates)
    fwyf1.style.iconstyle.scale = 2
    #Molasses Reef
    mlrf1= kml.newpoint(name="Molasses Reef, FL",
                        description = mlrAlertOutput,
                        coords= [cp.coorMLR])
    mlrf1.style.iconstyle.icon.href= get_Icon(mlrSRI, missing_dates)
    mlrf1.style.iconstyle.scale = 2
    #Sand Key, FL 
    sanf1= kml.newpoint(name="Sand Key, FL",
                        description = sanAlertOutput,
                        coords= [cp.coorSAN])
    sanf1.style.iconstyle.icon.href= get_Icon(sanSRI, missing_dates)
    sanf1.style.iconstyle.scale = 2
    #Sombrero Key, FL
    smkf1= kml.newpoint(name="Sombrero Key, FL",
                        description = smkAlertOutput,
                        coords= [cp.coorSMK])
    smkf1.style.iconstyle.icon.href= get_Icon(smkSRI, missing_dates)
    smkf1.style.iconstyle.scale = 2
    
    #add kml screen overlays
    addScreenOverlays( kml)

    #exporting kml file
    if not(os.path.exists(cp.kml)):
        os.mkdir(cp.kml)
    filename= cp.kml+s_mm_dd_yyyy[:2]+"_"+s_mm_dd_yyyy[3:5]+"_"+s_mm_dd_yyyy[6:10]+"--"+e_mm_dd_yyyy[:2]+"_"+e_mm_dd_yyyy[3:5]+"_"+e_mm_dd_yyyy[6:10]+".kml"
    kml.save(filename)
    return filename  

def addLookat( filename):
    
    #reading lines of .kml file
    fileread= open(filename, 'r')
    lines= fileread.readlines()

    #adding section to specify LookAt distance and location for kml '<Document>'
    lines.insert(3, '        <LookAt>\n')
    lines.insert(4, '            <longitude>'+ str(cp.KMLcoords[0])+'</longitude>\n')
    lines.insert(5, '            <latitude>'+ str(cp.KMLcoords[1])+'</latitude>\n')
    lines.insert(6, '            <range>400000</range>\n')
    lines.insert(7, '        </LookAt>\n')
    fileread.close()
    
    #writing lines back to file
    filewrite= open(filename, 'w')
    filewrite.writelines(lines)
    filewrite.close()


def main( mm_dd_yyyy):
    if (type(mm_dd_yyyy)==str):
        #generating the bulk of .kml file for single date
        filename= single_date(mm_dd_yyyy)
        #adding default camera position
        addLookat(filename)
    elif((type(mm_dd_yyyy)==list)and(type(mm_dd_yyyy[0])==str)):
        #generating the bulk of .kml file for a range of dates
        filename= range_date(mm_dd_yyyy)
        #adding default camera position
        addLookat(filename)
    else:
        raise ValueError('Argument Should be a single string or list of two\
                strings in the form \'mm_dd_yyyy\'')

#edit ranged of SRI for ranged summary
#ADD SRI LIMITS TO CONFIG FILE
#work on range file name
#work on formatting of ranged summary:
"""05_06_2005-09_07_2005 SRI: 33
Rules fired:
_08/05/05: mcb_w3A(9)
_08/08/05: mcb_w3A(9)
_08/23/05: mcb_w3A(9)
_08/29/05: mcb_AM(6)"""
#make day_alert summary shorter with >, < comparisons instead of making a list of dates
#comment code
