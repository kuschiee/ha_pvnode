"""Constants for the PVNode integration."""

from __future__ import annotations

import logging
from typing import Final

from homeassistant.components.weather import (
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_FOG,
    ATTR_CONDITION_HAIL,
    ATTR_CONDITION_LIGHTNING,
    ATTR_CONDITION_PARTLYCLOUDY,
    ATTR_CONDITION_POURING,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SNOWY_RAINY,
    ATTR_CONDITION_SUNNY,
    ATTR_CONDITION_WINDY,
)

DOMAIN = "pvnode"
MANUFACTURER = "PVNode"
MODEL = "PVNode-0.0.1"
URL = "https://pvnode.com"
LOGGER = logging.getLogger(__package__)

CONF_ORIENTATION = "orientation"
CONF_SLOPE = "slope"
CONF_KWP = "kwp"
CONF_BUILDYEAR = "buildyear"
CONF_INSTALLATION_HEIGHT = "instheight"
CONF_INSTALLATION_DATE = "instdate"
CONF_TECHNOLOGY = "technology"
CONF_OBSTRUCTION = "obstruction"
CONF_WEATHER_ENABLED = "weather_enabled"

TECHNOLOGIES = ['', 'perc', 'monosi', 'multisi', 'cdte', 'topcon']

ATTRIBUTION = "Data provided by PVNode"
CONDITION_CLASSES: Final[dict[str, list[int]]] = {
#    ATTR_CONDITION_CLEAR_NIGHT: [],
    ATTR_CONDITION_CLOUDY: [3],
#    ATTR_CONDITION_EXCEPTIONAL: [],
    ATTR_CONDITION_FOG: [45,48],
    ATTR_CONDITION_HAIL: [96, 99],
    ATTR_CONDITION_LIGHTNING: [95],
#    ATTR_CONDITION_LIGHTNING_RAINY: [],
    ATTR_CONDITION_PARTLYCLOUDY: [2],
    ATTR_CONDITION_POURING: [82],
    ATTR_CONDITION_RAINY: [51, 53, 55, 56,57, 61, 63, 65],
    ATTR_CONDITION_SNOWY: [71, 73, 75],
    ATTR_CONDITION_SNOWY_RAINY: [77],
    ATTR_CONDITION_SUNNY: [0, 1],
    ATTR_CONDITION_WINDY: [32],
}
CONDITION_MAP = {
    cond_code: cond_ha
    for cond_ha, cond_codes in CONDITION_CLASSES.items()
    for cond_code in cond_codes
}
