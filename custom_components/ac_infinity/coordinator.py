from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=30)


class ACInfinityCoordinator(DataUpdateCoordinator):
    def __init__(
        self,
        hass: HomeAssistant,
        mac: str,
        name: str | None = None,
    ) -> None:
        """Initialize AC Infinity coordinator."""
        self.hass = hass
        self.mac = mac.upper()
        self.name = name or f"AC Infinity {self.mac}"

        # Placeholder state
        self.data = {
            "online": False,
            "ports": {
                1: False,
                2: False,
                3: False,
                4: False,
                5: False,
                6: False,
                7: False,
                8: False,
            },
        }

        super().__init__(
            hass,
            _LOGGER,
            name=self.name,
            update_interval=UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        """Fetch data from the device (stub for now)."""
        _LOGGER.debug("Polling AC Infinity device %s", self.mac)

        # Until BLE read is implemented, just report online
        self.data["online"] = True

        return self.data

    async def async_set_port(self, port: int, state: bool) -> None:
        """Set outlet/port ON or OFF."""
        if port not in self.data["ports"]:
            raise ValueError(f"Invalid port: {port}")

        _LOGGER.debug(
            "Setting AC Infinity %s port %s -> %s",
            self.mac,
            port,
            state,
        )

        # TODO: Insert HunterJM BLE write here
        self.data["ports"][port] = state
        self.async_set_updated_data(self.data)
