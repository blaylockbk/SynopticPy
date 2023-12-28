"""Miscellaneous utilities for SynopticPy."""

import numpy as np

class ANSI:
    """ANSI color and escape codes."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    STRIKETHROUGH = "\033[9m"

    # Text color codes
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background color codes
    BLACK_BG = "\033[40m"
    RED_BG = "\033[41m"
    GREEN_BG = "\033[42m"
    YELLOW_BG = "\033[43m"
    BLUE_BG = "\033[44m"
    MAGENTA_BG = "\033[45m"
    CYAN_BG = "\033[46m"
    WHITE_BG = "\033[47m"

    @staticmethod
    def text(text, color):
        """Show ANSI-colored text.

        Examples
        --------
        >>> print(f"Color {ANSI.text('me', ANSI.GREEN)}.")
        """
        return f"{color}{text}{ANSI.RESET}"



def spddir_to_uv(wspd, wdir):
    """
    Calculate the u and v wind components from wind speed and direction.

    Parameters
    ----------
    wspd, wdir : array_like
        Arrays of wind speed and wind direction (in degrees)

    Returns
    -------
    u and v wind components

    """
    if isinstance(wspd, list) or isinstance(wdir, list):
        wspd = np.array(wspd, dtype=float)
        wdir = np.array(wdir, dtype=float)

    rad = 4.0 * np.arctan(1) / 180.0
    u = -wspd * np.sin(rad * wdir)
    v = -wspd * np.cos(rad * wdir)

    # If the speed is zero, then u and v should be set to zero (not NaN)
    if hasattr(u, "__len__"):
        u[np.where(wspd == 0)] = 0
        v[np.where(wspd == 0)] = 0
    elif wspd == 0:
        u = float(0)
        v = float(0)

    return np.round(u, 3), np.round(v, 3)
