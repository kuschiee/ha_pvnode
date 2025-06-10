"""Constants for the PVNode integration."""

from __future__ import annotations

import logging

DOMAIN = "pvnode"
LOGGER = logging.getLogger(__package__)

CONF_ORIENTATION= "orientation"
CONF_SLOPE = "slope"
CONF_KWP = "kwp"
CONF_BUILDYEAR = "buildyear"
CONF_INSTALLATION_HEIGHT = "instheight"
CONF_INSTALLATION_DATE = "instdate"
CONF_TECHNOLOGY = "technology"
CONF_OBSTRUCTION = "obstruction"

TECHNOLOGIES = ['', 'perc', 'monosi', 'multisi', 'cdte', 'topcon']
