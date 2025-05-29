"""DataUpdateCoordinator for the PVNode integration."""

from __future__ import annotations

from datetime import timedelta

from .pvnode import Estimate, PVNode, PVNodeConnectionError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_ORIENTATION,
    CONF_SLOPE,
    CONF_KWP,
    DOMAIN,
    LOGGER,
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
            kWp=entry.options[CONF_KWP]
        )

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