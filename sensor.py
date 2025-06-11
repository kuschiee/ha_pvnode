"""Support for the PVNode sensor service."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from .pvnode import Estimate

from homeassistant.components.sensor import (
    DOMAIN as SENSOR_DOMAIN,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfEnergy, 
    UnitOfPower,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfVolumetricFlux,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PVNodeConfigEntry
from .const import (
    DOMAIN, 
    MANUFACTURER,
    MODEL,
    URL,
    CONDITION_MAP,
    CONF_WEATHER_ENABLED
)
from .coordinator import PVNodeDataUpdateCoordinator


@dataclass(frozen=True)
class PVNodeSensorEntityDescription(SensorEntityDescription):
    """Describes a PVNode Sensor."""

    state: Callable[[Estimate], Any] | None = None


ENERGY_SENSORS: tuple[PVNodeSensorEntityDescription, ...] = (
    PVNodeSensorEntityDescription(
        key="energy_production_today",
        translation_key="energy_production_today",
        state=lambda estimate: estimate.energy_production_today,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=1,
    ),
    PVNodeSensorEntityDescription(
        key="energy_production_today_remaining",
        translation_key="energy_production_today_remaining",
        state=lambda estimate: estimate.energy_production_today_remaining,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=1,
    ),
    PVNodeSensorEntityDescription(
        key="energy_production_tomorrow",
        translation_key="energy_production_tomorrow",
        state=lambda estimate: estimate.energy_production_tomorrow,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=1,
    ),
    PVNodeSensorEntityDescription(
        key="power_highest_peak_time_today",
        translation_key="power_highest_peak_time_today",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    PVNodeSensorEntityDescription(
        key="power_highest_peak_time_tomorrow",
        translation_key="power_highest_peak_time_tomorrow",
        device_class=SensorDeviceClass.TIMESTAMP,
    ),
    PVNodeSensorEntityDescription(
        key="power_production_now",
        translation_key="power_production_now",
        device_class=SensorDeviceClass.POWER,
        state=lambda estimate: estimate.power_production_now,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0
    ),
    PVNodeSensorEntityDescription(
        key="power_production_next_hour",
        translation_key="power_production_next_hour",
        state=lambda estimate: estimate.power_production_at_time(
            estimate.now() + timedelta(hours=1)
        ),
        device_class=SensorDeviceClass.POWER,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0
    ),
    PVNodeSensorEntityDescription(
        key="power_production_next_12hours",
        translation_key="power_production_next_12hours",
        state=lambda estimate: estimate.power_production_at_time(
            estimate.now() + timedelta(hours=12)
        ),
        device_class=SensorDeviceClass.POWER,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0
    ),
    PVNodeSensorEntityDescription(
        key="power_production_next_24hours",
        translation_key="power_production_next_24hours",
        state=lambda estimate: estimate.power_production_at_time(
            estimate.now() + timedelta(hours=24)
        ),
        device_class=SensorDeviceClass.POWER,
        entity_registry_enabled_default=False,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=0
    ),
    PVNodeSensorEntityDescription(
        key="energy_current_hour",
        translation_key="energy_current_hour",
        state=lambda estimate: estimate.energy_current_hour,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=1,
    ),
    PVNodeSensorEntityDescription(
        key="energy_next_hour",
        translation_key="energy_next_hour",
        state=lambda estimate: estimate.sum_energy_production(1),
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=1,
    ),
    PVNodeSensorEntityDescription(
        key="last_update",
        translation_key="last_update",
        device_class=SensorDeviceClass.TIMESTAMP,
    )
)


WEATHER_SENSORS: tuple[PVNodeSensorEntityDescription, ...] = (
    PVNodeSensorEntityDescription(
        key='weather_precipitation_now',
        name="Precipitation",
        native_unit_of_measurement=UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR,
        device_class=SensorDeviceClass.PRECIPITATION_INTENSITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PVNodeSensorEntityDescription(
        key='weather_humidity_now',
        name="Humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PVNodeSensorEntityDescription(
        key='weather_code_now',
        name="Weather Code",
        state= lambda estimate: CONDITION_MAP.get(estimate.weather_code_now),
    ),
    PVNodeSensorEntityDescription(
        key='weather_wind_speed_now',
        name="Wind speed",
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PVNodeSensorEntityDescription(
        key='weather_temperature_now',
        name="Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    )
)


async def async_setup_entry(hass: HomeAssistant, entry: PVNodeConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback,) -> None:
    """Defer sensor setup to the shared sensor module."""
    coordinator = entry.runtime_data

    sensors = ENERGY_SENSORS
    if entry.options[CONF_WEATHER_ENABLED]:
        sensors = ENERGY_SENSORS + WEATHER_SENSORS

    async_add_entities(
        PVNodeSensorEntity(
            entry_id=entry.entry_id,
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in sensors
    )


class PVNodeSensorEntity(CoordinatorEntity[PVNodeDataUpdateCoordinator], SensorEntity):
    """Defines a PVNode sensor."""

    entity_description: PVNodeSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(self, *, entry_id: str, coordinator: PVNodeDataUpdateCoordinator, entity_description: PVNodeSensorEntityDescription,) -> None:
        """Initialize PVNode sensor."""
        super().__init__(coordinator=coordinator)
        self.entity_description = entity_description
        self.entity_id = f"{SENSOR_DOMAIN}.{entity_description.key}"
        self._attr_unique_id = f"{entry_id}_{entity_description.key}"

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry_id)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name="Solar production forecast",
            configuration_url=URL,
        )

    @property
    def native_value(self) -> datetime | StateType:
        """Return the state of the sensor."""
        if self.entity_description.state is None:
            state: StateType | datetime = getattr(
                self.coordinator.data, self.entity_description.key
            )
        else:
            state = self.entity_description.state(self.coordinator.data)

        return state
