"""Support for the AccuWeather service."""

from __future__ import annotations

from typing import cast
from datetime import datetime

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_HUMIDITY,
    ATTR_FORECAST_NATIVE_PRECIPITATION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
    ATTR_FORECAST_TIME,
    SingleCoordinatorWeatherEntity,
    Forecast,
    WeatherEntityFeature,
)
from homeassistant.const import (
    UnitOfPrecipitationDepth,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    ATTRIBUTION,
    CONDITION_MAP, 
    CONF_WEATHER_ENABLED
)

from .coordinator import (
    PVNodeConfigEntry,
    PVNodeDataUpdateCoordinator
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: PVNodeConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add a PVNode weather entity from a config_entry."""
    if entry.data[CONF_WEATHER_ENABLED]:
        async_add_entities([PVNodeWeatherEntity(coordinator=entry.runtime_data, entry=entry)])


class PVNodeWeatherEntity(SingleCoordinatorWeatherEntity[PVNodeDataUpdateCoordinator]):
    """Define an PVNodeWeather entity."""

    _attr_attribution = ATTRIBUTION
    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_name = None

    _attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND

    _attr_supported_features = WeatherEntityFeature.FORECAST_HOURLY

    def __init__(self, coordinator: PVNodeDataUpdateCoordinator, entry: PVNodeConfigEntry) -> None:
        """Initialize."""
        super().__init__(coordinator)
        
        self._attr_unique_id = f"weather_{entry.unique_id}"
        self._attr_device_info = coordinator.get_device_info()

        self.coordinator = coordinator

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        return CONDITION_MAP.get(self.coordinator.data.weather_code_now)

    @property
    def native_temperature(self) -> float:
        """Return the temperature."""
        return cast(float, self.coordinator.data.weather_temperature_now)

    @property
    def humidity(self) -> int:
        """Return the humidity."""
        return cast(int, self.coordinator.data.weather_humidity_now)

    @property
    def native_wind_speed(self) -> float:
        """Return the wind speed."""
        return cast(float, self.coordinator.data.weather_wind_speed_now)

    @callback
    def _async_forecast_hourly(self) -> list[Forecast] | None:
        """Return the hourly forecast in native units."""
        return [
            {
                ATTR_FORECAST_TIME: date.isoformat(),
                ATTR_FORECAST_HUMIDITY: item["RH"],
                ATTR_FORECAST_NATIVE_TEMP: item["temp"],
                ATTR_FORECAST_NATIVE_PRECIPITATION: item["precip"],
                ATTR_FORECAST_NATIVE_WIND_SPEED: item["vwind"],
                ATTR_FORECAST_CONDITION: self.coordinator.format_condition(item["weather_code"], date),
            }
            for date, item in self.coordinator.data.weather_hours.items() if date >= datetime.now().replace(tzinfo=self.coordinator.data.api_timezone)
        ]
