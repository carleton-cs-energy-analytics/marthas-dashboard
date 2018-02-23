Energy Analytics Comps
======================

.. _energy-analytics-comps https://github.com/carleton-cs-energy-analytics/energy-analytics-comps
.. _marthas_dashbaord https://github.com/carleton-cs-energy-analytics/marthas-dashboard

Welcome! Our COMPS project is currently split into two separate repositories: ::

   carleton-cs-energy-analytics
     |
     +-- energy-analytics-comps
     +-- marthas-dashboard

* The energy-analytics-comps repo acquires energy data, imports it into the database, and serves data via an API at: http://energycomps.its.carleton.edu/api/index.php.
* The marthas-dashboard repo queries the API, and serves useful visualizations at: http://energycomps.its.carleton.edu/dashboard/. Analysis lives over here, too.

Documentation for both repos is provided below.

Documentation
-------------

.. toctree::
   :maxdepth: 1
   :caption: energy-analytics-comps

   database/data_importers.md
   database/database_structure.md
   database/api.md

.. toctree::
   :maxdepth: 1
   :caption: marthas-dashboard

   dashboard/getting_started.md
   dashboard/analysis/analysis_done_so_far.md
   dashboard/analysis/anomaly_detection_using_kmeans_clustering.md
