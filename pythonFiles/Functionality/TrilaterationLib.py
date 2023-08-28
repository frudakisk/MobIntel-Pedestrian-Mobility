"""
This file focuses on functions that dealt with trilateration algorithms. We also
attempted a multilateration method, but it performed worse than trilateration.
This file should contain functions that deal with trilateration and the functions 
that help us visualize trilateration
"""

import sys, math, numpy as np, folium, requests, json, webbrowser
from geopy import distance

sys.path.append("pythonFiles")

from Functionality import RSSIToDistanceLib as rLib
from Functionality import GridLib as gLib

response = requests.get("https://api-prod.mobintel.org/v1/sensors")
api = response.json()['results']

#Multilaterate using the distances from the sensors
def multilaterate(coords, dists):
    """
    coords: is a 2D array of coordinates. coords will be populated with the output of 'getCoordinates' function.
    dists: dists is an array. Each index of the array has an (x, y) value for the sensor put into it. 
    That index in the array 'dists' will match the distance from that sensor to the emitter. 
    dists will be populated with the output of the function 'rssiToDistanceV2()'.
    Description: coords must be full of every sensor that picked up the emitter before multilaterate is called.
    coords must have the same number of indices as dists.
    """
    P = [[]]

    if len(coords) > len(dists):
      print("Error: more sensors than distances.")
      print(len(coords))
      print(len(dists))
    if len(coords) < len(dists):
      print("Error: more distances than sensors.")
      print(len(dists))
      print(len(dists))

    earthR = 6378137 #Earth radius in m
    #using authalic sphere
    #if using an ellipsoid this step is slightly different
    #Convert geodetic Lat/Long to ECEF xyz
    #   1. Convert Lat/Long to radians
    #   2. Convert Lat/Long(radians) to ECEF

    for i in range(0, len(coords)):
      xA = earthR *(math.cos(math.radians(coords[i][0])) * math.cos(math.radians(coords[i][1])))
      #print('xA is:', xA)  #used for testing
      yA = earthR *(math.cos(math.radians(coords[i][0])) * math.sin(math.radians(coords[i][1])))
      #print('yA is:', yA)
      zA = earthR *(math.sin(math.radians((coords[i][0]))))
      #print('zA is:', zA)
      P.append([])
      P[i].append(xA) #append this tuple of ECEF coords to one index inside P
      P[i].append(yA)
      P[i].append(zA)

    A = []
    b = []
    for m in range(0,len(P)-1):
      x = P[m][0]
      #print('for m loop, x is:', x)  #used for testing
      y = P[m][1]
      #print('for m loop, y is:', y)
      z = P[m][2]
      #print('for m loop, z is:', z)
      Am = 2*x
      Bm = 2*y
      Cm = 2*z
      Dm = earthR*earthR + (pow(x,2)+pow(y,2)+pow(z,2)) - pow(dists[m],2)
      A += [[Am,Bm,Cm]]
      b += [[Dm]]
# Solve using Least Squares of an MxN System
# A*x = b --> x = (ATA)_inv.AT.b = A+.b
    A = np.array(A)
    b = np.array(b)
    AT = A.T
    ATA = np.matmul(AT,A)
    ATA_inv = np.linalg.inv(ATA)
    Aplus = np.matmul(ATA_inv,AT)
    x = np.matmul(Aplus,b)

# convert back to lat/long from ECEF
# convert to degrees
    lat = math.degrees(math.asin(x[2] / earthR))
    lon = math.degrees(math.atan2(x[1],x[0]))
    print (lat,lon)
    return (lat,lon) #This should be the coordinates of the emitting device


def trilaterate(sXLoc, sXDist, sYLoc, sYDist, sZLoc, sZDist):
    """
    sXLoc: a tuple (lat, long) which tells us the location of sensor X
    sXDist: The distance the emitting device is from sensor X
    sYLoc: a tuple (lat, long) which tells us the location of sensor Y
    sYDist: The distance the emitting device is from sensor Y
    sZLoc: a tuple (lat, long) which tells us the location of sensor Z 
    sZDist: The distance the emitting device is from sensor Z
    Returns: a (lat, long) position of where this algorithms predicts the emitting
    devices is located
    Description: This function returns a tuple (lat, long) of the trilaterated 
    location using the information from 3 locations and their distances.
    """

    earthR = 6378137 #Earth radius in m
    S1Lat = sXLoc[0] #coordinate of sensor 1
    S1Lon = sXLoc[1]
    S1Dist = sXDist # distance from s1 to device in meters
    S3Lat = sYLoc[0]
    S3Lon = sYLoc[1]
    S3Dist = sYDist # distance from s3 to device in meters
    S10Lat = sZLoc[0]
    S10Lon = sZLoc[1]
    S10Dist = sZDist

    #using authalic sphere
    #if using an ellipsoid this step is slightly different
    #Convert geodetic Lat/Long to ECEF xyz
    #   1. Convert Lat/Long to radians
    #   2. Convert Lat/Long(radians) to ECEF
    xA = earthR *(math.cos(math.radians(S1Lat)) * math.cos(math.radians(S1Lon)))
    yA = earthR *(math.cos(math.radians(S1Lat)) * math.sin(math.radians(S1Lon)))
    zA = earthR *(math.sin(math.radians(S1Lat)))

    xB = earthR *(math.cos(math.radians(S3Lat)) * math.cos(math.radians(S3Lon)))
    yB = earthR *(math.cos(math.radians(S3Lat)) * math.sin(math.radians(S3Lon)))
    zB = earthR *(math.sin(math.radians(S3Lat)))

    xC = earthR *(math.cos(math.radians(S10Lat)) * math.cos(math.radians(S10Lon)))
    yC = earthR *(math.cos(math.radians(S10Lat)) * math.sin(math.radians(S10Lon)))
    zC = earthR *(math.sin(math.radians(S10Lat)))

    P1 = np.array([xA, yA, zA])
    P2 = np.array([xB, yB, zB])
    P3 = np.array([xC, yC, zC])

    #from wikipedia
    #transform to get circle 1 at origin
    #transform to get circle 2 on x axis
    ex = (P2 - P1)/(np.linalg.norm(P2 - P1))
    i = np.dot(ex, P3 - P1)
    ey = (P3 - P1 - i*ex)/(np.linalg.norm(P3 - P1 - i*ex))
    ez = np.cross(ex,ey)
    d = np.linalg.norm(P2 - P1)
    j = np.dot(ey, P3 - P1)

    #from wikipedia
    #plug and chug using above values
    x = (pow(S1Dist,2) - pow(S3Dist,2) + pow(d,2))/(2*d)
    y = ((pow(S1Dist,2) - pow(S10Dist,2) + pow(i,2) + pow(j,2))/(2*j)) - ((i/j)*x)

    #print(x,y)
    #print(pow(S1Dist,2))
    #print(pow(x,2) - pow(y,2))
    # only one case shown here
    z = np.sqrt(abs(pow(S1Dist,2) - pow(x,2) - pow(y,2)))

    #triPt is an array with ECEF x,y,z of trilateration point
    triPt = P1 + x*ex + y*ey + z*ez

    #print(z*ez)
    #print(triPt[2])

    #convert back to lat/long from ECEF
    #convert to degrees
    lat = math.degrees(math.asin(triPt[2] / earthR))
    lon = math.degrees(math.atan2(triPt[1],triPt[0]))

    return (lat,lon) #This should be the coordinates of the emitting device


def plotRowOnMap(row, sensorSet, trueEmitterLocationSet, data, m, d=None, createCSV=False, oldVersion=True):
    """
    row: a row from the fanchen_trilateration_2022_11_13.parquet file, or a file of
    the same format
    sensorSet: must be an empty set() to hold all sensor locations. we outsource these
    coordinates because we want to plot them later.
    trueEmitterLocationSet: must be an empty set() that holds all the actual emitter 
    locations that we are using as our ground truth.
    data: must be an empty list() that will hold data for a data frame if the user decides
    to create a data frame object from this function
    m: a folium.Map object for us to add markers to. This is how we visualize
    the trilateration outcomes
    d: the radius at which the user wants to plot trilaterated points (meters)
    createCSV: if set to true, loads @data with information to be easily converted to
    a csv file.
    oldVersion: if true, we use old method of trilateration, if true we use newer version
    (new version is better)
    Returns: data about a trilaterated point saved in sensorSet, trueEmitterLocationSet
    and data
    Description:
    plots the trilaterated position of the emitter at each row of
    the trilateration dataset. Also keep track of which sensors were being used
    and the actual locations of the emitter.
    row must be a row of data in the form of a row in fanchen_trilateration_2022_11_13.parquet.
    At the end of this function, sensorSet, trueEmitterLocation, and data will be loaded with information
    That can be used to plot the sensors that were used in trilateration
    as well as plotting the actual location of the emitter at the time of trilateration
    """
    sXCoords = getCoordinates(row["sensor_x"])
    sYCoords = getCoordinates(row["sensor_y"])
    sZCoords = getCoordinates(row["sensor_z"])
    sensorSet.add(sXCoords)
    sensorSet.add(sYCoords)
    sensorSet.add(sZCoords)
    #plot sensors later?
    if oldVersion:
        sYDist= rLib.rssiToDistance(row["rssi_y"])
        sZDist= rLib.rssiToDistance(row["rssi_z"])
        sXDist= rLib.rssiToDistance(row["rssi_x"])
    else:
        sYDist= rLib.rssiToDistanceV2(row["rssi_y"])
        sZDist= rLib.rssiToDistanceV2(row["rssi_z"])
        sXDist= rLib.rssiToDistanceV2(row["rssi_x"])

    # sYDist= linearRssiToDistanceFull(row["rssi_y"])
    # sZDist= linearRssiToDistanceFull(row["rssi_z"])
    # sXDist= linearRssiToDistanceFull(row["rssi_x"])

    location = trilaterate(sXLoc=sXCoords, sXDist=sXDist, sYLoc=sYCoords, sYDist=sYDist, sZLoc=sZCoords, sZDist=sZDist)
    #instead of location, give distance to true position
    emitterCoords = getEmitterCoords(row)
    dist = distance.distance(emitterCoords, location).meters
    #prepare data to be stored in dataframe
    if createCSV:
        row = list(row)
        row.append(dist)
        data.append(row)
    if d == None:
        #plot all
        folium.Marker(location, popup=dist ,icon=folium.Icon(color="green"), tooltip="Click Me!").add_to(m)
    elif d != None and dist < d:
        #Only plot the ones that are d meteres away from true emitter location
        folium.Marker(location, popup=dist ,icon=folium.Icon(color="green"), tooltip="Click Me!").add_to(m)
    trueEmitterLocationSet.add(emitterCoords)


def getCoordinates(sensorNum):
    """
    sensorNum: can be of type float, numpy.float32, or string. Represents a sensor
    id number
    Returns: the geographical location of the emitter as a tuple of (lat, long)
    Description: Given the sensor number, this function returns the location 
    of the sensor in the form of a tuple (latitude, longitude).
    single digit sensor numbers must be prefixed with 0 (i.e., 02 instead of just 2)
    if an s is prefixing the sensor, it will be removed (i.e., s02 -> 02)
    """
    if type(sensorNum) == int:
        sensorNum = str(sensorNum)
    elif type(sensorNum) == np.float32 or type(sensorNum) == float:
        sensorNum = str(int(sensorNum))
        if isSingleDigit(sensorNum):
            sensorNum = "0"+sensorNum #only if single digit
    elif "s" in sensorNum:
        sensorNum = sensorNum[1:]
    elif isSingleDigit(sensorNum) and sensorNum[0] != "0":
        sensorNum = "0"+sensorNum

    sensorString = "Sensor " + str(sensorNum)
    for r in api:
        if r['label'] == sensorString:
            loc = r['location']
            return (loc['x'], loc['y'])
        

def getEmitterCoords(row):
    """
    row: a row of data from fanchen_trilateration_2022_11_13.parquet dataframe
    or a dataframe of similar structure
    Returns: location of emitter as a tuple (latitude, longitude)
    Description: This function returns the location of an emitter given a row 
    of data from the trilateration dataframe 
    fanchen_trilateration_2022_11_13.parquet
    """
    refCoords = getCoordinates(row['ref_sensor'])
    emitterCoords = gLib.adjustedLongitude(refCoords, row['x'])
    return emitterCoords


#check if a number is single digit or not
def isSingleDigit(num):
    """
    num: this parameter can be of type integer, float, or string but
    will be converted to an integer value before calculation.
    Return: returns true if num can be represented as a single digit, false if otherwise
    Description: If num is a float, it will be rounded to the nearest whole number, 
    and then calculations will proceed. We basically figure out if the inputted 
    number is a single digit or not.
    """
    if type(num) == float:
        num = round(num)
    num = int(num)
    count = 0
    while num != 0:
        num //= 10
        count += 1
    if count == 1:
        return True
    else:
        return False
    

def jprint():
    """
    Returns: Nothing
    Description: Prints out the MobIntel api in json format
    """
    text = json.dumps(api, sort_keys=True, indent=4)
    print(text)


def createTrilateratedMap(df, headCount, centralPoint, pathName, d=None, createCsv=False, oldVersion=False):
    """
    df: trilateration dataframe. ususally this is fanchen_trilateration_2022_11_13.parquet
    headCount: how many rows we want to plot
    centralPoint: where the center of the map will be focused on upon rendering
    pathName: The name of the file where the map will be. Must be an html path.
    d: radius of how far, in meters, we want to plot trilaterated point from the actual locations of emitters
    createCsv: a boolean that when true, creates a csv file, false will not create anything
    oldVersion: if true, we use old method of trilateration, if true we use newer version (new version is better)
    pathName: the file path where you want to create the map html file
    """
    subset = df.head(headCount)
    m = folium.Map(location=centralPoint, width=2000, height=900, zoom_start=15, max_zoom=21)
    sensorSet = set()
    emitterSet = set()
    data = list()
    subset.apply(lambda row: plotRowOnMap(row, sensorSet, emitterSet, data, m, d=d, createCSV=createCsv, oldVersion=oldVersion), axis=1)
    for sensor in sensorSet:
        folium.Marker(sensor, icon=folium.Icon(color="orange", icon="star")).add_to(m)
    for emitter in emitterSet:
        folium.Marker(emitter, icon=folium.Icon(color="red", icon="cloud")).add_to(m)
    m.save(pathName)
    webbrowser.open(pathName, new=2)