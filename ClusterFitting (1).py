# Importing the necessary libraries
import wbdata
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from scipy.optimize import curve_fit
from scipy.stats import norm

def changeFormat(filename):
    data = pd.read_csv(filename)
    data = data.set_index('Country Name')
    data = data.drop([
                    'Country Code' , 
                    'Indicator Name' , 
                    'Indicator Code'
                    ] , 
                    axis = 1 
            )
    data = data.T
    
    return data


# Countries Needed
countries_1 = 'US'
countries_2 = 'RU'
 
# Indicators Needed
indicators_usa = {
                    'NY.GNP.PCAP.CD' : 'GNI per Capita'
                }

indicators_russia = {
                    'NY.GNP.PCAP.CD' : 'GNI per Capita'
                }   

# Grab indicators above for countires above and load into data frame
df_usa = wbdata.get_dataframe(indicators_usa, country = countries_1 , 
                          convert_date = False)

df_russia = wbdata.get_dataframe(indicators_russia , 
                                 country = countries_2 , 
                                 convert_date = False)

dfu = df_usa
df_ru = df_russia


# Filling the NaN values
dfu.fillna(dfu['GNI per Capita'].mean() , 
           inplace = True)

df_ru.fillna(df_ru['GNI per Capita'].mean() , 
             inplace = True)

# Visualising GNI per Capita for USA & Russia :
df_ru.plot(
            kind = 'bar' ,
            color = 'blue'
        )
plt.title('GNI per Capita for Russia')
plt.show()

dfu.plot(
            kind = 'bar' , 
            color = 'red'
        )
plt.title('GNI per Capita for USA')
plt.show()

df_stacked = pd.concat(
                        [df_ru , dfu] , 
                        axis = 1
                    )
df_stacked.plot(
                    kind = 'bar' , 
                    stacked = True
            )

plt.title('GNI per Capita for USA & Russia (Stacked)')
plt.show()


"""
Normalizing the data using Min-Max Normalization Method:
"""

#initialize the scaler
scaler = MinMaxScaler()

#fit the scaler to the data
scaler.fit(dfu.values.reshape(-1 , 1))

#transform the data
dfu_normalized = scaler.transform(dfu.values.reshape(-1 , 1))

#print the normalized data

"""
Performing K-Means Clustering:
"""

# number of clusters
k = 4

# run kmeans
kmeans = KMeans(n_clusters=k)

# fit the kmeans to the normalized data
kmeans.fit(dfu_normalized)

# add the cluster labels as a new column to the dataframe
dfu['cluster'] = kmeans.labels_

# get the cluster centers
cluster_centers = kmeans.cluster_centers_

cluster_centers = np.array(cluster_centers).reshape(-1 , 1)

# plot the cluster membership
plt.scatter(dfu.index , dfu['GNI per Capita'] , 
            c = dfu['cluster'] , cmap = 'rainbow')

# plot the cluster centers
dfu.reset_index(inplace=True)
print(dfu)
plt.scatter(dfu.index , dfu['GNI per Capita'] , 
            c = dfu['cluster'] , 
            cmap = 'rainbow')

plt.scatter(range(4) , cluster_centers[: , 0] ,
            c = 'black' , 
            s = 200 , 
            alpha = 0.5)

plt.xlabel('Year')
plt.ylabel('GNI per Capita')
plt.tick_params(axis = 'x' , labelsize = 2)
plt.show()


"""
Fitting the clusters to an exponential growth model:
"""

# Define the exponential growth model
def exp_growth(x , a , b):
    return a * np.exp(b * x)

# Get the x and y data
x_data = dfu.index
y_data = dfu['GNI per Capita']

# Fit the model using curve_fit
params, cov = curve_fit(exp_growth , x_data , y_data)

# Get the parameter estimates
a = params[0]
b = params[1]

# Plot the data and the fitted model
plt.scatter(x_data , y_data)
plt.plot(x_data , 
         exp_growth(x_data , a , b) , 'r-')

plt.xlabel('Year')
plt.ylabel('GNI per Capita')
plt.show()

# Get the standard error of the estimates
a_err = np.sqrt(cov[0][0])
b_err = np.sqrt(cov[1][1])

# Get the 95% confidence intervals
a_conf = norm.interval(0.95 , 
                       loc = a , 
                       scale = a_err)

b_conf = norm.interval(0.95 , 
                       loc = b , 
                       scale = b_err)

# Print the confidence intervals
print(f'a: {a:.2f} +/- {a_err:.2f} ({a_conf[0]:.2f}, {a_conf[1]:.2f})')
print(f'b: {b:.2f} +/- {b_err:.2f} ({b_conf[0]:.2f}, {b_conf[1]:.2f})')