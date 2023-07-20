# MobIntel-Project

## Project Description
This is where we will compile all out code that went towards this project. This project was working towards determining the trajectory of people along a street to help cities better plan for pandemics. With this kind of information, city planners could understand how people are moving and make precautions based on this information

## Table of Contents
- How to Find Stuff
This section will provide an overview of how our code is organized and where to expect to find things throughout the
repository.
- Libraries
In this section, we will provide the names of each of the libraries created in this repo and with a short description
of what the library is intended to be used for. Also, for each library, there will be a list of function names.
- Drivers
This section has all the drivers fo each of the libraries. Here, we will explain the intentions of some functions.
- other stuff
This section includes misc. stuff 


### How to Find Stuff

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
