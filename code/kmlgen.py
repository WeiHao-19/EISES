import simplekml

def main():
    #initialize kml object
    kml = simplekml.Kml()
    kml.document.name = "Fig3_test"
    fwyf1= kml.newpoint(name="Fowey Rock Lighthouse",
                        description = "SRI= XX for MM/DD/YY. MCB forecast rules fired [X]",
                        coords= [(-80.097, 25.591)])
    fwyf1.lookat = simplekml.LookAt( latitude=-80.097, longitude=25.591,
            range=300000)
    fwyf1.style.iconstyle.icon.href= 'http://maps.google.com/mapfiles/kml/paddle/wht-blank.png'
    fwyf1.style.iconstyle.color= 'ffff0000'
    kml.save("/Users/soden/Desktop/fwyf1_location.kml")
