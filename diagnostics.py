"""Diagnostics support for PVNode integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant

from . import PVNodeConfigEntry

TO_REDACT = {
    CONF_API_KEY,
    CONF_LATITUDE,
    CONF_LONGITUDE,
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: PVNodeConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data

    return {
        "entry": {
            "title": entry.title,
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": async_redact_data(entry.options, TO_REDACT),
        },
        "data": {
            "energy_production_today": coordinator.data.energy_production_today,
            "energy_production_today_remaining": coordinator.data.energy_production_today_remaining,
            "energy_production_tomorrow": coordinator.data.energy_production_tomorrow,
            "energy_current_hour": coordinator.data.energy_current_hour,
            "power_production_now": coordinator.data.power_production_now,
            "watts": {
                watt_datetime.isoformat(): watt_value
                for watt_datetime, watt_value in coordinator.data.watts.items()
            },
            "wh_hours": {
                wh_datetime.isoformat(): wh_value
                for wh_datetime, wh_value in coordinator.data.wh_hours.items()
            },
        },
        "account": {
            "last_update": coordinator.data.last_update
        }
    }