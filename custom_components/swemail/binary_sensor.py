"""Binary sensor platform for Swedish Mail Delivery."""

from datetime import date, timedelta
from typing import Optional

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
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
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities: list[BinarySensorEntity] = []

    # Combined "any provider" sensors for today and tomorrow.
    entities.append(MailDeliveryBinarySensor(coordinator, None, 0, "delivery_today"))
    entities.append(
        MailDeliveryBinarySensor(coordinator, None, 1, "delivery_tomorrow")
    )

    # Per-provider "delivery today" sensors.
    for provider in coordinator.providers:
        entities.append(
            MailDeliveryBinarySensor(coordinator, provider, 0, "delivery_today")
        )

    async_add_entities(entities)


class MailDeliveryBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor that is on when mail is delivered on a given day."""

    _attr_icon = "mdi:mailbox"

    def __init__(self, coordinator, provider: Optional[str], days_offset: int, key: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._provider = provider
        self._days_offset = days_offset

        postal_code = coordinator.postal_code
        if provider is None:
            self._attr_unique_id = f"{DOMAIN}_{postal_code}_{key}"
            self._attr_name = f"Mail {key.replace('_', ' ').title()} {postal_code}"
        else:
            self._attr_unique_id = f"{DOMAIN}_{postal_code}_{provider}_{key}"
            self._attr_name = (
                f"{provider.capitalize()} "
                f"{key.replace('_', ' ').title()} {postal_code}"
            )

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{DEVICE_NAME}_{postal_code}")},
            name=f"{DEVICE_NAME} {postal_code}",
            manufacturer=DEVICE_AUTHOR,
            model=f"v{DEVICE_VERSION}",
            entry_type=DeviceEntryType.SERVICE,
        )

    def _delivers_on(self, provider: str, target: str) -> bool:
        """Return True if the provider delivers on the target ISO date."""
        if not self.coordinator.data or provider not in self.coordinator.data:
            return False
        provider_data = self.coordinator.data[provider]
        postal_data = provider_data.get(self.coordinator.postal_code, {})
        return postal_data.get("next_delivery") == target

    @property
    def is_on(self) -> bool:
        """Return true if mail is delivered on the configured day."""
        target = (date.today() + timedelta(days=self._days_offset)).isoformat()

        if self._provider is not None:
            return self._delivers_on(self._provider, target)

        return any(
            self._delivers_on(provider, target)
            for provider in self.coordinator.providers
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def attribution(self) -> str:
        """Return the attribution."""
        return SENSOR_ATTRIB
