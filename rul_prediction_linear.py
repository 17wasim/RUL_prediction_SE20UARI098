# -*- coding: utf-8 -*-
"""RUL_prediction_Linear.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10974HnG4-A6Kx0Hw4LRguDezUt95A2pb
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import seaborn as sns
import math
import matplotlib.pyplot as plt
from matplotlib import cm

from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import QuantileTransformer , PowerTransformer
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression

from keras.layers import Dense , LSTM
from keras.models import Sequential
from sklearn.metrics import mean_squared_error

# %matplotlib inline
cmap = cm.get_cmap('Spectral') # Colour map (there are many others)

from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import explained_variance_score
from sklearn.metrics import r2_score

import pickle

train_file = "/content/drive/MyDrive/train_FD001.txt"
test_file = "/content/drive/MyDrive/test_FD001.txt"
RUL_file = "/content/drive/MyDrive/RUL_FD001.txt"

df = pd.read_csv(train_file,sep=" ",header=None)
df.head()

df.drop(columns=[26,27],inplace=True)
columns = ["Section-{}".format(i)  for i in range(26)]
df.columns = columns
df.head()

df.describe()

# Names
MachineID_name = ["Section-0"]
RUL_name = ["Section-1"]
OS_name = ["Section-{}".format(i) for i in range(2,5)]
Sensor_name = ["Section-{}".format(i) for i in range(5,26)]

# Data in pandas DataFrame
MachineID_data = df[MachineID_name]
RUL_data = df[RUL_name]
OS_data = df[OS_name]
Sensor_data = df[Sensor_name]

# Data in pandas Series
MachineID_series = df["Section-0"]
RUL_series = df["Section-1"]

grp = RUL_data.groupby(MachineID_series)
max_cycles = np.array([max(grp.get_group(i)["Section-1"]) for i in MachineID_series.unique()])

df.drop(columns=["Section-0",
                "Section-4", # Operatinal Setting
                "Section-5", # Sensor data
                "Section-9", # Sensor data
                "Section-10", # Sensor data
                "Section-14",# Sensor data
                "Section-20",# Sensor data
                "Section-22",# Sensor data
                "Section-23"] , inplace=True)

print(type(df))
gen = MinMaxScaler(feature_range=(0, 1))
df = gen.fit_transform(df)
df = pd.DataFrame(df)
pt = PowerTransformer()
df = pt.fit_transform(df)

df=np.nan_to_num(df)

def RUL_df():
    rul_lst = [j  for i in MachineID_series.unique() for j in np.array(grp.get_group(i)[::-1]["Section-1"])]
    rul_col = pd.DataFrame({"rul":rul_lst})
    return rul_col

RUL_df().head()

X = np.array(df)
y = np.array(RUL_df()).reshape(-1,1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.20)

lin_model = LinearRegression()
lin_model.fit(X_train, y_train)

pred_lin = lin_model.predict(X)

print("\nmean_squared_error >> ", mean_squared_error(y, pred_lin))
print("mean_absolute_error >>",mean_absolute_error(y, pred_lin))

print("Acc of Linear Regression >> ",lin_model.score(X_test, y_test))

pickle.dump(lin_model, open('linear_regression.sav', 'wb'))

lin_model = pickle.load(open('linear_regression.sav', 'rb'))

df_test = pd.read_csv(test_file, sep=" ",header=None)
df_test.drop(columns=[26,27],inplace=True)
df_test.columns = columns
df_test.head()

df_rul = pd.read_csv(RUL_file, names=['rul'])
df_rul.head()

RUL_name = ["Section-1"]
RUL_data = df_test[RUL_name]
MachineID_series = df_test["Section-0"]
grp = RUL_data.groupby(MachineID_series)
max_cycles = np.array([max(grp.get_group(i)["Section-1"]) for i in MachineID_series.unique()])
max_cycles

df_test.drop(df_test[["Section-0",
                "Section-4", # Operatinal Setting
                "Section-5", # Sensor data
                "Section-9", # Sensor data
                "Section-10", # Sensor data
                "Section-14",# Sensor data
                "Section-20",# Sensor data
                "Section-22",# Sensor data
                "Section-23"]], axis=1 , inplace=True)

gen = MinMaxScaler(feature_range=(0, 1))
df_test = gen.fit_transform(df_test)
df_test = pd.DataFrame(df_test)
pt = PowerTransformer()
df_test = pt.fit_transform(df_test)
df_test=np.nan_to_num(df_test)

lin_pred = lin_model.predict(df_test)
lin_pred = np.array(lin_pred)
lin_pred = lin_pred.flatten()
lin_pred = lin_pred.reshape(lin_pred.shape[0],1)
lin_pred.shape

final_lin_pred = []
count = 0
for i in range(100):
    temp = 0
    j = max_cycles[i]
    while j>0:
        temp = temp + lin_pred[count]
        j=j-1
        count=count+1
    final_lin_pred.append(temp/max_cycles[i])

final_lin_pred=np.array(final_lin_pred)
final_lin_pred = final_lin_pred.flatten()

fig = plt.figure(figsize=(18,10))
plt.plot(final_lin_pred,c='red',label='prediction')
plt.plot(df_rul,c='blue',label='y_test')

fig.suptitle('RUL Prediction using Linear Regressin Model', fontsize=35)
plt.xlabel("Engine Number", fontsize=35)
plt.ylabel("Remaining Useful Life", fontsize=35)

plt.legend(loc='upper left')
plt.grid()
plt.show()

def scoring_function(actual,predicted):
    d = []
    for i in range(len(predicted)):
        d.append((predicted[i] - actual[i]))
    scores = []
    for i in range(len(d)):
        if d[i] >= 0:
            scores.append(math.exp(d[i]/10) - 1)
        else :
            scores.append(math.exp((-1*d[i])/13) - 1)
    return sum(scores)

print("mean_squared_error >> ", mean_squared_error(df_rul,final_lin_pred))
print("root mean_absolute_error >>",math.sqrt(mean_squared_error(df_rul,final_lin_pred)))
print("mean_absolute_error >>",mean_absolute_error(df_rul,final_lin_pred))
print("scoring function >>",scoring_function(np.array(df_rul),final_lin_pred))

