"""Config flow for HabitSync."""
import voluptuous as vol
from homeassistant import config_entries
from httpx import HTTPStatusError

from .api import HabitSyncApi
from .const import DOMAIN

class HabitSyncConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HabitSync."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                api = HabitSyncApi(user_input["host"], user_input["api_key"])
                await api.get_habits()
                return self.async_create_entry(title="HabitSync", data=user_input)
            except HTTPStatusError:
                errors["base"] = "auth"
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("host"): str,
                    vol.Required("api_key"): str,
                }
            ),
            errors=errors,
        )
