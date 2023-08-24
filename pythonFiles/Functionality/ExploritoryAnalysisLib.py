"""
This file contains functions that were used to explore the data in the mobintel
sensor files as well as the parking lot experiment data (sampled_source_data.csv).
In this file, we can find a lot of plots and data separation. Any future functions
that deal with anaylzing files of data should go here.
"""

import sys, matplotlib.pyplot as plt, pandas as pd, numpy as np

sys.path.append("pythonFiles")

from Functionality import MLLib as mll, DataFiltrationLib as dfl

#requires the groupby dataframe and the date to look for
def createLineGraph(df, date, dayByDay=False):
    """
    df: a df that contains a subset of data by date from dateAggDf or HourAggDf
    date: a timestamp object 
    dayByDay: If False, we focus on creating one plot that has all hours of each day
    in the given data frame. If True, we focus on each day and look at all hours of 
    each day separately
    Returns: A matplotlib graph object
    Description: This function requires a a dataframe made from the groupBy functions
    of either dateAggDf or HourAggDf. This function is a helper function for 
    plotInDepthWeek or plotDays
    """
    plt.plot(np.array(df.index), np.array(df["sensorid"].values))
    plt.xlabel("Day")
    plt.ylabel("Count of Devices")
    plt.title("Count of devices per hour on a week")
    if dayByDay == True:
      plt.xlabel("Hour")
      plt.title("Count of devices on " + str(date))
      plt.show()


def distanceCounter(dataframe):
    """
    dataframe: I'm not sure what kind of df goes in here, but it should have a
    distance column.
    Returns: a dictionary that keeps track of how many times a distance occured
    Description: For each rssi value, capture the count of the distances
    """
    dict = {}
    for distance in dataframe["Distance"]:
        if distance not in dict:
            dict[distance] = 1
        else:
            dict[distance] += 1
    return dict

def rssiSet():
    """"
    returns: all the unique rssi values from the parking lot experiment
    Description: get all the unique rssi values in a set. This function focuses on the 
    parking lot experiment data (sampled_source_data.csv) and collects all the 
    unique rssi values in a set
    """
    s1 = mll.sensorDistance("s1")
    s2 = mll.sensorDistance("s2")
    s3 = mll.sensorDistance("s3")
    s4 = mll.sensorDistance("s4")
    sList = ['s1', 's2', 's3', 's4']
    sensorList =[s1, s2, s3, s4]
    for i in range(len(sList)):
        df = mll.createDataFrame(sList[i], sensorList[i])

    s = set((df["RSSI_Value"]))
    return s

def dateAggDf(filename):
    """
    filename: a mobintel sensor parquet file
    returns: a dataframe where we aggregate it by the date
    Description: a dataframe where the data is aggregated by days, which comes from
    the probingtime column in the sensor data files.
    """
    df = dfl.read_file(filename) #read and remove useless columns
    df = dfl.sensor_trim(df) #filters out isphysical == 1
    #Remove duplicate probingtimes - too many in one second & don't represent devices
    df.drop_duplicates(subset="probingtime", keep="first", inplace=True)
    #aggregate the data by dates
    dateAgg= df.groupby(pd.Grouper(key='probingtime', axis=0, freq="D", sort=True)).count()
    return dateAgg

def hourAggDf(filename):
    """
    filename: a mobintel sensor parquet file
    returns: a dataframe where we aggregate it by the hour
    Description: a dataframe is created where the data is aggregated by the hour of
    each day, which comes from the probingtime column in the sensor data files.
    """
    df = dfl.read_file(filename) #read and remove useless columns
    df = dfl.sensor_trim(df) #filters out isphysical == 1
    #Remove duplicate probingtimes - too many in one second & don't represent devices
    df.drop_duplicates(subset="probingtime", keep="first", inplace=True)
    #aggregate the data by hour per day
    hourAgg = df.groupby(pd.Grouper(key="probingtime", axis=0, freq="h", sort=True)).count()
    return hourAgg


def plotDateAgg(dateAgg):
    """
    dateAgg: sensor data that was turned into a data frame that was aggregated
    by days
    Returns: a plot of the data with x-axis as the day and y-axis as a count
    Description: Visualizes the data when it is aggregated by days. We are counting
    the number of probe request that happen on each day for this week of data.
    """
    #This block presents the entire week in a general sense
    #Create a line graph of dates
    plt.figure(figsize=(10, 4.8))
    plt.plot(np.array(dateAgg.index), np.array(dateAgg['sensorid'].values))
    plt.xlabel("Dates")
    plt.ylabel("Count of probe request")
    plt.title("Day vs. Count")
    plt.show()


def plotInDepthWeek(dateAgg, hourAgg):
    """
    dateAgg: use dateAggDf to make this variable
    hourAgg: use hourAggDf to make this variable
    Returns: a plot that shows the data by the hour but shows the entire week
    Description: The returned plot uses is a more detailed version of plotDateAgg 
    because we are not generalizing the days and are focusing in on the hours within
    the days
    """
    #This block presents one graph of the entire week
    plt.figure(figsize=(15, 4.8))
    for timestamp in dateAgg.index:
        date = timestamp.date()
        df = hourAgg[hourAgg.index.date == date]
        createLineGraph(df, date, dayByDay=False)
    plt.show()


def plotDays(dateAgg, hourAgg):
    """
    dateAgg: use dateAggDf to make this variable
    hourAgg: use hourAggDf tp make this variable
    Returns: several graphs that focus on the hours of just one day each.
    Description: This block presents each day of the week in separate graphs. We 
    plot out one day out of the week and show the probe request count per hour on
    that day. Then we make a new plot for the next day and so on until we are done.
    """
    for timestamp in dateAgg.index:
        date = timestamp.date()
        df = hourAgg[hourAgg.index.date == date]
        plt.figure(figsize=(10, 4.8))
        createLineGraph(df, date, dayByDay=True)