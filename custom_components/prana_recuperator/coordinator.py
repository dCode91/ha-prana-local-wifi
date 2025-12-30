"""DataUpdateCoordinator for Prana Recuperator."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PranaApiClient, PranaApiError, PranaConnectionError, PranaState
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Polling interval - reduced to 15 seconds for better sync with external app
SCAN_INTERVAL = timedelta(seconds=15)

# Delay after making a change before refreshing state (let device process)
POST_COMMAND_DELAY = 0.5

# Maximum retries for commands
MAX_RETRIES = 3
RETRY_DELAY = 1.0


class PranaCoordinator(DataUpdateCoordinator[PranaState]):
    """Prana data update coordinator."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        api: PranaApiClient,
        device_name: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({device_name})",
            update_interval=SCAN_INTERVAL,
        )
        self.api = api
        self.device_name = device_name
        # Lock to prevent concurrent modifications
        self._command_lock = asyncio.Lock()

    async def _async_update_data(self) -> PranaState:
        """Fetch data from API."""
        try:
            return await self.api.get_state()
        except PranaConnectionError as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err
        except PranaApiError as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err

    async def _execute_command_with_retry(
        self,
        command_func,
        *args,
        **kwargs,
    ) -> None:
        """Execute a command with retry logic."""
        last_error = None
        
        for attempt in range(MAX_RETRIES):
            try:
                await command_func(*args, **kwargs)
                return
            except PranaApiError as err:
                last_error = err
                _LOGGER.warning(
                    "Command failed (attempt %d/%d): %s",
                    attempt + 1,
                    MAX_RETRIES,
                    err,
                )
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY)
        
        raise last_error

    async def _refresh_after_command(self) -> None:
        """Refresh data after a command with a small delay."""
        # Wait for device to process the command
        await asyncio.sleep(POST_COMMAND_DELAY)
        # Force a refresh
        await self.async_refresh()

    async def async_set_speed(self, speed: int, fan_type: str) -> None:
        """Set fan speed and refresh data."""
        async with self._command_lock:
            try:
                # Get fresh state first to avoid conflicts
                current_state = await self.api.get_state()
                _LOGGER.debug(
                    "Setting %s speed to %d (current: %s)",
                    fan_type,
                    speed,
                    current_state.raw_data,
                )
                
                # Execute the command with retry
                await self._execute_command_with_retry(
                    self.api.set_speed, speed, fan_type
                )
                
                # Refresh after command
                await self._refresh_after_command()
                
            except PranaApiError as err:
                _LOGGER.error("Failed to set speed: %s", err)
                # Refresh anyway to get current state
                await self.async_refresh()
                raise

    async def async_set_fan_on(self, value: bool, fan_type: str) -> None:
        """Turn fan on/off and refresh data."""
        async with self._command_lock:
            try:
                # Get fresh state first
                current_state = await self.api.get_state()
                _LOGGER.debug(
                    "Setting %s fan to %s (current is_on: %s)",
                    fan_type,
                    value,
                    current_state.is_fan_on(fan_type),
                )
                
                # Execute the command with retry
                await self._execute_command_with_retry(
                    self.api.set_speed_is_on, value, fan_type
                )
                
                # Refresh after command
                await self._refresh_after_command()
                
            except PranaApiError as err:
                _LOGGER.error("Failed to set fan state: %s", err)
                await self.async_refresh()
                raise

    async def async_set_switch(self, switch_type: str, value: bool) -> None:
        """Set switch state and refresh data."""
        async with self._command_lock:
            try:
                # Get fresh state first
                current_state = await self.api.get_state()
                _LOGGER.debug(
                    "Setting switch %s to %s (current state: %s)",
                    switch_type,
                    value,
                    getattr(current_state, switch_type, None),
                )
                
                # Execute the command with retry
                await self._execute_command_with_retry(
                    self.api.set_switch, switch_type, value
                )
                
                # Refresh after command
                await self._refresh_after_command()
                
            except PranaApiError as err:
                _LOGGER.error("Failed to set switch: %s", err)
                await self.async_refresh()
                raise

    async def async_set_brightness(self, brightness: int) -> None:
        """Set brightness and refresh data."""
        async with self._command_lock:
            try:
                # Get fresh state first
                current_state = await self.api.get_state()
                _LOGGER.debug(
                    "Setting brightness to %d (current: %d)",
                    brightness,
                    current_state.brightness,
                )
                
                # Execute the command with retry
                await self._execute_command_with_retry(
                    self.api.set_brightness, brightness
                )
                
                # Refresh after command
                await self._refresh_after_command()
                
            except PranaApiError as err:
                _LOGGER.error("Failed to set brightness: %s", err)
                await self.async_refresh()
                raise

    async def async_force_refresh(self) -> None:
        """Force an immediate refresh of the data."""
        async with self._command_lock:
            await self.async_refresh()
