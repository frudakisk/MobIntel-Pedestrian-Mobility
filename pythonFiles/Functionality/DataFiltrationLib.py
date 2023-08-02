import pandas as pd
from datetime import datetime, date, timedelta

df500 = "datasets/block_500_only.csv"

def read_file(filepath):
    """
    filepath: a parquet file that is of the form of a MobIntel sensor file
    This functions reads in relevant data from a mobIntel parquet file
    and returns a dataframe
    """
    # only reads relevant columns from file, faster
    probe = pd.read_parquet(filepath, columns=["sensorid", "machash",
                                                "isphysical", "probingtime",
                                                "rssi"])
    # changes some data types to improve speed, lower memory cost
    probe = probe.astype({"sensorid": "int8", "isphysical": "int8", "rssi": "int16"})

    return probe

# removes physical devices and irrelevant columns
def sensor_trim(probe):
    """
    probe: a dataframe that has an 'isphysical' field, where it is either 0 or 1
    Filters out physical devices from a sensor parquet file and returns the 
    new dataframe without isphysical == 1
    """
    probe_sorted = probe.loc[probe["isphysical"] != 1] # drop all physical MAC addresses
    probe_filtered = probe_sorted.drop(columns =["isphysical"]).reset_index() # drop irrelevant columns
    return probe_filtered


def mac_count(pqfile, cutoff):
    """
    pqfile: a parquet file that represents data from a mobIntel sensor
    cutoff: the cutoff integer number that tells us how many of the same machashes
    we will be accepting before removing it from dataframe
    returns: a new df with hopefully less rows than inputted df.
    Counts mac addresses and removes outlier above cutoff number. Retains
    speed even on smaller cutoffs but does not store actual count of machashes
    """

    # counts mac hash occurences, sets to true if greater than filter, false if not
    mac_count = pqfile.groupby("machash").count() > cutoff

    # gets all mac hashes that do not occur more than filter number
    filtered_list = mac_count.loc[mac_count["sensorid"] == False]
    # does inner merge on list, compares original data to list without outliers
    outliers_removed = pd.merge(pqfile, filtered_list, how="inner", on = "machash")

    # removes and renames irrelevant columns created by merge
    outliers_removed = outliers_removed.drop(columns = ["sensorid_y", "probingtime_y",
                                            "rssi_y"])
    outliers_removed = outliers_removed.rename(columns={"sensorid_x":"sensorid",
                                            "probingtime_x": "probingtime",
                                            "rssi_x": "rssi"})

    return outliers_removed

def groupByMacHash(df):
    """
    df: a dataframe that has a machash field and a probingtime field
    return: a dataframe that where each row is a different machash and has a list of all that
    machashes probetimes
    This function restructures our sensor dataframe and give a separate row for each unique machash found in the
    dataframe. It then collects all the probing times that were assocaited with a machash and stores it as a list
    in a new column
    """
    #A Dataframe that includes the machash and a list of all the probing times for that machash
    return df.groupby(['sensorid', 'machash']).agg({'probingtime':list}).reset_index()


#Creates and returns a dictionary where a date is the key and the values is a list of timestamps (probingTimes)
#Works only with dataframe that has a column of a list of timestamps
def newDateCollector(row):
    """
    row: a row from the mobIntel sensor dataframe that has a 'probingtime' column
    Returns: dictionary where a date is the key and the values are a list of timestamps (probingTimes)
    This function only works with a dataframe that has a column of a list of timestamps
    """
    dateDict = {}
    #create just a list for the specific row
    probingTimeList = row["probingtime"]
    for probingTime in probingTimeList:
        date = probingTime.date()
        if date in dateDict:
            dateDict[date].append(probingTime.time())
        else:
            dateDict[date] = [probingTime.time()]
    return dateDict


#find the total time a device was within the area of a probe.
#Also keeping in mind the threshold for how big of a difference there should not be between pings to be
#considered still in the area of the sensor
def deviceInSensorAreaDuration(probingTimes, DURATION_LIMIT):
    DURATION_LIMIT = timedelta(minutes=DURATION_LIMIT)
    duration = timedelta(0,0)
    count = len(probingTimes)
    if count <= 1:
        #Only one probing time for this device found, cannot determine duration
        return duration.total_seconds()
    else:
        for i in range(count):
            if (i+1) < count:
                #get the absolute value - times should be in order anyways
                if probingTimes[i+1] > probingTimes[i]:
                    current_duration = (datetime.combine(date.today(), probingTimes[i+1]) - datetime.combine(date.today(), probingTimes[i]))
                    if current_duration < DURATION_LIMIT:
                        duration = duration + current_duration
                    # else:
                    #     print("REACHED DURATION_LIMIT")
                else:
                    current_duration = (datetime.combine(date.today(), probingTimes[i]) - datetime.combine(date.today(), probingTimes[i+1]))
                    if current_duration < DURATION_LIMIT:
                        duration = duration + current_duration
                    # else:
                    #     print("REACHED DURATION_LIMIT")
        return duration.total_seconds()


#Creates the information that will be put in a new column of a dataframe
#Using the deviceInSensorAreaDuration(), we capture the duration of each row and put them in
#dictonary format incase a machash appears on different days
def newDetermineDuration(row, durationLimit):
    dateDict = newDateCollector(row)
    if len(dateDict.keys()) > 1 :
        #make len(keys) rows for same machash - just different days
        #I think the better way to do this is to have duration be an object rather than just a number
        #An example object would be a dictionary with the date as the key and the duration on that date as the value
        durationDict = {}
        keyList = list(dateDict.keys())
        for i in range(len(keyList)):
            duration = deviceInSensorAreaDuration(dateDict[keyList[i]], durationLimit)
            durationDict[keyList[i]] = duration
        return str(durationDict)
    else:
        durationDict = {}
        #get the date which is the only key value
        key = list(dateDict.keys())[0]
        #get the value from the only key in the dictionary (should be a list [] of probingtimes)
        probingTimesList = list(dateDict.values())[0]
        duration = deviceInSensorAreaDuration(probingTimesList, durationLimit)
        durationDict[key] = duration
        return str(durationDict)
    

def determineMacHashDuration(filename):
    """
    filename: a mobIntel parquet file
    returns: a dataframe that contains all the probing times for a machash in a single row
    A combination of functions so that we have a one liner whenever we want to
    find the duration of machashes
    """
    df = read_file(filename)
    df = sensor_trim(df)
    df = groupByMacHash(df)
    df["Duration"] = df.apply(lambda row : newDetermineDuration(row, 7), axis=1)
    return df

def getSubsetByRefSensorAndX(refSensor, x):
    """
    refSensor: an integer that repesents a reference sensor in the 
    block_500_only.csv
    x: an integer that represents the distance the emitter is from the refSensor,
    but is also a column in the block_500_only.csv
    This function returns a data frame that is a subset of the same ref sensor
    column and x column
    """
    df = pd.read_csv(df500)
    newDf = df.query("ref_sensor == @refSensor & x == @x").copy()
    return newDf
