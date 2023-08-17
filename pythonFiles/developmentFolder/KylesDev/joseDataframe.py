"""
This file will create a dataframe for Jose in the format that is required for his practice.
He is requiring there to be 9 columns that have the rssi values of sensors
a tx_coord column, which is essentially the location of the emitter in our grid
a class label column, which would just be the number of the tile

Steps:
1. Create 170x20 Grid - with all its quirks (center, location, is_emitter, etc)
2. Find coordinate locations of the 9 emitters by starting with the x and ref_sensor columns of block_500_only.csv
3. Figure out what tile location each emitter is at. This should be a function from (x, ref_sensor) -> tile location
4. Capture tile location index as class_label
5. New dataframe will have tile location, rssi from 9 sensors, and class_label instead of x ,ref_sensor, rssi from 9 sensors
"""

import sys, os
sys.path.append('pythonFiles')

from Functionality import GridLib as gl, DataFiltrationLib as dl, Constants as c
import pandas as pd

origin = (26.71333451697524, -80.05695531266622)


def transformData(row, newDataList, activeEmitters, gridTable):
    """
    row: a row from the df500 dataframe
    newDataList: a list to hold dictionaries of data for a dataframe
    activeEmitters: a dictionary that contains the reference location of the emitter
    gridTable: The current grid object we are referencing for tile locations
    as the key, and the tile location as the value
    returns: new list of data prepared for a dataframe
    This function will turn a row from the df500 dataframe into a row for 
    joses dataframe requirements. Each row should be saved into the newDataList. What is required is a tx_coord column, which is the
    tile location of an emitting device, rssi values from 9 recievers, and a class_label,
    which is ultimatly the index number of each row in df500 that has an emitter in it
    """
    newRowData = {}
    ref_sensor = str(row["ref_sensor"])
    ref_sensor = ref_sensor[:-2]
    rowReference = f"{ref_sensor}, {row['x']}"
    #find the value with the appropriate key
    for key, value in activeEmitters.items():
        if str(key) == str(rowReference):
            newRowData["tx_coord"] = value
            #use this value to dtermine class_label number
            v = str(value)
            r = gridTable.query("location == @v")
            for index, rData in r.iterrows():
                newRowData["class_label"] = int(index)
            break

    #get sensor rssi data
    sensorData = row[3:]
    i = 0
    for data in sensorData:
        keyName = "receiver_" + str(i)
        newRowData[keyName] = data
        i += 1

    #add dictionary to list
    newDataList.append(newRowData)

#turn this whole process into one function
def fanchenToJoseData(inputFileName, outputFileName, gridFileName, gridOrigin):
    """
    inputFileName: The file path of the block data 
    outputFileName: the output file path for the jose version of the data
    gridOrigin: the origin of the grid that is used for the data in the
    inputFileName construction

    Returns: a csv file in the JoseData format

    Description: This function takes in a csv file in the block500 format that
    Phillip creates. We then perform some functions on this file to convert it 
    to the format that Jose needs for his machine learing process. Currently,
    we are static with the grid side and spacing. We can add parameters for
    that stuff later...
    """
    #read the inputFileName as a df and rename index column
    df = pd.read_csv(inputFileName)
    df = df.rename(columns={"Unnamed: 0": "class_label"})

    #create the grid structure that will use the data from the df
    grid_tuple = gl.completeGrid(origin= gridOrigin,
                latDistance= 170,
                longDistance= 25,
                adjustedMeridianDistance= 1,
                adjustedParallelDistance= 1,
                df500= df)
    
    activeEmitters = gl.getActiveEmitterLocs(emitter_locs=grid_tuple[1])

    #make csv file for this grid
    gl.exportGridAsCsv(grid=grid_tuple[0], pathName=gridFileName, withIndex=False)

    #read same file
    df_grid= pd.read_csv(gridFileName)

    joseData = []
    df.apply(lambda row: transformData(row, joseData, activeEmitters, df_grid), axis=1 )
    josedf = pd.DataFrame(data=joseData)
    print(josedf) #can remove this line

    #change the order of the columns just to have same layout as Joses data
    josedf = josedf.iloc[:,[0,2,3,4,5,6,7,8,9,10,1]]

    print(josedf) #can remove this line

    josedf.to_csv(outputFileName, index=False)

    print("THIS IS THE NEW JOSE DATA")
    test = pd.read_csv(outputFileName) #we can remove this line
    print(test)


#main - call this function
# fanchenToJoseData(inputFileName="datasets/block_500_11_16.csv",
#                     outputFileName="datasets/JoseData_11_16.csv",
#                     gridFileName="datasets/170x25LargeGrid_11_16.csv",
#                     gridOrigin=origin)


#need to convert each file from RSSI_localization_data_WPB to a block_500 format
directory = "datasets/RSSI_localization_data_WPB"
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    if os.path.isfile(f):
        print(f"Starting processing of file: {f}")
        date = f[-14:-4]
        block_500, block_400 = dl.convertFanchen(fanchenFileName=f)
        save_filename = f"datasets/DataForJose/block_500_{date}.csv"
        block_500.to_csv(save_filename)
        if not block_500.empty: #if the block data is not empty, convert
            #convert each of the block 500 format csv files into a jose file
            joseOutputName = f"datasets/DataForJose/JoseData_{date}.csv"
            gridFileName = f"datasets/DataForJose/170x25LargeGrid_{date}.csv"
            fanchenToJoseData(inputFileName=save_filename,
                            outputFileName=joseOutputName,
                            gridFileName=gridFileName,
                            gridOrigin=c.GRID_170x25_ORIGIN)
            print(f"Done with file: {f}")
print("Processing complete!")