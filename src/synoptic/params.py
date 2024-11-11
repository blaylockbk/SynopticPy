"""Allowed input parameters for each service."""

import warnings

station_selectors = {
    "stid",
    "state",
    "country",
    "nwszone",
    "nwsfirezone",
    "cwa",
    "gacc",
    "subgacc",
    "county",
    "vars",
    "varsoperator",
    "network",
    "radius",
    "bbox",
    "height",
    "width",
    "spacing",
    "networkimportance",
    "status",
    "complete",
    "fields",  # NOT SUPPORTED
}

qc_options = {"qc", "qc_remove_data", "qc_flags", "qc_checks"}

params_timeseries = (
    station_selectors
    | {"token", "start", "end", "recent"}
    | {
        "obtimezone",  # IGNORED
        "showemptystations",
        "showemptyvars",
        "units",
        "precip",
        "all_reports",
        "hfmetars",
        "sensorvars",
        "timeformat",  # IGNORED
        "output",  # IGNORED
    }
    | qc_options
)

params_latest = (
    station_selectors
    | {"token"}
    | {
        "obtimezone",  # IGNORED
        "showemptystations",
        "showemptyvars",
        "units",
        "within",
        "minmax",
        "minmaxtype",
        "minmaxtimezone",
        "hfmetars",
        "sensorvars",
        "timeformat",  # IGNORED
        "output",  # IGNORED
    }
    | qc_options
)

params_nearesttime = (
    station_selectors
    | {"token", "attime", "within"}
    | {
        "obtimezone",  # IGNORED
        "showemptystations",
        "showemptyvars",
        "units",
        "hfmetars",
        "sensorvars",
        "timeformat",  # IGNORED
        "output",  # IGNORED
    }
    | qc_options
)

params_precipitation = (
    station_selectors
    | {"token", "start", "end", "recent"}
    | {
        "pmode",
        "interval",
        "obtimezone",  # IGNORED
        "showemptystations",
        "units",
        "interval_window",
        "all_reports",
        "timeformat",  # IGNORED
        "output",  # IGNORED
    }
)

params_qcsegments = (
    station_selectors
    | {"token", "start", "end", "recent"}
    | {
        "inside",
        "obtimezone",  # IGNORED
        "showemptystations",
        "qc_checks",
        "output",  # IGNORED
    }
)

params_latency = (
    station_selectors
    | {"token", "start", "end"}
    | {
        "obtimezone",  # IGNORED
        "showemptystations",
        "stats",
        "timeformat",  # IGNORED
        "output",  # IGNORED
    }
)

params_metadata = (
    station_selectors
    | {"token"}
    | {
        "complete",
        "sensorvars",
        "obrange",
        "timeformat",  # IGNORED
        "output",  # IGNORED
    }
)

params_qctypes = {"token", "shortname", "id"}
params_variables = {"token"}
params_networks = {"token", "id", "shortname", "sortby"}
params_networktypes = {"token", "id"}


def validate_params(service, **params):
    """Warn of any unexpected parameters."""
    expected = {
        "timeseries": params_timeseries,
        "latest": params_latest,
        "nearesttime": params_nearesttime,
        "precipitation": params_precipitation,
        "qcsegments": params_qcsegments,
        "latency": params_latency,
        "metadata": params_metadata,
        "qctypes": params_qctypes,
        "variables": params_variables,
        "networks": params_networks,
        "networktypes": params_networktypes,
    }

    unexpected_keys = set(params) - expected[service]

    for key in params:
        if key in unexpected_keys:
            warnings.warn(
                f"'{key}' is not an expected API parameter for the {service} service.",
                UserWarning,
            )
        if key in {"timeformat", "output", "fields", "obtimezone"}:
            warnings.warn(f"The '{key}' key is ignored by SynopticPy.", UserWarning)
