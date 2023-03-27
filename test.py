#!/usr/bin/env python
# -*- coding: utf-8 -*-
from synoptic.services import stations_metadata, stations_timeseries
from datetime import timedelta

# in my case the config file is saved here:
# /home/gitpod/.config/SynopticPy/config.toml

df = stations_timeseries(
    stid='WBB',
    vars=['air_temp', 'wind_speed'],
    recent=timedelta(hours=1)
)

print(df)