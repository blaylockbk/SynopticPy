.. raw :: html

   <div align=center>
   <img src="_static/SynopticPy_white.svg" style="background-color:transparent" width=350 class='only-dark' />
   </div>
   <br>
   <br>

.. raw :: html

   <div align=center>
   <img src="_static/SynopticPy_blue.svg" style="background-color:transparent" width=350 class='only-light' />
   </div>
   <br>
   <br>

.. toctree::
   :maxdepth: 3
   :hidden:

   /user_guide/index
   /reference_guide/index



===================================
SynopticPy: Synoptic API for Python
===================================

`Synoptic's Weather API <https://docs.synopticdata.com/services/weather-data-api>`_ provides real-time and historical surface-based weather and environmental observations for thousands of mesonet stations, and the `open-access data <https://synopticdata.com/pricing/open-access-pricing/>`_ is *free*. More data and enhanced services may be purchased (from Synoptic, not me).

I'm a Synoptic user. I wrote this package to conveniently request data from Synoptic in a Pythonic way and convert its returned JSON to a `Polars DataFrame <https://docs.pola.rs/>`_.

.. code:: python

   from datetime import timedelta
   from synoptic import TimeSeries

   df = TimeSeries(
      stid="wbb",
      recent=timedelta(minutes=30)
   ).df()

.. raw :: html

   <img src="_static/json_to_polars.png" style="background-color:transparent" />


.. important::
   🎟️ You need a Synoptic API token before using SynopticPy. `Register for a free Synoptic account
   <https://customer.synopticdata.com/signup-targeted/?signup=open-access>`_.

I'm sharing this package to improve my skills with Polars and gain more experience in building and maintaining open-source Python packages. If you are using Synoptic's API and came across this package, I hope you find it useful.

**Best of Luck 🍀**

-Brian

.. seealso::
   📈 The `StationPy Web App <https://blaylockbk.github.io/SynopticPy/timeseries>`_ lets you plot station data in your browser powered by `pyscript <https://pyscript.net/>`_.
