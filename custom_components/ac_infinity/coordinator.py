"""AC Infinity BLE coordinator (dynamic GATT discovery, hunterjm style)."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from bleak import BleakClient
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=30)


class ACInfinityCoordinator(DataUpdateCoordinator):
    """Handle BLE connection and commands."""

    def __init__(self, hass, address: str, name: str):
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=UPDATE_INTERVAL,
        )

        self.address = address
        self.client: BleakClient | None = None
        self.write_uuid: str | None = None
        self.notify_uuid: str | None = None
        self._services_printed = False

    # ---------------------------------------------------------
    # CONNECTION
    # ---------------------------------------------------------

    async def _connect(self):
        """Connect to BLE device."""
        if self.client and self.client.is_connected:
            return

        _LOGGER.info("Connecting to AC Infinity %s", self.address)

        self.client = BleakClient(self.address, timeout=20)
        await self.client.connect()

        await self._discover_characteristics()

    async def _disconnect(self):
        if self.client and self.client.is_connected:
            await self.client.disconnect()

    # ---------------------------------------------------------
    # SERVICE DISCOVERY  (IMPORTANT PART)
    # ---------------------------------------------------------

    async def _discover_characteristics(self):
        """Auto find write + notify characteristics."""
        services = await self.client.get_services()

        for service in services:
            for char in service.characteristics:
                props = char.properties

                if not self._services_printed:
                    _LOGGER.debug(
                        "SERVICE %s | CHAR %s | %s",
                        service.uuid,
                        char.uuid,
                        props,
                    )

                if (
                    not self.write_uuid
                    and ("write" in props or "write-without-response" in props)
                ):
                    self.write_uuid = char.uuid

                if not self.notify_uuid and "notify" in props:
                    self.notify_uuid = char.uuid

        self._services_printed = True

        if not self.write_uuid:
            raise RuntimeError("No writable characteristic found")

        _LOGGER.info("Using write UUID: %s", self.write_uuid)
        if self.notify_uuid:
            _LOGGER.info("Using notify UUID: %s", self.notify_uuid)

    # ---------------------------------------------------------
    # PACKET SEND
    # ---------------------------------------------------------

    async def _send(self, payload: bytes):
        """Write raw packet to device."""
        await self._connect()

        _LOGGER.debug("TX → %s", payload.hex())

        await self.client.write_gatt_char(
            self.write_uuid,
            payload,
            response=False,
        )

    # ---------------------------------------------------------
    # SIMPLE CONTROLS (START HERE)
    # ---------------------------------------------------------

    async def async_turn_on(self, port: int = 1):
        """Turn outlet ON."""
        # simple hunterjm style packet template
        packet = bytearray([0xAA, 0x01, port, 0x01])
        await self._send(packet)

    async def async_turn_off(self, port: int = 1):
        """Turn outlet OFF."""
        packet = bytearray([0xAA, 0x01, port, 0x00])
        await self._send(packet)

    async def async_toggle(self, port: int = 1):
        """Toggle outlet."""
        # simple brute test toggle
        packet = bytearray([0xAA, 0x02, port])
        await self._send(packet)

    # ---------------------------------------------------------
    # HA UPDATE LOOP
    # ---------------------------------------------------------

    async def _async_update_data(self):
        """Keep connection alive."""
        await self._connect()
        return {"connected": self.client.is_connected}
