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

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
