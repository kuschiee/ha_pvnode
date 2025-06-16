"""DataUpdateCoordinator for the PVNode integration."""

from __future__ import annotations

from datetime import timedelta

from .pvnode import Estimate, PVNode, PVNodeConnectionError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.components.weather import (
     ATTR_CONDITION_CLEAR_NIGHT,
     ATTR_CONDITION_SUNNY
)

from homeassistant.helpers import sun

from .const import (
    DOMAIN, 
    MANUFACTURER,
    MODEL,
    URL,
    CONF_ORIENTATION,
    CONF_SLOPE,
    CONF_KWP,
    CONF_INSTALLATION_HEIGHT,
    CONF_INSTALLATION_DATE,
    CONF_TECHNOLOGY,
    CONF_OBSTRUCTION,
    CONF_WEATHER_ENABLED,
    LOGGER,
    CONDITION_MAP
)

type PVNodeConfigEntry = ConfigEntry[PVNodeDataUpdateCoordinator]


class PVNodeDataUpdateCoordinator(DataUpdateCoordinator[Estimate]):
    """The PVNode Data Update Coordinator."""

    config_entry: PVNodeConfigEntry

    def __init__(self, hass: HomeAssistant, entry: PVNodeConfigEntry) -> None:
        """Initialize the PVNode coordinator."""

        self.forecast = PVNode(
            api_key=entry.options[CONF_API_KEY],
            latitude=entry.data[CONF_LATITUDE],
            longitude=entry.data[CONF_LONGITUDE],
            orientation=entry.options[CONF_ORIENTATION],
            slope=entry.options[CONF_SLOPE],
            kWp=entry.options[CONF_KWP],
            instheight=entry.options[CONF_INSTALLATION_HEIGHT],
            instdate=entry.options[CONF_INSTALLATION_DATE],
            time_zone=hass.config.time_zone,
            technology=entry.options[CONF_TECHNOLOGY],
            obstruction=entry.options[CONF_OBSTRUCTION],
            weather_enabled=entry.data[CONF_WEATHER_ENABLED]
        )

        self.entry_id = entry.entry_id
        update_interval = timedelta(minutes=15)

        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> Estimate:
        """Fetch PVNode estimates."""
        try:
            return await self.forecast.estimate()
        except PVNodeConnectionError as error:
            raise UpdateFailed(error) from error

    def get_device_info(self):
        return DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self.entry_id)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name="Forecast",
            configuration_url=URL,
        )

    def format_condition(self, weathercode, date = None):
         condition = CONDITION_MAP.get(weathercode)
         sunisup = True
         if date is None:
             sunisup = sun.is_up(self.hass)
         else:
             sunisup = sun.is_up(self.hass, date)
         if condition == ATTR_CONDITION_SUNNY and not sunisup:
             condition = ATTR_CONDITION_CLEAR_NIGHT
         return condition 
