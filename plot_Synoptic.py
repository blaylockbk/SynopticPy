## Brian Blaylock
## September 1, 2020

"""
===========================
Plot Data From Synoptic API
===========================
Quick plots from the Synoptic API
"""

import matplotlib.pyplot as plt
import numpy as np

from get_Synoptic import *

def plot_timeseries(cmap=None, 
                    plot_kwargs=dict(marker='.', markersize=3),
                    **params):
    '''
    Plot timeseries from multiple stations on a single plot for each variable.
    
    Parameters
    ----------
    cmap : str
        A matplotlib named colormap to cycle colors (e.g. 'Spectral', 'Blues')
    plot_kwargs : dict
        kwargs for the plotted lines
    params : keyword arguments
        Same as for `stations_timeseries`
    '''
    
    # Get the data
    a = stations_timeseries(**params)
    
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
        if var == 'metar':
            continue
        fig, ax = plt.subplots(1,1,figsize=[16,8])
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

    