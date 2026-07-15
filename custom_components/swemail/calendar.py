"""Calendar platform for Swedish Mail Delivery."""

from datetime import date, datetime, timedelta
from typing import Optional

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
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
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the calendar platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([MailDeliveryCalendar(coordinator)])


class MailDeliveryCalendar(CoordinatorEntity, CalendarEntity):
    """Calendar exposing upcoming mail delivery days as all-day events."""

    _attr_icon = "mdi:calendar-clock"

    def __init__(self, coordinator):
        """Initialize the calendar."""
        super().__init__(coordinator)
        postal_code = coordinator.postal_code
        self._attr_unique_id = f"{DOMAIN}_{postal_code}_calendar"
        self._attr_name = f"Mail Delivery Calendar {postal_code}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{DEVICE_NAME}_{postal_code}")},
            name=f"{DEVICE_NAME} {postal_code}",
            manufacturer=DEVICE_AUTHOR,
            model=f"v{DEVICE_VERSION}",
            entry_type=DeviceEntryType.SERVICE,
        )

    def _all_events(self) -> list[CalendarEvent]:
        """Build the list of known delivery events from coordinator data."""
        data = self.coordinator.data or {}
        events: dict[tuple, CalendarEvent] = {}

        for provider in self.coordinator.providers:
            postal_data = data.get(provider, {}).get(self.coordinator.postal_code, {})
            city = postal_data.get("postal_city") or ""

            for field in ("next_delivery", "upcoming_delivery"):
                value = postal_data.get(field)
                if not value:
                    continue
                try:
                    day = datetime.strptime(value, "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    continue

                summary = f"{provider.capitalize()} utdelning"
                events[(summary, day)] = CalendarEvent(
                    start=day,
                    end=day + timedelta(days=1),
                    summary=summary,
                    description=f"{city} {self.coordinator.postal_code}".strip(),
                )

        return sorted(events.values(), key=lambda event: event.start)

    @property
    def event(self) -> Optional[CalendarEvent]:
        """Return the next upcoming delivery event."""
        today = date.today()
        for calendar_event in self._all_events():
            if calendar_event.end > today:
                return calendar_event
        return None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return delivery events within the requested range."""
        start = start_date.date() if isinstance(start_date, datetime) else start_date
        end = end_date.date() if isinstance(end_date, datetime) else end_date
        return [
            calendar_event
            for calendar_event in self._all_events()
            if calendar_event.start < end and calendar_event.end > start
        ]

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success
