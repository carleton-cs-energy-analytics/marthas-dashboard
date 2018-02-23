.. marthas-dashboard documentation master file, created by
   sphinx-quickstart on Thu Feb 22 17:21:50 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Energy Analytics Comps
======================

Welcome! Our COMPS project is currently split into two separate repositories: ::

   carleton-cs-energy-analytics
     |
     +-- energy-analytics-comps
     +-- marthas-dashboard

- The [`energy-analytics-comps`](https://github.com/carleton-cs-energy-analytics/energy-analytics-comps) repo acquires energy data, imports it into the database, and serves data via an API at: http://energycomps.its.carleton.edu/api/index.php.

- The [`marthas-dashboard`](https://github.com/carleton-cs-energy-analytics/marthas-dashboard) repo queries the API, and serves useful visualizations at: http://energycomps.its.carleton.edu/dashboard/. Analysis lives over here, too.

energy-analytics-comps
----------------------

.. toctree::
   :maxdepth: 1
   :caption: energy-analytics-comps

   database/data_importers.md
   database/database_structure.md
   database/api.md

martha's dashboard
------------------

.. toctree::
   :maxdepth: 1

   dashboard/getting_started.md
   dashboard/analysis_done_so_far.md

Data-Importers.md



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
