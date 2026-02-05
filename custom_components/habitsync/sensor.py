"""Sensor platform for HabitSync."""
import logging
from homeassistant.helpers.entity import Entity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the HabitSync sensor."""
    api = hass.data[DOMAIN][config_entry.entry_id]
    habits = await api.get_habits()
    _LOGGER.info("Habits: %s", habits)
    sensors = [HabitSyncSensor(api, habit) for habit in habits]
    async_add_entities(sensors, True)

class HabitSyncSensor(Entity):
    """Representation of a HabitSync sensor."""

    def __init__(self, api, habit):
        """Initialize the sensor."""
        self.api = api
        self.habit = habit
        self._state = None

    def _get_habit_id(self, habit=None):
        """Return the habit identifier using common fallback keys."""
        h = habit or self.habit or {}
        return (
            h.get("id")
            or h.get("uuid")
            or h.get("habitUuid")
            or h.get("habit_uuid")
            or h.get("uuidString")
            or None
        )

    @property
    def unique_id(self):
        """Return a unique ID."""
        hid = self._get_habit_id()
        return f"habitsync_{hid}" if hid is not None else None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.habit.get("name") or self._get_habit_id() or "HabitSync"

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, "habitsync")},
            "name": "HabitSync",
            "manufacturer": "jofoerster",
        }

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        """Fetch new state data for the sensor."""
        # TODO: This is not ideal, as it will fetch all habits again.
        # The API should have an endpoint to get a single habit.
        raw = await self.api.get_habits()

        # Normalize different API response shapes into a list of habit dicts
        if isinstance(raw, dict):
            if "habits" in raw and isinstance(raw["habits"], list):
                habits = raw["habits"]
            elif "data" in raw and isinstance(raw["data"], list):
                habits = raw["data"]
            elif all(isinstance(v, dict) for v in raw.values()):
                habits = list(raw.values())
            else:
                habits = [raw]
        else:
            habits = raw

        target_id = self._get_habit_id()
        for habit in habits:
            hid = (
                habit.get("id")
                or habit.get("uuid")
                or habit.get("habitUuid")
                or habit.get("habit_uuid")
            )
            if hid is not None and target_id is not None and hid == target_id:
                _LOGGER.info("Habit: %s", habit)
                # Prefer common status/completion keys
                self._state = (
                    habit.get("status")
                    or habit.get("completion")
                    or habit.get("value")
                    or habit.get("recordValue")
                )
                break
