import sys, matplotlib.pyplot as plt, pandas as pd, numpy as np

sys.path.append("pythonFiles")

from Functionality import MLLib as mll, DataFiltrationLib as dfl

#requires the groupby dataframe and the date to look for
def createLineGraph(df, date, dayByDay=False):
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
    For each rssi value, capture the count of the distances
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
    get all the rssi values in a set
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
    """
    df = dfl.read_file(filename) #read and remove useless columns
    df = dfl.sensor_trim(df) #filters out isphysical == 1
    #Remove duplicate probingtimes - too many in one second & don't represent devices
    df.drop_duplicates(subset="probingtime", keep="first", inplace=True)
    #aggregate the data by hour per day
    hourAgg = df.groupby(pd.Grouper(key="probingtime", axis=0, freq="h", sort=True)).count()
    return hourAgg


def plotDateAgg(dateAgg):
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
    hourAgg: use hourAggDf tp make this variable
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
    This block presents each day of the week in separate graphs
    """
    for timestamp in dateAgg.index:
        date = timestamp.date()
        df = hourAgg[hourAgg.index.date == date]
        plt.figure(figsize=(10, 4.8))
        createLineGraph(df, date, dayByDay=True)