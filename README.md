# MobIntel-Project


## Table of Contents
1. Project Description
2. Project History
3. How to Find Stuff
4. Libraries
5. Drivers
6. How to Use Libraries
7. Commenting Convention

---

### Project Description
The research question we will try to answer during this project is: how should crowds be managed in real-time during a pandemic to mitigate risk and ease the public fear of taking mass transit? This question will be addressed by bridging engineering and scientific models at the intersection of indoor pedestrian mobility, epidemiology, and travel behavior. Rather than investing in transit infrastructure and services in a short timeframe (which is especially challenging when transit agencies are struggling with staffing shortage and financial crisis), reshaping public transport mobility could be a more viable way.

This GitHub Repository is where we will compile all our code that goes towards this project. So far, this project has been working towards determining the trajectory of people along a street to help cities better plan for pandemics. With this kind of information, city planners could understand how people are moving and take precautions based on this information. As an overview, in our research, we encountered valuable insights regarding trilateration of RSSI values as a method for determining device positions. Recognizing its limitations, we shifted our focus to exploring a new avenue — the grid system. As of August 28th, 2023, we have some promising results from our grid system and are in the process of testing it with real data from the MobIntel sensors. More specific details about the history of this project can be found in the Project History Section.

---

### Project History
In this section, we will discuss the history of this project. This includes all attempted methods for solving our problem stated in the Project Description, as well as the details that went into these attempted methods so that future workers on this project can start where we left off. We initially focused on the problem of figuring out where an emitting device, such as a mobile phone, was physically located. This was necessary since we are trying to get a trajectory of a single mobile device. The end goal was to get multiple points on a map and connect them in a certain order to show the trajectory that the mobile device moved. 


#### Trilateration
Trilateration constitutes a geometric methodology utilized to ascertain the coordinates of an unknown point of interest based on the measurement of distances from known reference points. When more than three distances are incorporated within this method, it extends to multilateration, allowing for increased accuracy in positioning determination.

The deployment of trilateration within our study held promise due to the availability of multiple closely spaced sensors. These sensors, situated in close proximity, gather pertinent data concerning nearby devices. Notably, the Received Signal Strength Indicator (RSSI) value, garnered from the device's probe request, emerges as a critical datum. This RSSI value quantifies the signal's intensity upon its reception by MobIntel sensors. Generally, the RSSI value deteriorates with increasing distance between the sensor and the signal's origin point, establishing a perceptible correlation. Our objective encompassed an exploration of this correlation's robustness for trilateration, contingent on accurate distances derived from known positions. In undertaking this pursuit, we diligently reviewed pertinent literature to gain insight into this domain.

However, our findings revealed the RSSI-to-distance correlation to be frail and inherently unreliable. Diverse factors, inclusive of weather conditions (humidity, precipitation), environmental context (urban, suburban, rural), device and sensor age, collectively influence the RSSI value. Despite this realization, driven by the magnitude of our available data, we persevered in our endeavor to explore potential solutions.

Our trilateration implementation comprised two distinct methodologies. Initially, a "Conversion Table" was devised to establish a direct RSSI-to-distance correspondence. This table exists in two variants, available at 'datasets/rssiToDistanceCorrelation_V2.csv' and 'datasets/rssiToDistanceCorrelation.csv', with the former being preferred. Detailed insight into these conversion tables' development can be found in the PowerPoint slides located at 'media/powerpoints/WeeklyMeeting(05-31-23).pptx'. Regrettably, this approach's performance fell short of expectations.

![Image](media/images/trilaterationResults.png)

The accompanying image depicts the evaluation of multiple RSSI-to-distance conversion methods utilizing a dataset conducive to trilateration, containing 1000 data entries. For instance, when applying the New Lookup Table* and assessing the trilateration accuracy for points within a 5-meter radius of the true emitting device location, an accuracy of 8.4% was achieved. This signifies that among the 1000 points, 84 were positioned within 5 meters of the actual emitting device location. Despite these evaluations, the achieved accuracy across all methodologies proved inadequate for our project's exigencies. Consequently, we ventured into alternative methodologies for RSSI-to-distance conversion, given their salience in trilateration endeavors.

The alternative approach hinged on the integration of machine learning models, with a particular emphasis on the K-Nearest Neighbors (KNN) methodology. Unfortunately, the accuracy of this method, approximately 14%, was notably deficient. Intriguingly, deliberations emerged regarding the feasibility of correlating a range of distances to a single RSSI value, potentially augmenting accuracy. However, such a strategy was deemed unlikely to cater to our trilateration requirements. Given the lackluster performance, point plotting stemming from the machine learning method was eschewed due to inadequate RSSI-to-distance accuracy.

Our trilateration pursuit encountered multiple impediments. Preliminary considerations acknowledged the limitations inherent in RSSI due to its intrinsic variability. A composite of diverse influences, encompassing weather dynamics, sensor location, environmental context, and device-sensor conditions, collectively contributed to its unreliability. Numerous factors lay beyond our control, while some remained immeasurable. In summation, trilateration emerges as a suboptimal technique for pinpointing mobile device locations, necessitating alternative approaches for accurate positioning.

#### Forecasting Models
Subsequent to the resolution to pivot away from trilateration, we embarked upon an exploration of alternative conceptual avenues. Among these, the realm of forecasting models emerged as a focal point of investigation. To briefly explain, forecasting models encompass a suite of techniques tailored to collate and manipulate data, engendering reliable and precise projections. In our context, this translated to harnessing the timestamps accompanying each probe request as captured by the MobIntel sensors. Our data was primed for such methods however, despite the inherent alignment between our data and forecasting methods, a deliberation ensued, casting doubt upon the suitability of this approach for our overarching objectives.

Specifically, our current objectives centered on the accurate localization of emitting devices. While forecasting models excelled in forecasting the temporal clustering of individuals and their corresponding locations, a crucial shortcoming emerged—the inability to project the trajectories leading to these locations. As such, the forecasting methods, though proficient in prognostication, proved insufficient for our aim of tracing the trajectory of an individual device. Consequently, we adjudged the application of forecasting models infeasible within the scope of our endeavor.

#### Development of the Grid System
The grid system proceeds our trilateration efforts. In trilateration, we saw that we had some points that got pinned far away from their expected location. To help minimize this error, we encapsulated the street where our sensors are in a grid structure. A visual representation of this method can be seen in the image below.
![Image](media/images/1mGrid.png)
By encapsulating the street, it was projected that we would always have a localization result somewhere within the grid rather than 3 streets down, like what happened in trilateration. So, in theory, the smaller the grid, the better the results should be, however, this ideology does come with its own complications. Essentially, the grid system is the groundwork for our localization method. That is, using the path-loss model to determine the distance a device was using just an RSSI value. 

In this grid system, we can determine the length and width of the grid as well as the size of the tiles within the grid. In the picture above, we have a 175x25 grid with tiles that are 1x1. All metrics are in meters. In our beginning phases, we would use data that had the known locations of emitting devices. So, in our grid, we would know which tile the emitting device was located in by using some cross-reference methods. Similarly, we could also tell which tiles the MobIntel sensors were in. With this ground truth data, we could utilize path-loss models for localization purposes and determine how far off we were from the actual location of an emitting device. 

With this grid system, we could also calculate an "ideal" RSSI for each tile per sensor. This means that for each tile, we would use a path-loss mathematical model to determine the expected RSSI value for a tile given a sensor x meters away. We would do this for each distance between the tile and sensors since there are multiple sensors within a grid. For example, if we have 5 sensors in a grid, a grid tile would have 5 ideal calculated RSSI values relating to each of the respective sensors. These calculated RSSI values would be the basis of how we calculate the "score", which would be a mathematical function that calculates a value that is essentially the difference between the ideal RSSI value and an actual RSSI value captured at that tile location. More specifically, the calculated RSSI for a sensor is subtracted from the actual RSSI, and the result is multiplied by the logarithm of the sensor's distance from that tile. Additionally, if a sensor was less than 10 meters away from the tile, it was ignored. This resulted in a "score" for every sensor for every tile. We then take the average of the scores for every sensor in a tile, and the tile with the lowest average score is considered the most likely location for the device. This score could only be calculated for tiles that we know have an emitter in them because those are the only places we had actual RSSI values captured. 

We felt that this method would work better for us because all the signals that the sensors are receiving should be just within the street (now within the grid). Capitalizing on this, we could perform our localization method on the data we have that pertains to this street block and get more accurate localization results. Our plan is to expand this grid structure in one of two ways. We would either have a grid for each block of the street, resulting in less square footage overall, and therefore it would be less computationally challenging for our machines, or put a giant grid over the whole street of Clematis Street. This would result in more square footage.

#### Testing the Grid System with Ground Truth Data
The grid system underwent a vigorous testing phase. As explained in the section above, we have a dataset that contains a lot of data from known emitter locations. This gives us ground truth data that we can test our localization methods with. As a result of our testing, it was noted that the majority of our localization attempts were within 10 meters of the actual location of the known emitter positions. This was a great improvement from trilateration. 

#### Testing the Grid System with MobIntel Data
After testing the accuracy of our data with known emitter locations, we started testing without knowing the position of the emitting device. The idea was to listen to the majority of localized points. For example, in our data, we have around 950 probe requests for a single position. Each request is to be localized to a tile and wherever the majority of the localizations went, that would be the tile we pick as the "best localization". This method proved to be rather successful. The majority of the localizations for any given position were within 10 meters of the actual location of the emitting device. So after this testing phase, we can be confident that without knowing where a device was emitting, we could collect all the probe requests from it within the same moment in time, obtain the best localization for it, and be confident it will be within 10 meters of its actual position.

It would also be important to note that we began working on the concept of the "mini-grid" which has so far shown an even larger increase in accuracy. The idea here is to create a grid that encapsulates where the majority of localization was and perform the same localization method here. 

Currently (08/28/2023), we are looking to gather more data to test out predicting a trajectory within a grid.

---

### Dataframes in Use
Explain the dataframes we have been using so that there is a general understanding of the data we are making all our assumptions and planning on.

There is the block data we make from fanchens data

there is fanchens WPB data

There is the raw data from mobintel

There is the data from the grids that is flattened into a csv file

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
* multipleGrids(listOfGrids, parentOrigin)
* createGrid(origin, latDistance, longDistance, adjustedMeridianDistance, adjustedParallelDistance)
* makeCoordsArray(latList, longList)
* getGridCorners(coord_array)
* getEmitterCoords(df)
* getEmitterPositions(emitter_coords, latList, longList, grid_corners)
* getDeviceGridSpot(device_loc, lats, longs, grid_corners)
* makeGrid(grid_corners, latList, longList, emitter_locs, df)
* exportGridAsCsv(grid, pathName, withIndex)
* sensorLocationsDict(sensorList)
* sensorMaxCoords(sensorList, latList, longList)
* containsSensor(tile, sensorList, latList, longList)
* averageActualRSSI(emitter_locs, df, ref_sensor_list)
* completeGrid(origin, latDistance, longDistance, adjustedMeridianDistance, adjustedParallelDistance, df500)
* localizationTest(grid, df, emitter_locs)
* gridLocalizationTest(grid, df, emitter_locs, rand_row)
* gridLocalization(grid, df, emitter_locs)
* generateLocalizationGuesses(row, grid, numberOfGuesses, data)
* csvTojson(csvFilePath, jsonPath, removeIndex=False)
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

#### MLLib
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

### Commenting Convention
All of our functions in each library will have a comment section at the beginning. This comment is meant to help developers understand what the parameter are for the function, what to expect in return, and lightly describe what is going on in the function, or explain the purpose of the function. To standardize these comments, we try our best to follow the following convention:


"""

paramemter(1-n): explain what the parameter is and the object type
Returns: explain what we should expect after running this function
Description: lightl explain what the function does and why we have it

"""

We have as many parameter comments as there are in the signature of the function. For example, we write comments like this:

```
def adjustedLongitude(t, x):
  """
  t: the tuple of (lat,long) of reference location.
  x: is the distance, in meters, from the reference point.
  Returns: a new (lat,long) that is adjusted by x meters
  Description: If x is positive, this distance is eastward.
  If x is negative, this distance is westward. We return new 
  coordinates based on the current location + the value of x,
  which is a distance in meters.
  """
  .
  .
  .
```
