"""Sensor platform for HabitSync."""
import logging
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, SENSOR_TYPE_VALUE, SENSOR_TYPE_PERCENTAGE, SENSOR_TYPE_STATUS, DEFAULT_SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the HabitSync sensor."""
    api = hass.data[DOMAIN][config_entry.entry_id]
    habits = await api.get_habits()
    _LOGGER.info("Habits: %s", habits)
    
    # Get configured sensor types
    # Safe get for backwards compatibility with entries that don't have options yet
    options = config_entry.options if config_entry.options else {}
    enabled_types = set(options.get("sensor_types", list(DEFAULT_SENSOR_TYPES)))
    
    sensors = []
    for habit in habits:
        # Create sensors based on enabled types
        if SENSOR_TYPE_VALUE in enabled_types:
            sensors.append(HabitSyncValueSensor(api, habit))
        if SENSOR_TYPE_PERCENTAGE in enabled_types:
            sensors.append(HabitSyncPercentageSensor(api, habit))
        if SENSOR_TYPE_STATUS in enabled_types:
            sensors.append(HabitSyncStatusSensor(api, habit))
    
    async_add_entities(sensors, True)

class HabitSyncSensor(Entity):
    """Base class for HabitSync sensors."""

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
        if hid is not None:
            return f"habitsync_{hid}"
        # fallback to a stable name-based id
        name = (self.habit.get("name") or "habitsync_habit").lower().replace(" ", "_")
        return f"habitsync_{name}"

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
        """Fetch new state data for the sensor. Override in subclasses."""
        pass


class HabitSyncValueSensor(HabitSyncSensor):
    """Sensor showing the current record value/status."""

    def __init__(self, api, habit):
        """Initialize the sensor."""
        super().__init__(api, habit)
        self._attributes = {}

    @property
    def unique_id(self):
        """Return a unique ID."""
        hid = self._get_habit_id()
        if hid is not None:
            return f"habitsync_value_{hid}"
        name = (self.habit.get("name") or "habitsync_habit").lower().replace(" ", "_")
        return f"habitsync_value_{name}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.habit.get('name') or self._get_habit_id() or 'HabitSync'} Value"

    async def async_update(self):
        """Fetch new state data for the sensor."""
        target_id = self._get_habit_id()
        if not target_id:
            _LOGGER.warning("Cannot update sensor: no habit ID found")
            return

        # Fetch today's record for this specific habit
        try:
            tz = None
            if hasattr(self, "hass") and self.hass:
                tz = self.hass.config.time_zone
            record = await self.api.get_record(target_id, time_zone=tz)
            _LOGGER.debug("Record for habit %s: %s", target_id, record)
            # Extract state from record
            self._state = (
                record.get("status")
                or record.get("completion")
                or record.get("value")
                or record.get("recordValue")
            )
            # Set attributes from the record
            self._attributes = {
                k: v for k, v in record.items() if k in ("uuid", "habitUuid", "epochDay", "completion", "status", "recordValue", "value")
            }
            return
        except Exception as exc:
            _LOGGER.debug("Failed to fetch record for habit %s: %s", target_id, exc)

        # Fallback: fetch all habits and find matching one
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

        for habit in habits:
            hid = (
                habit.get("id")
                or habit.get("uuid")
                or habit.get("habitUuid")
                or habit.get("habit_uuid")
            )
            if hid is not None and target_id is not None and hid == target_id:
                _LOGGER.info("Habit: %s", habit)
                self._state = (
                    habit.get("status")
                    or habit.get("completion")
                    or habit.get("value")
                    or habit.get("recordValue")
                )
                self._attributes = {
                    k: v for k, v in habit.items() if k in ("uuid", "habitUuid", "epochDay", "completion", "status", "recordValue")
                }
                break

    @property
    def extra_state_attributes(self):
        """Return the state attributes for the sensor."""
        return getattr(self, "_attributes", {}) or None


class HabitSyncPercentageSensor(HabitSyncSensor):
    """Sensor showing the current completion percentage."""

    def __init__(self, api, habit):
        """Initialize the sensor."""
        super().__init__(api, habit)
        self._attributes = {}

    @property
    def unique_id(self):
        """Return a unique ID."""
        hid = self._get_habit_id()
        if hid is not None:
            return f"habitsync_percentage_{hid}"
        name = (self.habit.get("name") or "habitsync_habit").lower().replace(" ", "_")
        return f"habitsync_percentage_{name}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.habit.get('name') or self._get_habit_id() or 'HabitSync'} Percentage"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return "%"

    async def async_update(self):
        """Fetch the completion percentage for this habit."""
        target_id = self._get_habit_id()
        if not target_id:
            _LOGGER.warning("Cannot update percentage sensor: no habit ID found")
            return

        try:
            habit_detail = await self.api.get_habit(target_id)
            _LOGGER.debug("Habit detail for %s: %s", target_id, habit_detail)
            self._state = habit_detail.get("currentPercentage")
            self._attributes = {k: v for k, v in habit_detail.items() if k in ("currentMedal", "uuid", "habitUuid")}
        except Exception as exc:
            _LOGGER.debug("Failed to fetch habit details for %s: %s", target_id, exc)
            self._state = None

    @property
    def extra_state_attributes(self):
        """Return the state attributes for the sensor."""
        return getattr(self, "_attributes", {}) or None


class HabitSyncStatusSensor(HabitSyncSensor):
    """Sensor showing the completion status (COMPLETED, MISSED, etc.)."""

    def __init__(self, api, habit):
        """Initialize the sensor."""
        super().__init__(api, habit)
        self._attributes = {}

    @property
    def unique_id(self):
        """Return a unique ID."""
        hid = self._get_habit_id()
        if hid is not None:
            return f"habitsync_status_{hid}"
        name = (self.habit.get("name") or "habitsync_habit").lower().replace(" ", "_")
        return f"habitsync_status_{name}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.habit.get('name') or self._get_habit_id() or 'HabitSync'} Status"

    async def async_update(self):
        """Fetch the completion status for today's record."""
        target_id = self._get_habit_id()
        if not target_id:
            _LOGGER.warning("Cannot update status sensor: no habit ID found")
            return

        try:
            tz = None
            if hasattr(self, "hass") and self.hass:
                tz = self.hass.config.time_zone
            record = await self.api.get_record(target_id, time_zone=tz)
            _LOGGER.debug("Record status for %s: %s", target_id, record)
            self._state = record.get("completion")
            self._attributes = {k: v for k, v in record.items() if k in ("recordValue", "epochDay", "uuid")}
        except Exception as exc:
            _LOGGER.debug("Failed to fetch record status for %s: %s", target_id, exc)

    @property
    def extra_state_attributes(self):
        """Return the state attributes for the sensor."""
        return getattr(self, "_attributes", {}) or None
