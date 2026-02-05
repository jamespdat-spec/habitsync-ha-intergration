"""Button platform for HabitSync to mark habits done."""
import logging
from homeassistant.components.button import ButtonEntity

from .const import DOMAIN, FEATURE_BUTTONS, DEFAULT_FEATURES

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up HabitSync buttons."""
    # Check if buttons are enabled
    # Safe get for backwards compatibility with entries that don't have options yet
    options = config_entry.options if config_entry.options else {}
    enabled_features = set(options.get("features", list(DEFAULT_FEATURES)))
    if FEATURE_BUTTONS not in enabled_features:
        _LOGGER.debug("Mark Done buttons are disabled")
        return
    
    api = hass.data[DOMAIN][config_entry.entry_id]
    habits = await api.get_habits()
    buttons = []
    for habit in habits:
        buttons.append(HabitDoneButton(api, habit, hass=hass))
    async_add_entities(buttons, True)

class HabitDoneButton(ButtonEntity):
    """Button to mark a habit as done by creating a record via the API."""

    def __init__(self, api, habit, hass=None):
        self.api = api
        self.habit = habit
        self.hass = hass
        self._name = habit.get("name") or habit.get("uuid") or "HabitSync"

    @property
    def name(self):
        return f"{self._name} — Mark Done"

    @property
    def unique_id(self):
        hid = self.habit.get("id") or self.habit.get("uuid") or self.habit.get("habitUuid")
        return f"habitsync_button_{hid}" if hid else None

    async def async_press(self):
        from homeassistant.helpers.entity_registry import async_get as get_entity_registry

        hid = self.habit.get("id") or self.habit.get("uuid") or self.habit.get("habitUuid")
        if not hid:
            _LOGGER.error("Cannot mark habit done: no id for habit %s", self.habit)
            return
        try:
            tz = None
            if hasattr(self, "hass") and self.hass:
                tz = self.hass.config.time_zone
            await self.api.create_record(hid, value=1.0, time_zone=tz)
            _LOGGER.info("Created record for habit %s", hid)

            # Refresh related sensor entities to reflect the new record
            if hasattr(self, "hass") and self.hass:
                entity_registry = get_entity_registry(self.hass)
                # Find and update the sensor for this habit
                for entity in entity_registry.entities.values():
                    if entity.domain == "sensor" and "habitsync" in entity.unique_id and hid in entity.unique_id:
                        self.hass.async_create_task(self.hass.data["entity_components"]["sensor"].async_update_entity(entity.entity_id))
        except Exception as exc:  # pragma: no cover - best-effort API call
            _LOGGER.exception("Failed to create record for habit %s: %s", hid, exc)
