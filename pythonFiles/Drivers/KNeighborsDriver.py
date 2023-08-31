from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neighbors import KNeighborsClassifier
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
from math import sqrt
dfjose = pd.read_csv("JoseData.csv", engine='python') #data we are currently using
dfjose.drop(["class_label"], axis=1)
def KNNRegress (df): #regression model function

  #print("data before imputation:")
  #display(df)
  #df.describe()
  #df.isnull().values.any()
  for column in df.columns: #this loop replaces null values in DF with random values between the min and max of that column
    if column != 'tx_coord':
        df[column] = df.groupby('tx_coord')[column].transform(lambda x: x.fillna(np.random.uniform(x.min(), x.max())))

  #drop tx_coord column that holds coordinates
  coord = pd.DataFrame(columns = ['coord', 'X', 'Y'])
  coord['coord'] = df['tx_coord']
  #coord['coord'] = coord.coord.astype('string') #first attempt was converting the coordinates to string type
  #display(coord)
  #print('Unique values are:')
  #print(coord.unique())
  #coord = coord.str[1:-1] #this slices the parenthesis from the coordinate string
  #coord = coord.str.replace(', ', '.')
  new = coord['coord'].str.split(",", expand = True) #these next lines divide the coordinate DF into two columns, and remove the "()" and ","
  coord["X"] = new[0]
  coord["Y"] = new[1]
  coord["X"] = coord.X.str[1:]
  coord["Y"] = coord.Y.str[:-1]
  coord['X'] = coord.X.astype('int')
  coord['Y'] = coord.Y.astype('int')
  display(coord)
  #print(coord.dtypes)

# X values Regression !!!!!!!!!!!! Only testing with respect to X values. Essentially ignoring Y values for this portion
  imputer_mean = SimpleImputer(missing_values=np.nan, strategy='mean') #previoulsy how the null values were filled, replaced with for loop above
  #imputer_mean.get_feature_names_out([['receiver_0', 'receiver_1', 'receiver_2', 'receiver_3', 'receiver_4', 'receiver_5', 'receiver_6', 'receiver_7', 'receiver_8']])
  df2 = imputer_mean.fit_transform(df[['receiver_0', 'receiver_1', 'receiver_2', 'receiver_3', 'receiver_4', 'receiver_5', 'receiver_6', 'receiver_7', 'receiver_8']])
  df2 = pd.DataFrame(df2, columns = ['57','20','05','34','22','06','31','36','35'])
  #print(df2.unique())
  df2["X"] = coord.X #create columns in new DF for the X and Y coordinate respectively
  df2["Y"] = coord.Y
  display(df2)
  #print(df2.dtypes)
  #df2.coord.astype(str)
  #print(df2.dtypes)
  #df2.describe()
  #df2.isnull().values.any()
  Xx = df2.drop(['X','Y'], axis=1) #because this is only regression for X coordinates, all variables are named with an "x"
  yx = df2["X"] #Y-axis of regression
  Xx_train, Xx_test, yx_train, yx_test = train_test_split(Xx, yx, test_size=0.2, random_state=123) #train test split variables
  Xx_train.shape
  Xx_test.shape
  print('X_train is:', Xx_train)
  print('X_test is:', Xx_test)

#standardisation using standard scaler
  scaler = StandardScaler()
  xtrain_scaled = scaler.fit_transform(Xx_train.values)
  xtest_scaled = scaler.transform(Xx_test)
  xmodel = KNeighborsRegressor(n_neighbors = 15) #Creating regression model. Experiment with K values
  xmodel.fit(xtrain_scaled, yx_train.values) #fit model

#Show model
  xtrain_predict = xmodel.predict(xtrain_scaled)
  xmse = mean_squared_error(yx_train, xtrain_predict) #mean squared error and mean absolute error are methods to show accuracy of model. Lower is better
  xmae = mean_absolute_error(yx_train, xtrain_predict)
  #mape = (mean_absolute_error(y_train, model.predict(train_scaled)) * (1 / len(model.predict(train_scaled))))
  #prediction = model.predict(X_test)
  xscore = xmodel.score(Xx, yx)
  print("X prediction is:", xtrain_predict)
  print("X score is:", xscore) #score of 1 is perfect. Negative score means model is very bad at predicting
  #graph = model.kneighbors_graph(X)
  #graph.toarray()
  print("xmse = ",xmse," & xmae = ",xmae," & xrmse = ", sqrt(xmse))

#Y values Regression !!!!!!!!!! Only testing with respect to Y values. Essentially ignoring X values for this portion
  Xy = df2.drop(['X','Y'], axis=1) #because this is only regression for Y coordinates, all variables are named with an "y"
  yy = df2["Y"] #Y-axis of regression
  Xy_train, Xy_test, yy_train, yy_test = train_test_split(Xy, yy, test_size=0.2, random_state=123) #train test split variables
  Xy_train.shape
  Xy_test.shape
  print('Y_train is:', Xy_train)
  print('Y_test is:', Xy_test)

#standardisation using standard scaler
  ytrain_scaled = scaler.fit_transform(Xy_train.values)
  ytest_scaled = scaler.transform(Xy_test)
  ymodel = KNeighborsRegressor(n_neighbors = 15) #Creating regression model. Experiment with K values
  ymodel.fit(ytrain_scaled, yy_train.values) #fit model

#Show model
  ytrain_predict = ymodel.predict(ytrain_scaled)
  ymse = mean_squared_error(yy_train, ytrain_predict) #mean squared error and mean absolute error are methods to show accuracy of model. Lower is better
  ymae = mean_absolute_error(yy_train, ytrain_predict)
  #mape = (mean_absolute_error(y_train, model.predict(train_scaled)) * (1 / len(model.predict(train_scaled))))
  #prediction = model.predict(X_test)
  yscore = xmodel.score(Xy, yy)
  print("Y prediction is:", ytrain_predict)
  print("Y score is:", yscore) #score of 1 is perfect. Negative score means model is very bad at predicting
  #graph = model.kneighbors_graph(X)
  #graph.toarray()
  print("ymse = ",ymse," & ymae = ",ymae," & yrmse = ", sqrt(ymse))
  return (xscore, yscore)

KNNRegress(dfjose)

def KNNClass (df): #classification model function

  for column in df.columns: #this loop replaces null values in DF with random values between the min and max of that column
    if column != 'tx_coord':
        df[column] = df.groupby('tx_coord')[column].transform(lambda x: x.fillna(np.random.uniform(x.min(), x.max())))

  #drop tx_coord column that holds coordinates
  coord = pd.DataFrame(columns = ['coord'])
  coord['coord'] = df['tx_coord']
  coord['coord'] = coord.coord.astype('string') #converting the coordinates to string type
  display(coord)
  print(coord.dtypes)

# Classification !!!!!!!!!!!!
  imputer_mean = SimpleImputer(missing_values=np.nan, strategy='mean') #previoulsy how the null values were filled, replaced with for loop above
  #imputer_mean.get_feature_names_out([['receiver_0', 'receiver_1', 'receiver_2', 'receiver_3', 'receiver_4', 'receiver_5', 'receiver_6', 'receiver_7', 'receiver_8']])
  df2 = imputer_mean.fit_transform(df[['receiver_0', 'receiver_1', 'receiver_2', 'receiver_3', 'receiver_4', 'receiver_5', 'receiver_6', 'receiver_7', 'receiver_8']]) #don't need
  df2 = pd.DataFrame(df2, columns = ['57','20','05','34','22','06','31','36','35']) #create DF
  #print(df2.unique())
  df2["coord"] = coord #create column in new DF for the X and Y coordinates
  display(df2)
  print(df2.dtypes)
  X = df2.drop(['coord'], axis=1) # x-axis of classification is the RSSI's
  y = df2["coord"] #Y-axis of classification is the coords
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123) #train test split variables
  X_train.shape
  X_test.shape
  print('X_train is:', X_train)
  print('X_test is:', X_test)

#standardisation using standard scaler
  scaler = StandardScaler()
  train_scaled = scaler.fit_transform(X_train.values)
  test_scaled = scaler.transform(X_test)
  model = KNeighborsClassifier(n_neighbors = 15) #Creating regression model. Experiment with K values
  model.fit(train_scaled, y_train.values) #fit model

#Show model
  train_predict = model.predict(train_scaled)
  test_predict = model.predict(test_scaled) 
  #mse = mean_squared_error(y_train, train_predict) #can't use these methods of rating the model, since they only work on numeric data sets and we are using strings
  #mae = mean_absolute_error(y_train, train_predict)
  #mape = (mean_absolute_error(y_train, model.predict(train_scaled)) * (1 / len(model.predict(train_scaled))))
  #prediction = model.predict(X_test)
  score = model.score(X, y)
  accuracy = accuracy_score(y_test, test_predict) #accuracy function gives us an accuracy assessment based on the ability to predict correct string
  print("Classification prediction is:", train_predict)
  print("Score is:", score)
  print("Accuracy is:", accuracy)
  #graph = model.kneighbors_graph(X)
  #graph.toarray()
  #print("mse = ",mse," & mae = ",mae," & rmse = ", sqrt(mse))
  return (score)


KNNClass(dfjose)