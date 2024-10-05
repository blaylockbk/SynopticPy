.. raw :: html

   <div align=center>
   <img src="_static/SynopticPy_white.svg" style="background-color:transparent" width=350 class='only-dark' />
   </div>

.. raw :: html

   <div align=center>
   <img src="_static/SynopticPy_blue.svg" style="background-color:transparent" width=350 class='only-light' />
   </div>

.. raw :: html

   <div align=center>
   <h3>The (unofficial) Synoptic Weather API for Python</h3>
   </div>

.. toctree::
   :maxdepth: 3
   :hidden:

   /user_guide/index
   /reference_guide/index

Synoptic's `Weather API <https://docs.synopticdata.com/services/weather-data-api>`_ gives you access to real-time and historical surface-based weather and environmental observations for thousands of stations. Synoptic's `open-access data <https://synopticdata.com/pricing/open-access-pricing/>`_ is *free*. More data and enhances services may be purchased (from Synoptic, not me).

I'm a Synoptic user. I wrote SynopticPy to conveniently request data from Synoptic and convert its returned JSON to a `Polars DataFrame <https://docs.pola.rs/>`_. I'm sharing this package because (1) I want experience building and managing an open source package, (2) I want to get better at using Polars, and (3) I think this will be helpful to others using the Synoptic API with Python.

.. raw :: html

   <img src="_static/json_to_polars.png" style="background-color:transparent" />


.. code:: python

   from datetime import timedelta
   from synoptic import TimeSeries

   df = TimeSeries(
      stid="wbb",
      recent=timedelta(minutes=30)
   ).df

.. important::
   🎟️ You will need a Synoptic API token before using SynopticPy. `Register for a free Synoptic account
   <https://customer.synopticdata.com/signup-targeted/?signup=open-access>`_.

If you have stumbled across this package, I hope you find it useful.

**Best of Luck 🍀**

-Brian

.. seealso::
   📈 The `StationPy Web App <https://blaylockbk.github.io/SynopticPy/timeseries>`_ lets you plot station data from Synoptic in your browser powered by `pyscript <https://pyscript.net/>`_.
