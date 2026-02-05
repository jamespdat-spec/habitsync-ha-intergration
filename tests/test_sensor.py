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
    assert s.unique_id == "habitsync_abc"
    assert s.name == "Test Habit"


def test_async_update_get_record():
    """Test async_update calls get_record first."""
    class FakeApi:
        async def get_record(self, habit_id):
            if habit_id == "abc":
                return {"recordValue": 5, "uuid": "abc"}
            raise ValueError("Unknown habit")
        
        async def get_habits(self):
            return [{"id": "abc", "status": "ok"}]

    s = HabitSyncSensor(FakeApi(), {"id": "abc", "name": "n"})
    asyncio.run(s.async_update())
    assert s.state == 5
    assert s.extra_state_attributes is not None
    assert s.extra_state_attributes.get("uuid") == "abc"


def test_async_update_list_shape():
    class FakeApi:
        async def get_record(self, habit_id):
            raise Exception("Record API not available")
        
        async def get_habits(self):
            return [{"id": "abc", "status": "ok"}]

    s = HabitSyncSensor(FakeApi(), {"id": "abc", "name": "n"})
    asyncio.run(s.async_update())
    assert s.state == "ok"


def test_async_update_various_shapes():
    # shape: {'habits': [...]}
    class Api1:
        async def get_record(self, habit_id):
            return {"uuid": "u1", "completion": 5}
        
        async def get_habits(self):
            return {"habits": [{"uuid": "u1", "completion": 5}]}

    s1 = HabitSyncSensor(Api1(), {"uuid": "u1", "name": "n"})
    asyncio.run(s1.async_update())
    assert s1.state == 5

    # shape: {'data': [...]}
    class Api2:
        async def get_record(self, habit_id):
            return {"habitUuid": "h1", "value": 3.2}
        
        async def get_habits(self):
            return {"data": [{"habitUuid": "h1", "value": 3.2}]}

    s2 = HabitSyncSensor(Api2(), {"habitUuid": "h1", "name": "n"})
    asyncio.run(s2.async_update())
    assert s2.state == 3.2

    # single dict
    class Api3:
        async def get_record(self, habit_id):
            return {"id": "x", "status": "s"}
        
        async def get_habits(self):
            return {"id": "x", "status": "s"}

    s3 = HabitSyncSensor(Api3(), {"id": "x", "name": "n"})
    asyncio.run(s3.async_update())
    assert s3.state == "s"
