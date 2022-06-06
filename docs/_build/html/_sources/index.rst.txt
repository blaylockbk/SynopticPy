.. SynopticPy Docs documentation master file, created by
   sphinx-quickstart on Thu Dec 31 15:33:54 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: _static/SynopticPy_logo.png

===========================================
The Synoptic API for Python (unofficial)
===========================================

.. toctree::
   :maxdepth: 3
   :hidden:

   /user_guide/index
   /reference_guide/index

The `Synoptic Mesonet API <https://synopticdata.com/mesonet-api>`_ (formerly MesoWest) gives you access to real-time and historical surface-based weather and environmental observations for thousands of stations. Synoptic data access is `free <https://synopticdata.com/news/2022/3/15/synoptic-data-pbc-launches-new-open-access-weather-data-service>`_ for open-access data. More data and enhances services are available through a `paid tier <https://synopticdata.com/pricing>`_ (available through Synoptic, not me).

.. note::
   🌐 Register for a free account at the `Synoptic API Webpage
   <https://developers.synopticdata.com>`_. You will need to obtain an API token before using this python package.

   .. figure:: _static/synoptic_logo.png
      :width: 300

I wrote these functions to conveniently access data from the Synoptic API and convert the JSON data to a `Pandas DataFrame <https://pandas.pydata.org/docs/>`_. This may be helpful to others who are getting started with the Synoptic API and Python. The idea is loosely based on the obsolete `MesoPy <https://github.com/mesowx/MesoPy>`_ python wrapper, but returning the data as a Pandas DataFrame instead of a simple dictionary, making the retrieved data more ready-to-use.


If you have stumbled across this package, I hope it is useful to you or at least gives you some ideas.

**Best of Luck 🍀**

-Brian
