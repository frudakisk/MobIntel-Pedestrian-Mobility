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
distance_error_array = gl.localizationTest(grid, df500, emitter_locs)

while True:
  rand_row = random.randint(0,df500.shape[0] - 1) # picks number from 0 to size of dataframe - 1
  device_row = df500.iloc[rand_row] # gets random row
  position = device_row[0:2] # stores ref_sensor and x
  if emitter_locs[f'{int(position.iloc[1])}, {position.iloc[0]}'] != -1:
    emitter_grid_loc, best_localization_guess = gl.gridLocalization(grid, df500, emitter_locs, rand_row)
    print("Positions in question:\n", position)
    print("location of the position in question:\n", emitter_grid_loc)
    print("Showing best localization guesses\n", best_localization_guess)
    break

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
csvFile = "datasets/GridLibDriverGrid.csv"
testOutput = "datasets/GridLibDriverGridWithLocalization.csv"
gl.localizecsv(csvFilePath=csvFile, 
               csvOutputFilePath=testOutput,
               position = emitter_grid_loc,
               data = best_localization_guess)



#converting csv file to json file
csvFile = "datasets/GridLibDriverGridWithLocalization.csv"
jsonPath = "webDevelopmentFiles/interactiveGrid/grid_json.json"
gl.csvTojson(csvFile, jsonPath)



