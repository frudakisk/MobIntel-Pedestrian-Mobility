"""
This file will contain a general workflow from raw mobintel data to localizing mobile devices on 
Clematis Street. In order to do this, we need to create grid structures along the street. I was thinking
about making a separate grid for each street block because then the localization might be more accurate.
But at the same time, we cannot be 100% certain that the emitting device is within the grid we predict it to be in.

We could also make a giant grid that spans across the whole street, but since the street is slightly slanted, 
we will have to make up a lot of extra tiles. However, this MIGHT be okay if we are using that mini grid stuff that 
phillip is working on. 

Regardless of which route we are taking, it is still a good idea to build the testing framework. For testing purposes 
we should focus on one street block grid and try to see what we can do with a single mobintel data file.

For the data file, we would have to do our regular filtering process and then try to find the machashes that appear more
than once. I guess it's a good idea to see if we have some sort of machash probing multiple times
"""

import sys, pandas as pd

sys.path.append("pythonFiles")
from Functionality import DataFiltrationLib as dfl, GridLib as gl, Constants as c

df = dfl.read_file(filepath="datasets/1678683600000-sensor_1.parquet")
df = dfl.sensor_trim(probe=df)

grid0 = [c.GRID_BLOCK_500_ORIGIN, 170, 25, 1, 1]
grid1 = [c.GRID_BLOCK_400_ORIGIN, 140, 25, 1, 1]
grid2 = [c.GRID_BLOCK_300_ORIGIN, 162, 25, 1, 1]
grid3 = [c.GRID_BLOCK_200_ORIGIN, 115, 25, 1, 1]
listOfGrids = [grid0, grid1, grid2, grid3]

m = gl.multipleGrids(listOfGrids=listOfGrids, parentOrigin=c.GRID_BLOCK_400_ORIGIN)
gl.showGrid(m=m, filePath='media/maps/concatMap.html')

#What does one giant grid look like?
origin = (26.71322274321674, -80.05707291836983)
m = gl.visualizeGrid(origin=origin, 
                     lat_dist=640,
                     long_dist=35,
                     meridianDist=1,
                     parallelDist=1)
gl.showGrid(m=m, filePath='media/maps/giantMap.html')

#I should probably figure out how to collect machashes that appear multiple times at the same probing time

#see what sorting does first - sort by machash and then by probing time
df.sort_values(by=['machash', 'probingtime'])
print(df)

#since it is sorted, we can just go down the list
#I could just remove the rows that appear once in machash in probing time



#Go through the df and query each machash and probing time
#if there are multiple results in the query, grab those rows and store them in a separate df
#keep tabs on those index values
#remove the queried rows from the original df


countDict = {}
multipleDf = pd.DataFrame()
while(not df.empty):
    #query by machash and probingtime
    rowMachash = df.iloc[0]['machash']
    rowProbingTime = df.iloc[0]['probingtime']
    query = df.query("machash == @rowMachash and probingtime == @rowProbingTime")
    #store indexes
    l = list(query.index)
    #keep count of how many times a group size appears
    if len(l) not in countDict.keys():
        countDict[len(l)] = 1
    else:
        countDict[len(l)] = countDict[len(l)] + 1

    
    #check if there are multiple results in the query
    if len(l) > 1:
        #if there are multiple, add it to a dataframe
        multipleDf = pd.concat([multipleDf, query], axis=0).reset_index(drop=True)
    #regardless, remove the queried indexes from the original df, so that searching is faster
    df = df.drop(index=l)
    #reset index column for the df
    df.reset_index(inplace=True, drop=True)
    #just print it every 100 iterations
    if len(df) % 100 == 0:
        print(len(df))
        print(countDict)
        

print(multipleDf.head(300).to_string())
print(multipleDf)


# #check if there are multiple machashes for the same device id
# print("Starting process...")
# while(not df.empty):
#     #grab a deviceid
#     deviceid = df.iloc[0]['deviceid']
#     #collect all rows that have that device id and store those indexes
#     query = df.query("deviceid == @deviceid")
#     l = list(query.index)
#     #check if there are more than 1 unique machashes for this deviceid
#     uniqueMachashes = query['machash'].unique()
#     if len(uniqueMachashes) > 1:
#         print(f"device id {deviceid} has more than one machash associated with it!")
#     #remove the rows with the indexes we just took
#     df = df.drop(index=l)
#     #reset the index column for the df
#     df.reset_index(inplace=True, drop=True)
#     #print the size of the df
#     print(len(df))

# print("At this point we are done. Any prints come out of the while loop?")
    
