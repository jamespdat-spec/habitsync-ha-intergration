"""The HabitSync integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import HabitSyncApi
from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HabitSync from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    api = HabitSyncApi(entry.data["host"], entry.data["api_key"])
    hass.data[DOMAIN][entry.entry_id] = api

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
