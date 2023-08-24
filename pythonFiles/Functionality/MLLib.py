import pandas as pd, numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsRegressor

rssiDataSet = pd.read_csv("datasets/sampled_source_data.csv")

#Round all the distances to the closest whole number
def lambdaRound(row):
    """
    row: a row in the 
    Returns:
    Description: round all the distances to the closest whole number
    """
    return round(row["Distance"])


def sensorDistance(sensorId):
    """
    sensorId: string value that represents sensor number
    Returns: a dataframe  holding sensor distance data. Each row tells us
    how far away the rssi value was collected from
    Description: Using the data from the parking lot experiement,
    creates a sub dataframe that contains the sensor rssi value (e.i., s1) 
    and the distance from that sensor (s1_d)
    returned dataframe is in the form: rssi | distance
    """
    sensorDict = {sensorId: rssiDataSet[sensorId]}
    distanceString = sensorId+"_d"
    sensorDict[distanceString] = rssiDataSet[distanceString]
    return pd.DataFrame(data=sensorDict)


def createSubSet(x, y):
    """
    x: x coordinate column in parking lot experiment
    y: y coordinate column in parking lot experiement
    Returns: a subset of a data frame that resulted from a query on x and y
    Description: creates a subset based on the x & y coordinates on the rssiDataSet 
    data frame This function is created incase we need to separate by coordinates
    for whatever reason I had a good reason before I made this function, but now I forgot
    """
    return rssiDataSet.query("xcoord == @x & ycoord == @y")



def createDataFrame(sensorId, sensorDF):
    """
    sensorId: id number of a sensor
    sensorDF: result from sensorDistance(sensorid)
    Returns: a dataframe of data from this certain sensorid
    Description: Create a dataframe with the column names
    of SensorId | RSSI Value | Distance
    """
    sList = []
    for i in range(len(sensorDF)):
        sList.append(sensorId)
    data = {}
    data["sensor_Id"] = sList
    data["RSSI_Value"] = sensorDF[sensorId]
    data["Distance"] = sensorDF[sensorId+"_d"]
    return pd.DataFrame(data=data)


def scaleDataset(dataframe):
    """
    dataframe: a data frame 
    Returns: data in its entirety and data split up by the x and y value. Both are
    subsets of data but adding them together equal data
    Description: scale the dataset to help with machine learning
    """
    x = dataframe[dataframe.columns[1:-1]].values
    y = dataframe[dataframe.columns[-1]].values
    data = np.hstack((x, np.reshape(y, (-1,1))))
    return data, x, y

def KNN():
    """
    Returns: a plot that represents  the KNN algorithm success
    Description: This function uses the machine learning model called 
    K-nearest neighbors on the parking lot experiment performed by 
    fanched and stepan
    """

    s1 = sensorDistance("s1")
    s2 = sensorDistance("s2")
    s3 = sensorDistance("s3")
    s4 = sensorDistance("s4")
    sensorList =[s1, s2, s3, s4]


    sList = ['s1', 's2', 's3', 's4']
    dfList = [] #list of dataframes
    for i in range(len(sList)):
        df = createDataFrame(sList[i], sensorList[i])
        dfList.append(df)


    df = pd.concat(dfList, ignore_index=True) #adding all sensors data into one dataframe

    #Round distances to nearest whole number
    df["Distance"] = df.apply(lambda row: lambdaRound(row), axis=1)
    print("dataframe after concat & rounding distances\n", df)

    #prepare the data for machine learning
    training, valid, test = np.split(df.sample(frac=1), [int(0.6*len(df)), int(0.8*len(df))])

    train, xtrain, ytrain = scaleDataset(training)
    valid, xvalid, yvalid = scaleDataset(valid)
    test, xtest, ytest = scaleDataset(test)


    knn_model = KNeighborsRegressor(n_neighbors=3) #odd numbers only, typically 1, 3, or 5
    knn_model.fit(xtrain, ytrain)

    yprod = np.round(knn_model.predict(xtest), 0)

    #can print ytest and yprod to show what the test values were and what the prediction was
    #print("ytest\n", ytest)
    #print("yprod\n", yprod)

    offBy = {}
    length = len(ytest)
    correct = 0
    for i in range(length):
        if ytest[i] == yprod[i]:
            correct += 1
        else:
            diff = abs(ytest[i] - yprod[i])
            if diff in offBy:
                offBy[diff] += 1
            else:
                offBy[diff] = 1

    print("The following dictionary finds the difference between the prediction and actual value\nand counts the amount of times that difference occured")
    print(offBy)

    print("accuracy in decimal form: ", correct/length)
    percent = '{:.3%}'.format(correct/length)
    print("KNN recieved an accuracy of ", correct, "/", length, " or a percentage of ", percent)

    #graph the dataframe
    plt.scatter(df["RSSI_Value"], df["Distance"], color="orange", alpha=0.2)
    plt.title("Sensor distances for RSSI values")
    plt.xlabel("rssi value")
    plt.ylabel("distance (m)")

    plt.show()
