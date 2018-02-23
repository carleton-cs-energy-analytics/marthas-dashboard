# Anomaly Detection

We are looking into how we can tell if a point is behaving irregularly.  Being able to look at a time range and select specific points to look at will help reduce the amount of data facilities needs to look at in order to troubleshoot in a given building.  We decided that away to do this in the early stages would be to use kmeans clustering, which is an easy-to implement algorithm that we can use through [sklearn](http://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html).  Some research that Kiya looked into can be seen [here](https://docs.google.com/document/d/1pAwgF-BuBvSh6PzzZw4h9ajlyzoIZxXEAbUpgCAs1FU).

We chose this approach because:

* We don't know enough about our data to develop a model-based detection system
* Clustering is unsupervised, meaning we don't already need to know what points are anomalous
* By clustering, we don't expect every point to behave exactly the same way but we do expect some patterns between similar points.

## Kmeans

[Kmeans](https://en.wikipedia.org/wiki/K-means_clustering) is a clustering analysis algorithm that, given data points and a number, n, of desired clusters will categorize m-dimensional data points into n categories.

### Insert an example here with a couple pictures
https://docs.google.com/presentation/d/19NAHDsxQbjwuffGsPYSBg3DXJbbPDzCakr4zOrQdhdE/edit#slide=id.g31e789b1e2_0_1

### Insert how to run it here

```
analysis/anomaly_detection/anomaly_detection.py
```

Follow formatting in plot_cluster to get the data that is shown in above presentation
