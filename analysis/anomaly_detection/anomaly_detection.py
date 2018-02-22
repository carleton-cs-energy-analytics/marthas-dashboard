from marthas_dashboard.api import *
from sklearn import metrics
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
from mpl_toolkits.mplot3d import Axes3D # Have to keep so that can use '3d' projection
from math import ceil
import numpy as np
from datetime import timedelta,date

api = API()


def grabAllPointsInBuildingByType(building_id, start, stop, desc_type):
    api = API()
    points = api.building_points(building_id)
    
    temp_point_id = []
    for i in range(len(points)):
        if desc_type in points.description[i] and points.id[i] not in temp_point_id:
            temp_point_id.append(points.id[i])
    
    df_list = []
    for ptid in temp_point_id:
        littledf = api.point_values(ptid, start, stop)
        df_list.append(littledf)
    
    result = pd.concat(df_list)

    # print(result.head())

    return result


def grabAndPivotAllDaysInRangeForPoint(point_id, start_date, end_date):
    api = API()
    df_list = []

    for n in range(int((end_date - start_date).days)):
        from_date = start_date + timedelta(n)
        from_string = str(from_date)
        to_date = from_date + timedelta(1)
        to_string = str(to_date)
        littledf = api.point_values(point_id, from_string + " 00:00", to_string + " 00:00")

        try:
            df_pivot = (littledf
                    .groupby(['pointname', 'pointtimestamp'])['pointvalue']
                    .sum().unstack().reset_index().fillna(0)
                    .set_index('pointname'))
            new_columns = []
            for colname in df_pivot.columns:
                new_columns.append(str(colname).split(" ")[1])
            df_pivot.columns = new_columns
            new_index = [df_pivot.index[0] + str(from_date)]
            df_pivot.index = new_index

            df_list.append(df_pivot)
        except KeyError:
            print("No data for point id " + str(point_id) + " on date " + str(from_date))
    result = pd.concat(df_list)
    return result


def pivot_df(df):
    df_pivot = (df
                .groupby(['pointname', 'pointtimestamp'])['pointvalue']
                .sum().unstack().reset_index().fillna(0)
                .set_index('pointname'))

    return df_pivot


def plot_cluster_distance_3d(dist_to_clusters, labels, anomalies):
    ax = plt.axes(projection='3d')
    ax.scatter3D(dist_to_clusters[:, 0], dist_to_clusters[:, 1], dist_to_clusters[:, 2], c = labels)
    ax.scatter3D(dist_to_clusters[:, 0][anomalies], dist_to_clusters[:, 1][anomalies],dist_to_clusters[:, 2][anomalies], edgecolors='r', facecolors='none')

    # TODO: What color is each??
    ax.set_xlabel('Distance to Cluster 0')
    ax.set_ylabel('Distance to Cluster 1')
    ax.set_zlabel('Distance to Cluster 2')

    plt.savefig("distance_3d.png")


def plot_cluster_distance_2d(dist_to_clusters, labels, anomalies):
    f, axarr = plt.subplots(2, 2)

    axarr[0, 0].set_title('Distance between 0 and 1')
    axarr[0, 0].set_xlabel('Distance to Cluster 0')
    axarr[0, 0].set_ylabel('Distance to Cluster 1')
    axarr[0, 0].scatter(dist_to_clusters[:, 0], dist_to_clusters[:, 1], c=labels)
    axarr[0, 0].scatter(dist_to_clusters[:, 0][anomalies], dist_to_clusters[:, 1][anomalies], edgecolors='r', facecolors='none')

    axarr[0, 1].set_title('Distance between 0 and 2')
    axarr[0, 1].set_xlabel('Distance to Cluster 0')
    axarr[0, 1].set_ylabel('Distance to Cluster 2')
    axarr[0, 1].scatter(dist_to_clusters[:, 0], dist_to_clusters[:, 2], c=labels)
    axarr[0, 1].scatter(dist_to_clusters[:, 0][anomalies], dist_to_clusters[:, 2][anomalies], edgecolors='r', facecolors='none')


    axarr[1, 0].set_title('Distance between 1 and 2')
    axarr[1, 0].set_xlabel('Distance to Cluster 1')
    axarr[1, 0].set_ylabel('Distance to Cluster 2')
    axarr[1, 0].scatter(dist_to_clusters[:, 1], dist_to_clusters[:, 2], c=labels)
    axarr[1, 0].scatter(dist_to_clusters[:, 1][anomalies], dist_to_clusters[:, 2][anomalies], edgecolors='r', facecolors='none')


    # Fine-tune figure; hide x ticks for top plots and y ticks for right plots
    plt.setp([a.get_xticklabels() for a in axarr[0, :]], visible=False)
    plt.setp([a.get_yticklabels() for a in axarr[:, 1]], visible=False)

    plt.savefig("distance_2d.png")


def plot_simple(df, y_kmeans, cluster_centers):
    plt.scatter(df.iloc[:, 0], df.iloc[:, 1], c=y_kmeans, s=50, cmap='viridis')
    plt.scatter(cluster_centers[:, 0], cluster_centers[:, 1], c='black', s=200, alpha=0.5)
    plt.savefig("simple_plot.png")


def anomaly_detection(df, clusterings, cluster_centers, percent_threshold, size_threshold):
    """
    Classifies points as outliers if they are greater than a percentage of the maximum distance from their centroid
    :param df: A dataframe of size (num points) x (num times) with the coordinates of each point
    :param clusterings: A list of length (num points) with the cluster index assignment for each point
    :param cluster_centers: A list of the centroid coordinates for each cluster
    :param percent_threshold: If a point is farther than this percentage of max distance, it is an outlier
    :param size_threshold: If a cluster is smaller than this, all points in that cluster are outliers
    :return: A list of boolean values of length (num points) which tells whether each point is an outlier
    """
    # get the point of the maximum distance from each cluster
    cluster_max = {}
    cluster_count = [0]*len(cluster_centers)
    index = 0
    for name, row in df.iterrows():
        cluster = clusterings[index]
        cluster_count[cluster] += 1
        if cluster not in cluster_max:
            cluster_max[cluster] = 0
        distance_to_center = metrics.pairwise.euclidean_distances([row.tolist()], [cluster_centers[cluster]])[0]
        if cluster_max[cluster] < distance_to_center:
            cluster_max[cluster] = distance_to_center
        index += 1

    # find all anomalies
    index = 0
    anomalous = [False] * len(clusterings)
    for name, row in df.iterrows():
        cluster = clusterings[index]
        distance_to_center = metrics.pairwise.euclidean_distances([row.tolist()], [cluster_centers[cluster]])[0]
        if cluster_count[cluster] < size_threshold: # if too small of cluster, all points anomalous
            anomalous[index] = True
        if distance_to_center > cluster_max[cluster] * percent_threshold: # if too far from cluster center, anomalous
            anomalous[index] = True
        index += 1

    return anomalous


def std_anomaly_detection(df, clusterings, cluster_centers, num_std, size_threshold):
    """

    :param df: A dataframe of size (num points) x (num times) with the coordinates of each point
    :param clusterings: A list of length (num points) with the cluster index assignment for each point
    :param cluster_centers: A list of the centroid coordinates for each cluster
    :param num_std: A point farther than this many std from mean distance from centroid is outlier
    :param size_threshold: If a cluster is smaller than this, all points in that cluster are outliers
    :return: A list of boolean values of length (num points) which tells whether each point is an outlier
    """
    stds = []
    means = []
    for i in range(len(cluster_centers)):
        points_in_cluster = [np.where(clusterings == i)]
        cluster_df = df.iloc[points_in_cluster[0][0]]
        distance_df = metrics.pairwise.euclidean_distances(cluster_df, [cluster_centers[i]])
        stds.append(distance_df.std(axis=0)[0])
        means.append(distance_df.mean(axis=0)[0])

    cluster_count = [0]*len(cluster_centers)
    for i in range(len(clusterings)):
        cluster = clusterings[i]
        cluster_count[cluster] += 1

    index = 0
    anomalous = [False] * len(clusterings)
    for name, row in df.iterrows():
        cluster = clusterings[index]
        distance_to_center = metrics.pairwise.euclidean_distances([row.tolist()], [cluster_centers[cluster]])[0]
        if cluster_count[cluster] < size_threshold:  # if too small of cluster, all points anomalous
            anomalous[index] = True
        if distance_to_center > means[cluster] + num_std*stds[cluster]:  # if too far from cluster center, anomalous
            anomalous[index] = True
        index += 1

    return anomalous


def plot_timeline(df, clusterings, cluster_centers, anomalous, title, xlab, ylab, xtick_names):
    """
    Plots the values per time of all points in a cluster, highlighting anomalies as red
    :param df: dataframe of points
    :param clusterings: A list of length (num points) with the cluster index assignment for each point
    :param cluster_centers: A list of the centroid coordinates for each cluster
    :param anomalous: A list of boolean values of length (num points) which tells whether each point is an outlier
    :return: None
    """
    index = 0
    times = pd.to_datetime(df.columns).to_pydatetime()
    for name, row in df.iterrows():
        cluster = clusterings[index]
        if anomalous[index]:
            color = "red"
            # print("drawing point " + str(index) + " for cluster " + str(cluster))
        else:
            color = "black"
        plt.figure(cluster)
        plt.plot(times, row.tolist(), c=color)
        index += 1

    hours = mdates.HourLocator()
    hourFormat = mdates.DateFormatter("%H:%M")

    for i in range(len(cluster_centers)):
        plt.figure(i)
        ax = plt.axes()
        ax.xaxis.set_major_locator(hours)
        ax.xaxis.set_major_formatter(hourFormat)
        #plt.plot(cluster_centers[i], c="blue")
        #plt.ylim(-5,105)
        plt.xlim(times[0], times[-1])
        plt.title(title + ": Cluster " + str(i))
        plt.ylabel(ylab)
        plt.xlabel(xlab)
        plt.xticks(rotation=70)
        plt.savefig("cluster"+str(i)+"_timeline.png", bbox_inches='tight')


def plot_anomalies_all(df, anomalous):
    """
    Plots values per time of all points, highlighting anomalies as red
    :param df: dataframe of points
    :param anomalous: A list of boolean values of length (num points) which tells whether each point is an outlier
    :return: None
    """
    index = 0
    for name, row in df.iterrows():
        if not anomalous[index]:
            plt.plot(row.tolist(), c="black")
        index += 1

    index = 0
    for name, row in df.iterrows():
        if anomalous[index]:
            plt.plot(row.tolist(), c="red")
        index += 1

    plt.savefig("all_anomalies.png", bbox_inches = 'tight')


def cluster_and_plot_anomalies(df, n_clusters, n_init, std_threshold, size_threshold, title, xlab, ylab, xtick_names):

    # cluster and find anomalies
    kmeans = KMeans(n_clusters=n_clusters, init='k-means++', n_init=n_init)
    try:
        clusterings = kmeans.fit_predict(df)
    except ValueError:
        old_rows = df.shape[0]
        df = df.dropna(axis = 0, how = 'any')
        new_rows = df.shape[0]
        print("Dropped " + str(old_rows - new_rows) + " rows with NaN values, " + str(new_rows) + " rows remaining")
        clusterings = kmeans.fit_predict(df)
    cluster_centers = kmeans.cluster_centers_.tolist()
    anomalous = std_anomaly_detection(df, clusterings, cluster_centers, std_threshold, size_threshold)

    print(metrics.silhouette_score(df, clusterings))

    plot_timeline(df, clusterings, cluster_centers, anomalous, title, xlab, ylab, xtick_names)
    #plot_cluster_distance_3d(dist_to_clusters=kmeans.transform(df), labels=kmeans.labels_)
    #plot_cluster_distance_2d(dist_to_clusters=kmeans.transform(df),
                             #labels=kmeans.labels_, anomalies=anomalous)


def return_anomalous_points(df, n_clusters, n_init, std_threshold, size_threshold):
    '''
    Returns a list of point names that are anomalous
    :param df: Pandas dataframe, points are rows, timestamps are columns
    :param n_clusters: int number of desired clusters (we've been using 3 or 4)
    :param n_init: int number of times it should run kmeans (it will pick the best of these runs)
    :param std_threshold: int that if a point is greater than std_threshold standard deviations from the mean,
            it will be flagged as an anomaly
    :param size_threshold: int of minimum cluster size before all its points are considered anomalous
    :return: anomalous_point_names, a list of point names that we have flagged as anomalies
    '''
    kmeans = KMeans(n_clusters=n_clusters, init='k-means++', n_init=n_init)
    # TODO: account for possible NaN values
    clusterings = kmeans.fit_predict(df)
    cluster_centers = kmeans.cluster_centers_.tolist()
    anomalous = std_anomaly_detection(df, clusterings, cluster_centers, std_threshold, size_threshold)

    anomalous_point_names = df[anomalous].index._data

    return anomalous_point_names


def get_xtick_names(num_xticks, possible_names):
    step_size = round(len(possible_names) / float(num_xticks))
    return list(range(0,len(possible_names), step_size))




def plot_main():
    #df = grabAllPointsInBuildingByType(27, '2017-12-20 00:00', '2017-12-21 00:00', 'ROOM TEMP')
    df = api.building_values_in_range_by_type(45, '2017-12-27 00:00', '2017-12-28 00:00', 4922)
    df = pivot_df(df)
    # start = date(2017,11,1)
    # end = date(2018,1,31)
    # df = grabAndPivotAllDaysInRangeForPoint(938, start, end)
    title = "Room Temp in Evans on 12/27"
    xlab = "Time of day"
    ylab = "Room temperature"
    xtick_names = get_xtick_names(24, df.columns)
    cluster_and_plot_anomalies(df, 3, 10, 3,  df.shape[0]*0.03, title, xlab, ylab, xtick_names)

def return_main():
    # df = grabAllPointsInBuildingByType(27, '2017-12-20 00:00', '2017-12-21 00:00', 'ROOM TEMP')
    #df = pivot_df(df)
    start = date(2016,6,1)
    end = date(2016,8,31)
    df = grabAndPivotAllDaysInRangeForPoint(1652, start, end)
    #cluster_and_plot_anomalies(df, 4, 10, 3,  df.shape[0]*0.03)
    an_pt = return_anomalous_points(df, 4, 10, 3, df.shape[0]*0.03)
    print(an_pt)

if __name__ == '__main__':
    #plot_anomalies_all(4, 10)
    plot_main()