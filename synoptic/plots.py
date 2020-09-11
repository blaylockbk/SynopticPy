## Brian Blaylock
## September 1, 2020

"""
=====
Plots
=====
Quick plots from the Synoptic API
"""
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import synoptic.services as ss

plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = .5
plt.rcParams['axes.grid'] = True

def plot_timeseries(data=None,
                    cmap=None,
                    plot_kwargs=dict(marker='.', markersize=3),
                    figsize=(10,5),
                    verbose=True,
                    **params):
    '''
    Plot timeseries from multiple stations on a single plot for each variable.
    
    Parameters
    ----------
    data : output from stations_timeseries or None.
        The returned data from ``stations_timeseries``.
        If None, then the user must supply param keywords to make
        the API request for stations_timeseries here.
    cmap : str
        A matplotlib named colormap to cycle colors (e.g. 'Spectral', 'Blues').
        If None, use the default color cycle.
    plot_kwargs : dict
        kwargs for the plotted lines
    params : keyword arguments
        Same as for `stations_timeseries`
    '''
    
    # User must supply the data as returned from stations_timeseries
    # or the param keywords used to make the API request.
    if data is None:
        a = ss.stations_timeseries(verbose=verbose, **params)
    else:
        a = data
    
    if not isinstance(a, list):
        a = [a]

    # Get unique columns names for all stations
    variables = list({item for sublist in a for item in sublist})
    variables.sort()
    
    if cmap is None:
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    else:
        # Cycle colors based on a matplotlib colormap
        cmap = plt.get_cmap(cmap)
        colors = [cmap(i) for i in np.linspace(0, 1, len(a))]
    
    #################################
    # Make the Plots
    #################################
    for i, var in enumerate(variables):
        if var in ['metar', 'wind_cardinal_direction']:
            continue
        fig, ax = plt.subplots(1,1, figsize=figsize)
        var_str = var.replace('_', ' ').title()

        ax.set_title(f"{var_str}", loc='left')
        ax.set_xlabel('')

        for c, stn in zip(colors, a):
            if var in stn:
                if '_set_' in var:
                    var_units = stn.attrs['UNITS']['_'.join(var.split('_')[:-2])]
                else:
                    var_units = stn.attrs['UNITS'][var]
                stn[var].plot(ax=ax, label=stn.attrs['STID'], color=c, **plot_kwargs)
                ax.set_ylabel(f"{var_str} ({var_units})")

        plt.grid(linestyle='--', alpha=.5)
        plt.xlabel('')
        plt.legend()
        

def plot_timeseries_wind(data=None,
                        figsize=(10,5),
                        **params):
    """
    3-panel plot showing wind timeseries (wind speed/gust, direction, quiver)
    """
    
    # User must supply the data as returned from stations_timeseries
    # or the param keywords used to make the API request.
    if data is None:
        df = ss.stations_timeseries(verbose=verbose, **params)
    else:
        df = data

    fig, (ax1, ax2, ax3) = plt.subplots(3,1, sharex=True, figsize=figsize)

    ax1.plot(df.index, df.wind_speed, color='k')
    ax1.scatter(df.index, df.wind_gust, marker='+', color='tab:green')
    ax1.set_ylim(ymin=0)
    ax1.set_ylabel(f"Wind Speed ({df.attrs['UNITS']['wind_speed']})")
    ax1.set_title(f"{df.attrs['STID']} : {df.attrs['NAME']}", loc='left', fontweight='bold')

    ax2.scatter(df.index, df.wind_direction, marker='.', color='tab:orange')
    ax2.set_yticks(range(0,361,45))
    ax2.set_ylim(0,360)
    ax2.set_ylabel(f"Wind Direction ({df.attrs['UNITS']['wind_direction']})")

    ax2b = ax2.twinx()
    ax2b.set_yticks(range(0,361,45))
    ax2b.set_yticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW', 'N'])
    ax2b.set_ylim(0,360)

    ax3.quiver(df.index, df.wind_speed,
            df.wind_u, df.wind_v, df.wind_speed, cmap='Blues',
            edgecolors='k', linewidths=.3,
            zorder=5)

def map_timeseries(data=None, *, verbose=True,
                   ax=None, scale='10m', scatter_kwargs={},
                   text=True, text_kwargs={},
                   **params):
    """
    Plot a map of station locations returned from a ``stations_timeseries``.
    
    Use this to plot the locations of your requested stations on a map,
    but if you just need the map, don't bother getting the timeseries
    data, too. Use the map_metadata function instead.
    
    Parameters
    ----------
    data : output from stations_timeseries or None.
        The returned data from ``stations_timeseries``.
        If None, then the user must supply param keywords to make
        the API request for stations_timeseries here.
    params : keyword arguments for stations_timeseries
        Parameters for stations_timeseries API request.
        Required if ``data=None`.
    """
    if ax is None:
        # Create a new default axis
        ax = plt.subplot(projection=ccrs.PlateCarree())

    # User must supply the data as returned from stations_timeseries
    # or the param keywords used to make the API request.
    if data is None:
        a = ss.stations_timeseries(verbose=verbose, **params)
    else:
        a = data
        
    if not isinstance(a, list):
        a = [a]
        
    lats = [i.attrs['latitude'] for i in a]
    lons = [i.attrs['longitude'] for i in a]
    stid = [i.attrs['STID'] for i in a]
    
    ax.scatter(lons, lats, transform=ccrs.PlateCarree(), **scatter_kwargs)
    
    if text:
        for lon, lat, stn in zip(lons, lats, stid):
            ax.text(lon, lat, stn, transform=ccrs.PlateCarree(), **text_kwargs)
    
    ax.add_feature(cfeature.STATES.with_scale(scale))
    
    ax.set_title('Station Locations', loc='left', fontweight='bold')
    ax.set_title(f'Total Stations: {len(a)}', loc='right')    
    
def map_metadata(data=None, *, verbose=True,
                 ax=None, scale='10m', scatter_kwargs={},
                 text=True, text_kwargs={},
                 **params):
    """
    Plot a map of station locations returned from a ``stations_metadata``.
    
    Use this to plot the locations of your requested stations on a map,
    but if you just need the map.
    
    Parameters
    ----------
    data : output from stations_metadata or None.
        The returned data from ``stations_metadata``.
        If None, then the user must supply param keywords to make
        the API request for stations_timeseries here.
    params : keyword arguments for stations_timeseries
        Parameters for stations_metadata API request.
        Required if ``data=None`.
    """
    if ax is None:
        # Create a new default axis
        ax = plt.subplot(projection=ccrs.PlateCarree())

    # User must supply the data as returned from stations_timeseries
    # or the param keywords used to make the API request.
    if data is None:
        a = ss.stations_metadata(verbose=verbose, **params)
    else:
        a = data
                
    lats = df.loc['latitude']
    lons = df.loc['longitude']
    stid = df.loc['STID']
    
    ax.scatter(lons, lats, transform=ccrs.PlateCarree(), **scatter_kwargs)
    
    if text:
        for lon, lat, stn in zip(lons, lats, stid):
            ax.text(lon, lat, stn, transform=ccrs.PlateCarree(), **text_kwargs)
    
    ax.add_feature(cfeature.STATES.with_scale(scale))
    
    ax.set_title('Station Locations', loc='left', fontweight='bold')
    ax.set_title(f'Total Stations: {len(a)}', loc='right') 