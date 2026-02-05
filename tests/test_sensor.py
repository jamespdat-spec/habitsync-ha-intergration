import sys
import types
import asyncio

# Provide a minimal dummy for homeassistant.helpers.entity.Entity
ha_helpers = types.ModuleType("homeassistant.helpers.entity")
class DummyEntity:
    pass
ha_helpers.Entity = DummyEntity
sys.modules["homeassistant.helpers.entity"] = ha_helpers

import importlib.util
from pathlib import Path

# Load the sensor module directly from its file to avoid package import issues
sensor_path = Path(__file__).parents[1] / "custom_components" / "habitsync" / "sensor.py"
spec = importlib.util.spec_from_file_location("habitsync_sensor", sensor_path)
sensor_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sensor_mod)
HabitSyncSensor = sensor_mod.HabitSyncSensor


def test_unique_id_and_name():
    class FakeApi:
        async def get_habits(self):
            return []

    habit = {"id": "abc", "name": "Test Habit"}
    s = HabitSyncSensor(FakeApi(), habit)
    # Base sensor just checks _get_habit_id, subclasses override unique_id
    assert s._get_habit_id() == "abc"
    
    # Test value sensor names
    v = sensor_mod.HabitSyncValueSensor(FakeApi(), habit)
    assert "Value" in v.name
    assert v.unique_id == "habitsync_value_abc"
    
    # Test percentage sensor names
    p = sensor_mod.HabitSyncPercentageSensor(FakeApi(), habit)
    assert "Percentage" in p.name
    assert p.unique_id == "habitsync_percentage_abc"
    assert p.unit_of_measurement == "%"
    
    # Test status sensor names
    st = sensor_mod.HabitSyncStatusSensor(FakeApi(), habit)
    assert "Status" in st.name
    assert st.unique_id == "habitsync_status_abc"


def test_async_update_get_record():
    """Test async_update calls get_record first for value sensor."""
    class FakeApi:
        async def get_record(self, habit_id):
            if habit_id == "abc":
                return {"recordValue": 5, "uuid": "abc", "completion": "COMPLETED"}
            raise ValueError("Unknown habit")
        
        async def get_habits(self):
            return [{"id": "abc", "status": "ok"}]

    v = sensor_mod.HabitSyncValueSensor(FakeApi(), {"id": "abc", "name": "n"})
    asyncio.run(v.async_update())
    assert v.state == 5
    assert v.extra_state_attributes is not None


def test_percentage_sensor():
    """Test percentage sensor fetches currentPercentage."""
    class FakeApi:
        async def get_habit(self, habit_id):
            if habit_id == "abc":
                return {"currentPercentage": 75.5, "uuid": "abc", "currentMedal": "gold"}
            raise ValueError("Unknown habit")

    p = sensor_mod.HabitSyncPercentageSensor(FakeApi(), {"id": "abc", "name": "n"})
    asyncio.run(p.async_update())
    assert p.state == 75.5
    assert p.extra_state_attributes is not None
    assert p.extra_state_attributes.get("currentMedal") == "gold"


def test_status_sensor():
    """Test status sensor fetches completion status."""
    class FakeApi:
        async def get_record(self, habit_id):
            if habit_id == "abc":
                return {"completion": "COMPLETED", "recordValue": 1.0, "epochDay": 12345}
            raise ValueError("Unknown habit")

    st = sensor_mod.HabitSyncStatusSensor(FakeApi(), {"id": "abc", "name": "n"})
    asyncio.run(st.async_update())
    assert st.state == "COMPLETED"
    assert st.extra_state_attributes is not None
    assert st.extra_state_attributes.get("recordValue") == 1.0


def test_async_update_list_shape():
    """Test value sensor handles list response shape with fallback."""
    class FakeApi:
        async def get_record(self, habit_id):
            raise Exception("Record API not available")
        
        async def get_habits(self):
            return [{"id": "abc", "status": "ok"}]

    v = sensor_mod.HabitSyncValueSensor(FakeApi(), {"id": "abc", "name": "n"})
    asyncio.run(v.async_update())
    assert v.state == "ok"


def test_async_update_various_shapes():
    """Test value sensor handles different API response shapes."""
    # shape: {'habits': [...]}
    class Api1:
        async def get_record(self, habit_id):
            return {"uuid": "u1", "completion": "COMPLETED", "value": 5}
        
        async def get_habits(self):
            return {"habits": [{"uuid": "u1", "completion": 5}]}

    v1 = sensor_mod.HabitSyncValueSensor(Api1(), {"uuid": "u1", "name": "n"})
    asyncio.run(v1.async_update())
    assert v1.state == 5

    # shape: {'data': [...]}
    class Api2:
        async def get_record(self, habit_id):
            return {"habitUuid": "h1", "value": 3.2}
        
        async def get_habits(self):
            return {"data": [{"habitUuid": "h1", "value": 3.2}]}

    v2 = sensor_mod.HabitSyncValueSensor(Api2(), {"habitUuid": "h1", "name": "n"})
    asyncio.run(v2.async_update())
    assert v2.state == 3.2

    # single dict
    class Api3:
        async def get_record(self, habit_id):
            return {"id": "x", "status": "s"}
        
        async def get_habits(self):
            return {"id": "x", "status": "s"}

    v3 = sensor_mod.HabitSyncValueSensor(Api3(), {"id": "x", "name": "n"})
    asyncio.run(v3.async_update())
    assert v3.state == "s"
