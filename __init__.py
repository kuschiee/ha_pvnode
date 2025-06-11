"""The PVNode integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_WEATHER_ENABLED
)

from .coordinator import PVNodeConfigEntry, PVNodeDataUpdateCoordinator

PLATFORMS = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: PVNodeConfigEntry) -> bool:
    """Set up PVNode from a config entry."""
    coordinator = PVNodeDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    platforms = PLATFORMS
    if entry.options[CONF_WEATHER_ENABLED]:
        platforms.append(Platform.WEATHER)

    await hass.config_entries.async_forward_entry_setups(entry, platforms)

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: PVNodeConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_update_options(hass: HomeAssistant, entry: PVNodeConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)