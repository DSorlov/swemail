import logging
from datetime import datetime
from typing import Any, Dict, Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DEVICE_AUTHOR,
    DEVICE_NAME,
    DEVICE_VERSION,
    DOMAIN,
    SENSOR_ATTRIB,
    SENSOR_NAME,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Swedish Mail sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []

    # Add provider-specific sensors for enabled providers
    for provider in coordinator.providers:
        entities.append(ProviderMailDeliverySensor(coordinator, provider))

    # Add combined next delivery sensor if multiple providers are enabled
    if len(coordinator.providers) > 1:
        entities.append(NextMailDeliverySensor(coordinator))

    async_add_entities(entities)


class ProviderMailDeliverySensor(CoordinatorEntity, SensorEntity):
    """Mail delivery sensor for a specific provider."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTime.DAYS
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_icon = "mdi:email-fast-outline"
    _attr_translation_key = "maildaysleft"

    def __init__(self, coordinator, provider: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._provider = provider
        self._attr_unique_id = f"{DOMAIN}_{coordinator.postal_code}_{provider}"
        self._attr_name = (
            f"{provider.capitalize()} {SENSOR_NAME} {coordinator.postal_code}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{DEVICE_NAME}_{coordinator.postal_code}")},
            name=f"{DEVICE_NAME} {coordinator.postal_code}",
            manufacturer=DEVICE_AUTHOR,
            model=f"v{DEVICE_VERSION}",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> Optional[int]:
        """Return the native value of the sensor."""
        if not self.coordinator.data or self._provider not in self.coordinator.data:
            return None

        provider_data = self.coordinator.data[self._provider]
        if self.coordinator.postal_code not in provider_data:
            return None

        try:
            next_delivery = provider_data[self.coordinator.postal_code]["next_delivery"]
            if not next_delivery:
                return None

            next_date = datetime.strptime(next_delivery, "%Y-%m-%d")
            num_days = (next_date - datetime.now()).days + 1

            # Handle edge case around midnight
            return max(0, num_days)
        except (ValueError, KeyError):
            return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        attributes = {
            "provider": self._provider,
            "postal_code": self.coordinator.postal_code,
            "logo": f"/local/swemail/{self._provider}.png",
        }

        if not self.coordinator.data or self._provider not in self.coordinator.data:
            attributes.update(
                {
                    "last_update": "",
                    "postal_city": "",
                    "next_delivery": "",
                    "days_left": "",
                }
            )
            return attributes

        provider_data = self.coordinator.data[self._provider]
        postal_data = provider_data.get(self.coordinator.postal_code, {})

        attributes.update(
            {
                "last_update": postal_data.get("last_update", ""),
                "postal_city": postal_data.get("postal_city", ""),
                "next_delivery": postal_data.get("next_delivery", ""),
                "days_left": self.native_value or "",
            }
        )

        return attributes

    @property
    def attribution(self) -> str:
        """Return the attribution."""
        return SENSOR_ATTRIB

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.native_value is not None


class NextMailDeliverySensor(CoordinatorEntity, SensorEntity):
    """Combined mail delivery sensor showing next delivery from all providers."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTime.DAYS
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_icon = "mdi:email-fast-outline"
    _attr_translation_key = "maildaysleft"

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{coordinator.postal_code}"
        self._attr_name = f"Mail {SENSOR_NAME} {coordinator.postal_code}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{DEVICE_NAME}_{coordinator.postal_code}")},
            name=f"{DEVICE_NAME} {coordinator.postal_code}",
            manufacturer=DEVICE_AUTHOR,
            model=f"v{DEVICE_VERSION}",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> Optional[int]:
        """Return the native value (days until next delivery)."""
        if not self.coordinator.data:
            return None

        best_date = None
        best_days = None

        for provider in self.coordinator.providers:
            if provider not in self.coordinator.data:
                continue

            provider_data = self.coordinator.data[provider]
            if self.coordinator.postal_code not in provider_data:
                continue

            try:
                next_delivery = provider_data[self.coordinator.postal_code][
                    "next_delivery"
                ]
                if not next_delivery:
                    continue

                next_date = datetime.strptime(next_delivery, "%Y-%m-%d")
                num_days = max(0, (next_date - datetime.now()).days + 1)

                if best_date is None or next_date < best_date:
                    best_date = next_date
                    best_days = num_days

            except (ValueError, KeyError):
                continue

        return best_days

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        attributes = {
            "all_providers": ",".join(self.coordinator.providers),
            "postal_code": self.coordinator.postal_code,
        }

        if not self.coordinator.data:
            return attributes

        best_date = None
        best_provider = None

        # Add individual provider data
        for provider in self.coordinator.providers:
            prefix = f"{provider}_"

            if provider not in self.coordinator.data:
                attributes.update(
                    {
                        f"{prefix}last_update": "",
                        f"{prefix}postal_city": "",
                        f"{prefix}next_delivery": "",
                        f"{prefix}days_left": "",
                        f"{prefix}logo": f"/local/swemail/{provider}.png",
                    }
                )
                continue

            provider_data = self.coordinator.data[provider]
            postal_data = provider_data.get(self.coordinator.postal_code, {})

            try:
                next_delivery = postal_data.get("next_delivery", "")
                if next_delivery:
                    next_date = datetime.strptime(next_delivery, "%Y-%m-%d")
                    num_days = max(0, (next_date - datetime.now()).days + 1)

                    if best_date is None or next_date < best_date:
                        best_date = next_date
                        best_provider = provider

                    attributes.update(
                        {
                            f"{prefix}last_update": postal_data.get("last_update", ""),
                            f"{prefix}postal_city": postal_data.get("postal_city", ""),
                            f"{prefix}next_delivery": next_delivery,
                            f"{prefix}days_left": num_days,
                            f"{prefix}logo": f"/local/swemail/{provider}.png",
                        }
                    )
                else:
                    attributes.update(
                        {
                            f"{prefix}last_update": "",
                            f"{prefix}postal_city": "",
                            f"{prefix}next_delivery": "",
                            f"{prefix}days_left": "",
                            f"{prefix}logo": f"/local/swemail/{provider}.png",
                        }
                    )
            except (ValueError, KeyError):
                attributes.update(
                    {
                        f"{prefix}last_update": "",
                        f"{prefix}postal_city": "",
                        f"{prefix}next_delivery": "",
                        f"{prefix}days_left": "",
                        f"{prefix}logo": f"/local/swemail/{provider}.png",
                    }
                )

        # Add next delivery info (best/earliest)
        if best_provider:
            attributes.update(
                {
                    "next_provider": best_provider.capitalize(),
                    "next_logo": f"/local/swemail/{best_provider}.png",
                    "next_delivery": attributes[f"{best_provider}_next_delivery"],
                    "next_days_left": attributes[f"{best_provider}_days_left"],
                }
            )
        else:
            attributes.update(
                {
                    "next_provider": "",
                    "next_logo": "",
                    "next_delivery": "",
                    "next_days_left": "",
                }
            )

        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def attribution(self) -> str:
        """Return the attribution."""
        return SENSOR_ATTRIB
