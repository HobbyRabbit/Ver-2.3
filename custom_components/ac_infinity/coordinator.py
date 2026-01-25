"""AC Infinity Coordinator."""
from __future__ import annotations

import asyncio
import logging
from typing import Dict

from ac_infinity_ble import ACInfinityController
from bleak.backends.device import BLEDevice

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth.active_update_coordinator import (
    ActiveBluetoothDataUpdateCoordinator,
)
from homeassistant.core import HomeAssistant, CoreState, callback

LOGGER = logging.getLogger(__name__)


class ACInfinityDataUpdateCoordinator(
    ActiveBluetoothDataUpdateCoordinator[Dict]
):
    def __init__(
        self,
        hass: HomeAssistant,
        ble_device: BLEDevice,
        controller: ACInfinityController,
    ) -> None:
        super().__init__(
            hass=hass,
            logger=LOGGER,
            address=ble_device.address,
            needs_poll_method=self._needs_poll,
            poll_method=self._async_update,
            connectable=True,
        )

        self.ble_device = ble_device
        self.controller = controller
        self.data: Dict | None = None

    @callback
    def _needs_poll(self, service_info, seconds_since_last_poll):
        return (
            self.hass.state == CoreState.running
            and (seconds_since_last_poll is None or seconds_since_last_poll > 30)
        )

    async def _async_update(self, service_info):
        await self.controller.update()
        self.data = self.controller.state
        return self.data

    @callback
    def _async_handle_bluetooth_event(self, service_info, change):
        self.ble_device = service_info.device
        self.controller.set_ble_device_and_advertisement_data(
            service_info.device, service_info.advertisement
        )

        if self.controller.state:
            self.data = self.controller.state
            self.async_update_listeners()

        super()._async_handle_bluetooth_event(service_info, change)
