"""Config flow for HabitSync."""
import voluptuous as vol
import logging
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from httpx import HTTPStatusError

from .api import HabitSyncApi
from .const import DOMAIN, SENSOR_TYPES, DEFAULT_SENSOR_TYPES, FEATURES, DEFAULT_FEATURES

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

    @staticmethod
    def async_get_options_flow(entry):
        """Return the config flow for options."""
        return HabitSyncOptionsFlow(entry)


class HabitSyncOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for HabitSync."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle the initial options step."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        _LOGGER = logging.getLogger(__name__)
        try:
            # Ensure defaults are lists for the form
            current_sensors = list(self.config_entry.options.get("sensor_types", list(DEFAULT_SENSOR_TYPES)))
            current_features = list(self.config_entry.options.get("features", list(DEFAULT_FEATURES)))

            schema = vol.Schema(
                {
                    vol.Optional("sensor_types", default=current_sensors): vol.All(cv.ensure_list, [vol.In(list(SENSOR_TYPES.keys()))]),
                    vol.Optional("features", default=current_features): vol.All(cv.ensure_list, [vol.In(list(FEATURES.keys()))]),
                }
            )

            return self.async_show_form(step_id="init", data_schema=schema)
        except Exception as exc:  # pragma: no cover - defensive logging for runtime issues
            _LOGGER.exception("Error building options form: %s", exc)
            return self.async_show_form(step_id="init", data_schema=vol.Schema({}), errors={"base": "unknown"})
