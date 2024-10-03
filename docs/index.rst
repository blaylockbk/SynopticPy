.. raw :: html

   <img src="_static/SynopticPy_white.svg" style="background-color:transparent; max-width:300;" class='only-dark' />

.. raw :: html

   <img src="_static/SynopticPy_blue.svg" style="background-color:transparent; max-width:300;" class='only-light' />

================================================
The (unofficial) Synoptic Weather API for Python
================================================

.. toctree::
   :maxdepth: 3
   :hidden:

   /user_guide/index
   /reference_guide/index

Synoptic's `Weather API <https://docs.synopticdata.com/services/weather-data-api>`_ gives you access to real-time and historical surface-based weather and environmental observations for thousands of stations, and the `open-access data <https://synopticdata.com/pricing/open-access-pricing/>`_ is free. More data and enhances services may be `purchased <https://synopticdata.com/pricing/>`_ (from Synoptic, not me).

I'm a Synoptic user. I wrote these functions to conveniently request data from Synoptic and convert its returned JSON to a `Polars DataFrame <https://docs.pola.rs/>`_. I'm sharing this as an open source project because I think these might be helpful to others who are getting started using the Synoptic API with Python. I also wrote this package to get more experience using Polars DataFrames.

.. raw :: html

   <img src="_static/json_to_polars.png" style="background-color:transparent; max-width:300;" />


.. important::
   🎟️ You will need a Synoptic API token before using SynopticPy. `Register for a free Synoptic account
   <https://customer.synopticdata.com/signup-targeted/?signup=open-access>`_.

If you have stumbled across this package, I hope you find it useful.

**Best of Luck 🍀**

-Brian

.. seealso::
   You can create timeseries of observations from weather stations using the `Station Timeseries Web App <https://blaylockbk.github.io/SynopticPy/timeseries>`_. This is a quick way to use SynopticPy without writing any code yourself.
