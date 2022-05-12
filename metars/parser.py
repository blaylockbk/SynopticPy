## Graciously provided by Karl Schneider (https://github.com/karlwx)
## October 19, 2021
## Example: https://github.com/karlwx/Model-Scripts/blob/main/SynopticData%20Suface%20Observations.ipynb


import fractions
import re

import metpy.calc as mpcalc
import numpy as np
import pandas as pd
from metpy.units import units


def metar_parser(metar, dt=None):
    """Parses metars for important variables

    Parameters
    ----------
    metar : str
        The METAR observation string to parse
    dt : datetime.datetime
        A datetime object representing the time of observation
        if dt is passed, the 'time' variable returned will be the datetime object
        otherwise, the METAR time string will be returned (DDHHMM)
    """

    # Station name, date, and time
    stid = re.findall("^(?:METAR|SPECI\s)?(\w{4})", metar)[0]
    time = re.findall("(\d{6})Z", metar)[0]
    hour = time[2:4]

    if dt:
        time = dt  # return time as datetime object if dt is passed, else return string from METAR

    # Wind speed, direction, gust
    try:
        wind = re.findall("\s(\d{3}|VRB)(\d?\d{2})(?:G(\d?\d{2}))?KT\s", metar)[0]
    except:
        wind = None
    try:
        wind_speed = int(wind[1])
    except:
        wind_speed = np.nan
    try:
        wind_dir = int(wind[0])
        wind_speed = int(wind[1])
        components = mpcalc.wind_components(
            wind_speed * units.kt, wind_dir * units.degrees
        )
        u_wind = components[0].magnitude
        v_wind = components[1].magnitude
    except:
        wind_dir = np.nan
        u_wind = np.nan
        v_wind = np.nan
    try:
        wind_gust = int(wind[2])
    except:
        wind_gust = np.nan

    # Visibility and clouds
    try:
        vis = re.findall("\s(\d+\s?\d?\/?\d?\d?)SM\s", metar)[0]
        vis = vis.split(" ")
        visibility = sum([float(fractions.Fraction(token)) for token in vis])
    except:
        visibility = np.nan

    try:
        cloud_layers = re.findall("(CLR|FEW|SCT|BKN|OVC|VV)(\d{3})?", metar)
        cloud_code = cloud_layers[-1][0]
        cloud_code_mapping = dict(
            CLR=0.0, FEW=25.0, SCT=50.0, BKN=75.0, OVC=100.0, VV=100.0
        )
        cloud_total = cloud_code_mapping[cloud_code]
    except:
        cloud_total = np.nan
    try:
        cloud_base = int(cloud_layers[0][1]) * 100
    except:
        cloud_base = np.nan

    # Present weather
    wx_re = re.compile(
        (
            "\s(TSNO|VA|FU|HZ|DU|BLDU|SA|BLSA|VCBLSAVCBLDU|BLPY|PO|VCPO|VCDS|VCSS|BR|BCBR|BC|MIFG|VCTS|VIRGA"
            "|VCSH|TS|THDR|VCTSHZ|TSFZFG|TSBR|TSDZ|SQ|FC|\+FC|DS|SS|DRSA|DRDU|TSUP|\+DS|\+SS|-BLSN|BLSN|\+BLSN|"
            "VCBLSN|DRSN|\+DRSN|VCFG|BCFG|PRFG|FG|FZFG|-VCTSDZ|-DZ|-DZBR|VCTSDZ|DZ|\+VCTSDZ|\+DZ|-FZDZ|-FZDZSN|"
            "FZDZ|\+FZDZ|FZDZSN|-DZRA|DZRA|\+DZRA|-VCTSRA|-RA|-RABR|VCTSRA|RA|RABR|RAFG|\+VCTSRA|\+RA|-FZRA|"
            "-FZRASN|-FZRABR|-FZRAPL|-FZRASNPL|TSFZRAPL|-TSFZRA|FZRA|\+FZRA|FZRASN|TSFZRA|-DZSN|-RASN|-SNRA|-SNDZ|"
            "RASN|\+RASN|SNRA|DZSN|SNDZ|\+DZSN|\+SNDZ|-VCTSSN|-SN|-SNBR|VCTSSN|SN|\+VCTSSN|\+SN|VCTSUP|IN|-UP|UP|"
            "\+UP|-SNSG|SG|-SG|IC|-FZDZPL|-FZDZPLSN|FZDZPL|-FZRAPLSN|FZRAPL|\+FZRAPL|-RAPL|-RASNPL|-RAPLSN|"
            "\+RAPL|RAPL|-SNPL|SNPL|-PL|PL|-PLSN|-PLRA|PLRA|-PLDZ|\+PL|PLSN|PLUP|\+PLSN|-SH|-SHRA|SH|SHRA|\+SH|"
            "\+SHRA|-SHRASN|-SHSNRA|\+SHRABR|SHRASN|\+SHRASN|SHSNRA|\+SHSNRA|-SHSN|SHSN|\+SHSN|-GS|-SHGS|FZRAPLGS|"
            "-SNGS|GSPLSN|GSPL|PLGSSN|GS|SHGS|\+GS|\+SHGS|-GR|-SHGR|-SNGR|GR|SHGR|\+GR|\+SHGR|-TSRA|TSRA|TSSN|"
            "TSPL|-TSDZ|-TSSN|-TSPL|TSPLSN|TSSNPL|-TSSNPL|TSRAGS|TSGS|TSGR|\+TSRA|\+TSSN|\+TSPL|\+TSPLSN|TSSA|"
            "TSDS|TSDU|\+TSGS|\+TSGR)\s"
        )
    )
    # Present weather
    try:
        wx = re.findall(wx_re, metar)[0]
    except:
        wx = None
    try:
        wx2 = re.findall(wx_re, metar)[1]
    except:
        wx2 = None
    try:
        wx3 = re.findall(wx_re, metar)[2]
    except:
        wx3 = None

    # Temperature and dewpoint
    try:
        # The standard ob to the nearest degree C
        group = re.findall("\s(M?\d{2})\/(M?\d{2})\s", metar)[0]
        temp = (
            (
                -float(group[0][1:]) * units.degC
                if group[0][0] == "M"
                else float(group[0]) * units.degC
            ).to("degF")
        ).magnitude
        dew = (
            (
                -float(group[1][1:]) * units.degC
                if group[1][0] == "M"
                else float(group[1]) * units.degC
            ).to("degF")
        ).magnitude
    except:
        temp = np.nan
        dew = np.nan
    try:
        # If T group exists, take these more precise numbers
        group = re.findall("\sT(\d{4})(\d{4})", metar)[0]
        temp = (
            (
                -float(group[0][1:]) / 10 * units.degC
                if group[0][0] == "1"
                else float(group[0]) / 10 * units.degC
            ).to("degF")
        ).magnitude
        dew = (
            (
                -float(group[1][1:]) / 10 * units.degC
                if group[1][0] == "1"
                else float(group[1]) / 10 * units.degC
            ).to("degF")
        ).magnitude
    except:
        None

    # Altimeter and SLP
    try:
        alti = float(re.findall("\sA(\d{4})\s", metar)[0]) / 100
    except:
        alti = np.nan
    try:
        slp = re.findall("\sSLP(\d{3})", metar)[0]
        if int(slp[0]) > 4:  # Logic for leading 9 or 10
            slp = float("9" + slp) / 10
        else:
            slp = float("10" + slp) / 10
    except:
        slp = np.nan

    # Precip groups, snow depth
    try:
        precip_1hr = float(re.findall("\sP(\d{4})", metar)[0]) / 100
    except:
        precip_1hr = np.nan
    try:
        precip_24hr = float(re.findall("\s7(\d{4})", metar)[0]) / 100
    except:
        precip_24hr = np.nan
    try:
        if hour in ["23", "05", "11", "17"]:
            precip_6hr = float(re.findall("\s6(\d{4})", metar)[0]) / 100
            precip_3hr = np.nan
        else:
            precip_6hr = np.nan
            precip_3hr = float(re.findall("\s6(\d{4})", metar)[0]) / 100
    except:
        precip_6hr = np.nan
        precip_3hr = np.nan
    try:
        snow_d = int(re.findall("\s4\/(\d{3})", metar)[0])
    except:
        snow_d = np.nan

    # Max and min temperatures
    try:
        group = re.findall("\s1(\d{4})\s2(\d{4})", metar)[0]
        temp_6hrmax = round(
            (
                (
                    -float(group[0][1:]) / 10 * units.degC
                    if group[0][0] == "1"
                    else float(group[0]) / 10 * units.degC
                ).to("degF")
            ).magnitude
        )
        temp_6hrmin = round(
            (
                (
                    -float(group[1][1:]) / 10 * units.degC
                    if group[1][0] == "1"
                    else float(group[1]) / 10 * units.degC
                ).to("degF")
            ).magnitude
        )
    except:
        temp_6hrmax = np.nan
        temp_6hrmin = np.nan
    try:
        group = re.findall("\s4(\d{4})(\d{4})", metar)[0]
        temp_24hrmax = round(
            (
                (
                    -float(group[0][1:]) / 10 * units.degC
                    if group[0][0] == "1"
                    else float(group[0]) / 10 * units.degC
                ).to("degF")
            ).magnitude
        )
        temp_24hrmin = round(
            (
                (
                    -float(group[1][1:]) / 10 * units.degC
                    if group[1][0] == "1"
                    else float(group[1]) / 10 * units.degC
                ).to("degF")
            ).magnitude
        )
    except:
        temp_24hrmax = np.nan
        temp_24hrmin = np.nan

    return dict(
        stid=stid,
        time=time,
        temp_f=temp,
        dew_f=dew,
        wx=wx,
        wx2=wx2,
        wx3=wx3,
        wind_dir_deg=wind_dir,
        wind_speed_kt=wind_speed,
        wind_gust_kt=wind_gust,
        u_wind_kt=u_wind,
        v_wind_kt=v_wind,
        visibility_mi=visibility,
        cloud_total_pct=cloud_total,
        cloud_base_ft=cloud_base,
        alti_inhg=alti,
        slp_mb=slp,
        temp_6hrmax_f=temp_6hrmax,
        temp_6hrmin_f=temp_6hrmin,
        temp_24hrmax_f=temp_24hrmax,
        temp_24hrmin_f=temp_24hrmin,
        precip_1hr_in=precip_1hr,
        precip_3hr_in=precip_3hr,
        precip_6hr_in=precip_6hr,
        precip_24hr_in=precip_24hr,
        snowd_in=snow_d,
        metar=metar,
    )


def station_data_parser(stndata):
    """Parses station data for plotting"""
    stndata = stndata["STATION"]
    data = []
    for stn in stndata:
        try:
            speed = stn["OBSERVATIONS"]["wind_speed_value_1"]["value"] * units("knot")
            direct = stn["OBSERVATIONS"]["wind_direction_value_1"]["value"] * units(
                "degree"
            )
            u, v = mpcalc.wind_components(speed, direct)
            stn = dict(
                stid=stn["STID"],
                lat=float(stn["LATITUDE"]),
                lon=float(stn["LONGITUDE"]),
                temp=stn["OBSERVATIONS"]["air_temp_value_1"]["value"] or np.nan,
                dew=stn["OBSERVATIONS"]["dew_point_temperature_value_1"]["value"]
                or np.nan,
                slp=stn["OBSERVATIONS"]["sea_level_pressure_value_1d"]["value"]
                or np.nan,
                u=u.magnitude,
                v=v.magnitude,
            )
            data.append(stn)
        except KeyError:
            continue

    return pd.DataFrame(data).to_dict("list")
