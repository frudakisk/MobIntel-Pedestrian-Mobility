import sys
import pandas as pd
from geopy import distance
import random

sys.path.append("pythonFiles")

from Functionality import GridLib as gl

df500 = pd.read_csv("datasets/block_500_only.csv", engine='python')
df500 = df500.drop(columns=("Unnamed: 0"))
origin = (26.713378, -80.05693981171936)

#adjusted latitude
newLoc = gl.adjustedLatitude(origin, 20)
#print(newLoc)
#print(distance.distance(newLoc, origin).meters)

#adjusted longitude
newLoc = gl.adjustedLongitude(origin, 20)
#print(newLoc)
#print(distance.distance(newLoc, origin).meters)

#visualize grid
m = gl.visualizeGrid(origin=origin, lat_dist=25, long_dist=5, 
                     meridianDist=1, parallelDist=1)
#gl.showGrid(m, "media/maps/driverGrid.html")

#create grid
latList, longList = gl.createGrid(origin=origin, latDistance=25, longDistance=5,
                                  adjustedMeridianDistance=1, adjustedParallelDistance=1)
#print(latList)
#print("Length of latList: ", len(latList))
#print(longList)
#print("length of longList: ", len(longList))

#The following short block of code is a representatation of how these functions should work together.
#functions such as containsSensor, sensorMaxCoords, sensorLocationsDict, and averageActualRSSI are all used as
#subfunctions to the following block
coords_array = gl.makeCoordsArray(latList, longList) # makes 2D array with all lat/long
grid_corners = gl.getGridCorners(coords_array) # stores the corner coordinates of all grid squares
emitter_coords = gl.getEmitterCoords(df500) # finds the coordinates of the all emitters
emitter_locs = gl.getEmitterPositions(emitter_coords, latList, longList, grid_corners) # gets the location of emitters with in the grid
grid = gl.makeGrid(grid_corners, latList, longList, emitter_locs, df500) # creates grid composed of GridSquare objects
#distance_error_array = gl.localizationTest(grid, df500, emitter_locs)

# while True:
#   rand_row = random.randint(0,df500.shape[0] - 1) # picks number from 0 to size of dataframe - 1
#   print("This is the random row selected\n", rand_row)
#   device_row = df500.iloc[rand_row] # gets random row
#   position = device_row[0:2] # stores ref_sensor and x
#   if emitter_locs[f'{int(position.iloc[1])}, {position.iloc[0]}'] != -1: #emitter_locs is a dictionary with a string as the key, and grid loc as value
#     emitter_grid_loc, best_localization_guess = gl.gridLocalization(grid, df500, emitter_locs, rand_row)
#     print("This is emitter_locs: ", emitter_locs)
#     print("Positions in question:\n", position)
#     print("device row:\n", device_row)
#     print("location of the position in question:\n", emitter_grid_loc)
#     print("Showing best localization guesses\n", best_localization_guess)
#     break

#Print out all the positions that have an emitter in it
#get all grid locations that have an emitter in it
activeEmitters = gl.getActiveEmitterLocs(emitter_locs=emitter_locs)
print("showing active emitters in the grid")
print(activeEmitters)
localizationList = gl.gridLocalization(grid, df500, activeEmitters)
print("locations of the positions in question & its best localization guesses\n")
for item in localizationList:
    print(item[0]) #should be just toe emitterLoc
    print(item[1])


print("Showing all locations that have a sensor in it")
for i in range(len(grid)):
    for j in range(len(grid[i])):
        tile = grid[i][j]
        if tile.hasSensor:
            print(tile.location)

# The following block demonstrates the gridLocalization function
# For now, it outputs a single tuple representing a cell of the grid
#estimated_device_loc = gl.gridLocalization(grid, df500, emitter_locs)
#print(estimated_device_loc)

#export grid as csv
gl.exportGridAsCsv(grid=grid, pathName="datasets/GridLibDriverGrid.csv")

# #localizing csv file
#This function will not work right now because we now have a list of data
#we need to put in a csv file. So needs to be updated to take
#localizationlist and write all data from it
csvFile = "datasets/GridLibDriverGrid.csv"
testOutput = "datasets/GridLibDriverGridWithLocalization.csv"
gl.localizecsv(csvFilePath=csvFile, 
               csvOutputFilePath=testOutput,
               localizationData=localizationList)



#converting localized csv file to json file
csvFile = "datasets/GridLibDriverGridWithLocalization.csv"
jsonPath = "webDevelopmentFiles/interactiveGrid/grid_json.json"
gl.csvTojson(csvFile, jsonPath)



