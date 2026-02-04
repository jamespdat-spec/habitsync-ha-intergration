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

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"habitsync_{self.habit['id']}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.habit["name"]

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
        habits = await self.api.get_habits()
        for habit in habits:
            if habit["id"] == self.habit["id"]:
                _LOGGER.info("Habit: %s", habit)
                self._state = habit["status"]
                break
