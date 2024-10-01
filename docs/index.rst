.. image:: _static/SynopticPy_blue.png

===========================================
The Synoptic API for Python (unofficial)
===========================================

.. toctree::
   :maxdepth: 3
   :hidden:

   /user_guide/index
   /reference_guide/index

The `Synoptic Weather API <https://docs.synopticdata.com/services/weather-data-api>`_ (formerly MesoWest) gives you access to real-time and historical surface-based weather and environmental observations for thousands of stations. Synoptic's `open access data <https://synopticdata.com/pricing/open-access-pricing/>`_ is free. More data and enhances services are available through a `paid tier <https://synopticdata.com/pricing/>`_ (available through Synoptic, not me).

.. note::
   🌐 Before using SynopticPy, you will need a Synoptic API token. Register for a free open-access account at the `Synoptic API Webpage
   <https://customer.synopticdata.com/signup-targeted/?signup=open-access>`_.

.. note::
   You can create timeseries of observations from weather stations using the `Station Timeseries Web App <https://blaylockbk.github.io/SynopticPy/timeseries>`_. This is a quick way to use SynopticPy without writing any code yourself.

SynopticPy is a collection of functions I use to conveniently access data from the Synoptic API and convert its returned JSON to a `Polars DataFrame <https://docs.pola.rs/>`_. This may be helpful to others who are getting started with the Synoptic API and Python.

If you have stumbled across this package, I hope it is useful to you or at least gives you some ideas.

**Best of Luck 🍀**

-Brian
