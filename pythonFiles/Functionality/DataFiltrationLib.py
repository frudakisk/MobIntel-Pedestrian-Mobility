"""
This file is meant to hold functions that pertain to filtering out data that is not
necessarily needed for our purposes. The MobIntel data files contain millions of rows
but not all of them are things that we need, so to make processing easier, we filter out
data.
"""

import pandas as pd
from datetime import datetime, date, timedelta

df500 = "datasets/block_500_only.csv"

# removes physical devices
def sensor_trim(probe):
    """
    probe: a pandas dataframe that has an 'isphysical' field, where it is either 0 or 1
    Returns: a dataframe where all rows have isphysical == 0
    Description: Filters out physical devices from a sensor parquet file and returns the 
    new dataframe without isphysical == 1. We then remove the 'isphysical' column and reset the 
    index values.
    """
    probe_sorted = probe.loc[probe["isphysical"] != 1] # drop all physical MAC addresses
    probe_filtered = probe_sorted.drop(columns =["isphysical"]).reset_index(drop=True) # drop irrelevant columns
    return probe_filtered

def read_file(filepath):
    """
    filepath: a parquet file that is of the form of a MobIntel sensor file
    Returns: a pandas dataframe object
    Description: This functions reads in relevant data from a mobIntel parquet file
    and returns a dataframe while also keeping relevant columns of data. We also
    change some data types to improve speed and memory cost
    """
    try:
        # only reads relevant columns
        probe = pd.read_parquet(filepath, columns=["sensorid", "machash",
                                                "isphysical", "probingtime",
                                                "rssi"])
    # if file is not parquet, catch error, and return -1
    except: 
        print("Incorrect file type. Please enter a parquet file")
        return -1

    # change some data types to improve speed/memory
    probe = probe.astype({"sensorid": "int8", "isphysical": "int8", "rssi": "int16"})

    # call sensor_trim to remove physical devices
    probe = sensor_trim(probe)

    return probe

def mac_count(pqfile, cutoff):
    """
    pqfile: a parquet file that represents data from a mobIntel sensor
    cutoff: the cutoff integer number that tells us how many of the same machashes
    we will be accepting before removing it from dataframe
    returns: a new df with hopefully less rows than inputted df.
    Description: Counts mac addresses and removes outlier above cutoff number. Retains
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

# This function reads in data from MobIntel, filters it, and creates a merged
# dataframe. The grid creation code and its subsequent functions assumes it has
# a dataframe with two columns of whatever information 
# (in the case of MobIntel: machash and probingtime) followed by columns
# containing RSSI values. These columns should also be named after the sensor 
# that received these RSSI values. 
# DO NOT USE FOR FANCHEN DATA, use convertFanchen function for that
def dataInitialization():
  # creates initial empty dataframe
  all_data = pd.DataFrame()

  # loop to read, filter, and merge however many data files are entered
  while True:
    # enter a file name
    file_name = input("Enter file name or enter X to end: ").strip()

    # if file_name = X, end loop
    if file_name == 'X' or file_name == 'x':
      break
    else:
      
      # read in files, remove unnecessary columns, remove phyiscal devices
      data = read_file(file_name) 

      # if file is not parquet, go back to start of loop
      if type(data) == int:
        continue
      
      # remove duplicate data 
      data = data.drop_duplicates(["machash", "sensorid", "probingtime"])

      # calls mac count function - removes machashes that appear too many times
      # (likely physical devices)
      data = mac_count(data, 500)

    # getting sensorid to rename "RSSI" column
    sensorid = data['sensorid'][0] 
    # if sensor is < 10, add a 0 to front (ex. 9 -> 09)
    if sensorid < 10:
      sensorid = '0' + str(sensorid)
    else:
      sensorid = str(sensorid)
    # drop sensorid column and rename rssi column to what the sensorid is 
    data = data.rename(columns={"rssi": sensorid}).drop(columns=["sensorid"])

    # if all data is empty dataframe, set new data equal to it
    if all_data.empty:
      all_data = data
    # otherwise, inner merge new data with all_data on machash and probingtime
    # this means all_data contains only rows that have the same machash and probingtime for multiple sensors
    else: 
      all_data = pd.merge(all_data, data, how ="inner", on=["machash","probingtime"])

  # return the final dataframe
  return all_data

def groupByMacHash(df):
    """
    df: a dataframe that has a machash field and a probingtime field (MobIntel datafile)
    returns: a dataframe where each row is a different machash and has a list of all that
    machashes probetimes
    Description: This function restructures our sensor dataframe and give a separate row for each unique machash found in the
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
    Description: This function only works with a dataframe that has a column of a list of timestamps.
    We can create this column of a list of timestamps with the groupByMacHash() function.
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
    """
    probingTime: A list of probing times
    DURATION_LIMIT: a timedelta object that represents how long (in minutes) we will wait for another signal
    Returns: a duration in second - how long of a difference between one probing time and another that does not exceed
    the duration limit
    Description: This function is meant to be used for data pertaining to one row that has a column of probing times
    This function fund the total time a device was within the area of a probe. It also
    keeps in mind the threshold for how long of a difference there should not be between pings to be considered
    still in the area of the sensor. This function is a helper function for newDetermineDuration
    """
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
    """
    row: a row from from the dataframe that is created from using the groupByMacHash function
    durationLimit: basically, how long (in minutes) we will wait for the next probing time
    Returns: a string representation of a dictionary that is to be a value in a new column of data in new data frame.
    This value represents how long that machash in the same row was within the area of the MobIntel sensor.
    Description: The functions is meant to be used for a lambda function on our mobintel data. 
    It creates a the information that will be put in a new column of a dataframe. Using the deviceInSensorAreaDuration(),
    we capture the duration of each row and put them in dictionary format incase a machash appears on different days.
    """
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
    Description: A combination of functions so that we have a one liner whenever we want to
    find the duration of machashes. This is so that a user does not have to call all these functions
    separately if they do not have to
    """
    df = read_file(filename)
    df = groupByMacHash(df)
    df["Duration"] = df.apply(lambda row : newDetermineDuration(row, 7), axis=1)
    return df

def getSubsetByRefSensorAndX(blockDataFile, refSensor, x):
    """
    blockData: This is a csv file that represents data captured in our block data format,
    which takes inspiration from the data that Fanchen Bao collected which can be found in 
    RSSI_localization_Data_WPB. This data format is created by using the convertFanchen() function
    refSensor: an integer that repesents a reference sensor in the 
    blockData csv format
    x: an integer that represents the eastward distance the emitter is from the refSensor,
    but is also a column in the blockData csv format
    Returns: This function returns a data frame that is a subset of the same ref sensor
    column and x column
    Description: This function reads in a csv file in the blockData format, and queries a subset of data
    from it where the ref_sensor column and x column match the query parameters. This function is to only
    be used on Fanchens data because mobintel data can never tell us the actual location of emitting devices
    """
    df = pd.read_csv(blockDataFile, index_col=[0])
    newDf = df.query("ref_sensor == @refSensor & x == @x").copy()
    return newDf

def convertFanchen(fanchenFileName):
    """
    fanchenFileName: a csv file from the RSSI_localization_data_WPB folder. Each file is data collected from
    different days.
    Returns: two blockData csv dataframes. One for block 500 and the other for block 400
    Description: When Fanchen collected data, he only did so on blocks 500 and 400 on Clematis Street.
    So, only the sensors in those two blocks can be referenced. we get easy to understand information about
    the data collected and can use it for multiple applications such as trilateration and localization
    """
    # block reads and organizes fanchen's dataset, renames sensor ids to actual

    #fanchen_data should read from datasets/RSSI_localization_data_WPB/2022_11_XX.csv
    fanchen_data = pd.read_csv(fanchenFileName)
    # drops unnecessary columns, converts datatypes to smaller format, renames column
    fanchen_data = fanchen_data.drop(columns=["label"])
    fanchen_data = fanchen_data.astype("float32")
    fanchen_data = fanchen_data.astype({"emitter":"int16","lamp_post":"int16"})
    fanchen_data = fanchen_data.rename(columns={"lamp_post": "ref_sensor"})
    fanchen_data = fanchen_data.loc[(fanchen_data['x'] != 20) & (fanchen_data['x'] != 24)]

    # separates raw data into different dataframes based on their location
    north_west = fanchen_data[(fanchen_data["class"] == 1) & (fanchen_data["city_block"] == 500)]
    south_west = fanchen_data[(fanchen_data["class"] == 0) & (fanchen_data["city_block"] == 500)]
    north_east = fanchen_data[(fanchen_data["class"] == 1) & (fanchen_data["city_block"] == 400)]
    south_east = fanchen_data[(fanchen_data["class"] == 0) & (fanchen_data["city_block"] == 400)]

    # renames all the ref sensors from unhelpful 1-6 to their actual ID
    north_west["ref_sensor"].loc[north_west["ref_sensor"] == 0] = 57
    north_west["ref_sensor"].loc[north_west["ref_sensor"] == 1] = 20
    north_west["ref_sensor"].loc[north_west["ref_sensor"] == 2] = 4
    north_west["ref_sensor"].loc[north_west["ref_sensor"] == 3] = 54
    north_west["ref_sensor"].loc[north_west["ref_sensor"] == 4] = 5
    north_west["ref_sensor"].loc[north_west["ref_sensor"] == 5] = 40
    north_west["ref_sensor"].loc[north_west["ref_sensor"] == 6] = 34

    south_west["ref_sensor"].loc[south_west["ref_sensor"] == 0] = 22
    south_west["ref_sensor"].loc[south_west["ref_sensor"] == 1] = 6
    south_west["ref_sensor"].loc[south_west["ref_sensor"] == 2] = 42
    south_west["ref_sensor"].loc[south_west["ref_sensor"] == 3] = 31
    south_west["ref_sensor"].loc[south_west["ref_sensor"] == 4] = 33
    south_west["ref_sensor"].loc[south_west["ref_sensor"] == 5] = 36
    south_west["ref_sensor"].loc[south_west["ref_sensor"] == 6] = 35

    north_east["ref_sensor"].loc[north_east["ref_sensor"] == 0] = 11
    north_east["ref_sensor"].loc[north_east["ref_sensor"] == 1] = 28
    north_east["ref_sensor"].loc[north_east["ref_sensor"] == 2] = 7
    north_east["ref_sensor"].loc[north_east["ref_sensor"] == 3] = 50
    north_east["ref_sensor"].loc[north_east["ref_sensor"] == 4] = 8
    north_east["ref_sensor"].loc[north_east["ref_sensor"] == 5] = 21

    south_east["ref_sensor"].loc[south_east["ref_sensor"] == 0] = 39
    south_east["ref_sensor"].loc[south_east["ref_sensor"] == 1] = 38
    south_east["ref_sensor"].loc[south_east["ref_sensor"] == 2] = 56
    south_east["ref_sensor"].loc[south_east["ref_sensor"] == 3] = 55
    south_east["ref_sensor"].loc[south_east["ref_sensor"] == 4] = 53
    south_east["ref_sensor"].loc[south_east["ref_sensor"] == 5] = 27
    south_east["ref_sensor"].loc[south_east["ref_sensor"] == 6] = 25

    # gets all info from block 500, keeps only sensors in that block, drops empty columns
    block_500_sensors = ['s57', 's20', 's04', 's54', 's05', 's40', 's34', 's22', 's06', 's42', 's31', 's33', 's36', 's35']
    block_500 = pd.merge(south_west, north_west, how='outer').drop(columns=['city_block', 'class'])
    block_500 = block_500[['x','ref_sensor','s57', 's20', 's04', 's54', 's05', 's40', 's34', 's22', 's06', 's42', 's31', 's33', 's36', 's35']]
    block_500 = block_500.dropna(how="all", axis=1)

    # gets all info from block 400, keeps only sensors in that block, drops empty columns
    block_400_sensors = ['s11', 's28', 's07', 's50', 's08', 's21', 's39', 's38', 's56', 's55', 's53', 's27', 's25']
    block_400 = pd.merge(south_east, north_east, how='outer').drop(columns=['city_block', 'class'])
    block_400 = block_400[['x','ref_sensor','s11', 's28', 's07', 's50', 's08', 's21', 's39', 's38', 's56', 's55', 's53', 's27', 's25']]
    block_400 = block_400.dropna(how="all", axis=1)

    return block_500, block_400
