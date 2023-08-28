"""
This file containts functions that dealt with converting an RSSI value to a 
distance (meters). The main component of these functions are the lookup tables that
were developed by doing a lot of averaging of rssi data. Trilateration required us
to conert an RSSI value to a distance, and because of this, trilateration did not
give us the results we required. In short, it is very difficult to get an accurate
conversion from and RSSI value to a distance - more information is required.
"""

import pandas as pd
import statistics

#Global Variables
lookupTable = pd.read_csv("datasets/rssiToDistanceCorrelation.csv", index_col=[0])
lookupTableV2 = pd.read_csv("datasets/rssiToDistanceCorrelation_V2.csv")


#Use the lookup table to convert an rssi value to a distance
def rssiToDistance(rssi):
    """
    rssi: an rssi value that is use to covert to distance
    Return: a distance in meters
    Description: using the old imported lookup table, we convert an rssi value (negative integer)
    to a distance. This version uses the lookupTable_V1 and provides some compensation
    for rssi values outside of its bounds. For rssi values higher than -46, we return a distance of 1m
    For rssi values lower than -94, we return a distance of 500m"""

    df = lookupTable[lookupTable["mean_mean_rssi"] == rssi]

    if rssi > -46:
        return 1.0
    elif rssi < -94:
        return 500.0 #I should do some better estimation, but this is good for now
    elif df.empty:
        #look for row that has rssi next highest
        while(True):
            rssi = rssi-1
            r = lookupTable[lookupTable["mean_mean_rssi"] == rssi]
            if r.empty:
                continue
            else:
                break
        #find index in table that has this rssi value
        index = lookupTable[lookupTable["mean_mean_rssi"] == rssi].index
        lowerIndex = index[0]
        upperIndex = lowerIndex+1
        #get the distance values at these two indexes and find the median of them
        dist1 = lookupTable[lookupTable.index == lowerIndex]
        dist2 = lookupTable[lookupTable.index == upperIndex]
        medianDistance = statistics.median([dist1.iloc[0]['mean_distance'], dist2.iloc[0]['mean_distance']])
        return medianDistance
    else:
        return df.iloc[0]["mean_distance"]

#----------------------------------------------------
def rssiToDistanceV2(rssi):
    """
    rssi: an rssi value that is used to convert to distance 
    Return: a distance in meters
    Description: This is version 2 of converting an rssi value to a distance.
    We utilize the lookupTable_V2 file to do this conversion.
    There will be no lower bounds for this version since we will not be accepting
    rssi values lower than -61.
    Therefore, we should only give this function values above or equal to -61.
    This function performs slightly better than the previous version"""

    df = lookupTableV2[lookupTableV2["mean_mean_rssi"] == rssi]

    if rssi > -46:
        return 1.0
    elif rssi < -61:
        #rssi values lower tha -61 are not considered when converting. resulting in 30m
        return 30.0
    elif df.empty:
        #look for row that has rssi next highest
        while(True):
            rssi = rssi-1
            r = lookupTableV2[lookupTableV2["mean_mean_rssi"] == rssi]
            if r.empty:
                continue
            else:
                break
        #find index in table that has this rssi value
        index = lookupTableV2[lookupTableV2["mean_mean_rssi"] == rssi].index
        lowerIndex = index[0]
        upperIndex = lowerIndex+1
        #get the distance values at these two indexes and find the median of them
        dist1 = lookupTableV2[lookupTableV2.index == lowerIndex]
        dist2 = lookupTableV2[lookupTableV2.index == upperIndex]
        medianDistance = statistics.median([dist1.iloc[0]['mean_distance'], dist2.iloc[0]['mean_distance']])
        return medianDistance
    else:
        return df.iloc[0]['mean_distance']
