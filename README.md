# MobIntel-Project
talk about commenting standards and how to understand what each comment for each function means

## Project Description
This is where we will compile all out code that went towards this project. This project was working towards determining the trajectory of people along a street to help cities better plan for pandemics. With this kind of information, city planners could understand how people are moving and make precautions based on this information. As an overview, In our research, we encountered valuable insights regarding trilateration of RSSI values as a method for determining device positions. Recognizing its limitations, we boldly shifted our focus to exploring a promising new avenue—the grid system. While still in its developmental phase, the grid approach holds immense potential for revolutionizing our understanding of device positioning.​


## Table of Contents
1. How to Find Stuff
2. Libraries
3. Drivers
4. How to Use Libraries
5. other stuff

---

### How to Find Stuff

In this readme file, we have categorized the abundant information as follows: On the highest level of organization, we have several
parent folders that contain information. The parent folders are datasets, media, pythonFiles, and webDevelopmentFiles.
Within the datasets folder, we have all the data sets that were used during our project. It also includes datasets that we 
created during our project. Mostly, they were developed from pre existing data sets provided to us, but with analysis data added into them.
In the media folder, we include things such as images and maps. Images is self explanatory, but the maps section includes html files that were
generated via out trilateration algorithms, or our grid visualization efforts. The pythonFiles folder is the meat of this assignment. In here we have 3 seperate
subfolders; developmentFolder, Drivers, and Functionality. The developmentFolder is a sort of playground where each of the developers can play with some of the
code for development purposes. The Drivers folder contains python files that utilize the libraries developed throughout this process. It tests and makes sure that
any updates given to any functionality still provide outputs that result in 0 errors. The Functionality folder holds all the libraries used in this project. For more detailed descriptions of the libraries, see the Libraries section of this readme file. Finally, the webDevelopmentFiles is the last parent folder. In this folder, we contain files that work with web development. Currently, there are two sub folders. Of the two, interactiveGrid is of larger importance. In this subfolder, we have the code for our interactive grid visualization. In the other subfolder, we have code written in php that revolved around various aspects of the project including trilateration, random waypointing, and other topics. 

---

### Libraries

#### RSSIToDistanceLib
This library was created to separate the functionality of converting an rssi value
to a distance. In total, there are two versions to do this. The first version
"rssiToDistance()" is the older, depreciated version of this conversion. It uses an older
lookup table that was updated lated on. rssiToDistanceV2() is the newest, and better, version
of this conversion. Its accuracy was better by a around 2% on average. Overall, the general
method of converting an rssi value to a distance was unsuccessful due to the low accuracy of both
functions.

* rssiToDistance(rssi)
* rssiToDistanceV2(rssi)

#### PathLossLib
This library is intended to hold all functions that are related to path loss models. Path loss models
are mathematical algorithms that determine the "ideal" rssi value based on certain values such as distance, 
path loss index, transmittion power, etc.  

* freeSpacePathLossLinear(distance)
* freeSpacePathLossdB(distance)
* pathLossExponent(distance)
* FSPL(distance)
* pathLossVanilla(distance, pathLossExponent, transmitterPower)

#### GridLib
In the GridLib library, we have functions that were used to create, visualize, and analyze 
information that was used in creating the grid that lays over Clematis Street. In here, we
can create any size grid on an location on the earth. 

* GridSquare ~ Class
* adjustedLongitude(t, x)
* adjustedLatitude(t, x)
* visualizeGrid(origin, lat_dist, long_dist, meridianDist, parallelDist)
* showGrid(m, filePath)
* createGrid(origin, latDistance, longDistance, adjustedMeridianDistance, adjustedParallelDistance)
* makeCoordsArray(lats, longs)
* getGridCorners(coord_array)
* getEmitterCoords(df)
* getEmitterPositions(emitter_coords, latList, longList, grid_corners)
* getDeviceGridSpot(device_loc, lats, longs, grid_corners)
* makeGrid(grid_corners, latList, longList, emitter_locs, df)
* exportGridAsCsv(grid, pathName)
* sensorLocationsDict(sensorList)
* sensorMaxCoords(sensorList, latList, longList)
* containsSensor(tile, sensorList, latList, longList)
* averageActualRSSI(emitter_locs, df, ref_sensor_list)
* completeGrid(origin, latDistance, longDistance, adjustedMeridianDistance, adjustedParallelDistance, df500)
* localizationTest(grid, df, emitter_locs)
* gridLocalizationTest(grid, df, emitter_locs, rand_row)
* gridLocalization(grid, df, emitter_locs)
* csvTojson(csvFilePath, jsonPath)
* localizecsv(csvFilePath, csvOutputFilePath, localizationData)
* getActiveEmitterLocs(emitter_locs)

#### TrilaterationLib
This library includes functionality that was used to trilaterate points on map. This library uses other
libraries such as GridLib and RSSIToDistanceLib to complete some of its tasks. In here, we focus on functions
that were used to plot points on a map to visualize how successful we were trilaterating devices using rssi values.

* multilaterate(coords, dists)
* trilaterate(sXLoc, sXDist, sYLoc, sYDist, sZLoc, sZDist)
* plotRowOnMap(row, sensorSet, trueEmitterLocationSet, data, m, d=None, createCSV=False, oldVersion=True)
* getCoordinates(sensorNum)
* getEmitterCoords(row)
* isSingleDigit(num)
* jprint()
* createTrilateratedMap(df, headCount, centralPoint, pathName, d=None, createCsv=False, oldVersion=False)

#### mLLib
This library was created to hold all the functions that were used in developing
a machine learning model. The ourpose of this was to see if k-nearest neighbors 
algorithm was helpful in picking the correct rssi value based on a give distance.
The accuracy of this machine learning model yield around 14% each time we ran it.

* lambdaRound(row)
* sensorDistance(sensorId)
* createSubSet(x, y)
* createDataFrame(sensorId, sensorDF)
* scaleDataset(dataframe)
* KNN()

#### DataFiltrationLib
This library was indended to contain all the functions used when we filter
raw data from the MobIntel sensors. There are a lot of rows and columns that have no been
necessary for out needs throughout this project, so we developed functions to quickly
trim them down to what we need. This library also includes functions that revolve around machash
related things.

* read_file(filepath)
* sensor_trim(probe)
* mac_count(pqfile, cutoff)
* groupByMacHash(df)
* newDateCollector(row)
* deviceInSensorAreaDuration(probingTimes, DURATION_LIMIT)
* newDetermineDuration(row, durationLimit)
* determineMacHashDuration(filename)
* getSubsetByRefSensorAndX(blockDataFile, refSensor, x)
* convertFanchen(fanchenFileName)

#### ExploritoryAnalysisLib
This library was of separate use during the project. When we were exploring forecasting
methods, we would use some of the functions here to determine if our data was primed
for such methods. In this library you will find functions that plot data from the MobIntel
sensors as well as separates the data into seprate categorize.

* createLineGraph(df, date, dayByDay=False)
* distanceCounter(dataframe)
* rssiSet()
* dateAggDf(filename)
* hourAggDf(filename)
* plotDateAgg(dateAgg)
* plotInDepthWeek(dateAgg, hourAgg)
* plotDays(dateAgg, hourAgg)

---

### Drivers
The purpose of the drivers is to showcase the functions within the library working
the way we expect them to. Some drivers are shorter than others and do not show each
function working separetly. This is because some drivers have functions that utilize the specific
usecase of other functions within it. If the parent function works as expected, we can assume the child
functions to be in working order. A list of the drivers will be presented here. The names of each driver correspond to which library it uses.

* RSSITOoDistanceLibDriver
* PathLossLibDriver
* GridLibDriver
* TrilaterationLibDriver
* mLLibDriver
* DataFiltrationLibDriver
* ExploritoryAnalysisLibDriver

---

### How to Use Libraries

To use a library in the pythonFiles folder, we must first import the sys module, which is in standard
library in python. Then, we must use the path.append method to add in an extra path for our 
system to search through when we are looking for libraries to use. Typically, this path will be 'pythonFiles', since it is native to the repository, and not the local device. Finally, we must call the library.
The way that we do this is by first importing from Functionality and then call the specific library I want.
I usually give it an alias as well. Below is an example code block of what this would look like:

```
import sys
sys.path.append("pythonFiles")

from Functionality import GridLib as gl
```

One could also use dot notation to grab the same library:
```
import sys
sys.path.append("pythonFiles")

import Functionality.GridLib as gl
```
