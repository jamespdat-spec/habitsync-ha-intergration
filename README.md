# HabitSync Integration for Home Assistant

A Home Assistant integration for syncing habit data from HabitSync.

## Features

- Track habits from HabitSync in Home Assistant
- Monitor habit completion status as sensors
- Cloud polling for real-time updates
- Configurable sensor types (value, percentage, status)
- Mark Done buttons for quick habit logging
- Real-time sensor refresh after marking habits done

## Installation

### Via HACS (Home Assistant Community Store)

1. Go to HACS in Home Assistant
2. Search for "HabitSync"
3. Install the integration
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/habitsync` directory to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

After installation, add HabitSync to your Home Assistant configuration:

1. Go to Settings → Devices & Services → Create Automation
2. Click "Create Automation" and follow the setup wizard
3. Enter your HabitSync host and API key

### Configuration Options

After setup, you can customize which entities are created by going to:
**Settings → Devices & Services → HabitSync → Options**

#### Sensor Types (Configurable per habit)

- **Current Value** - Shows today's record value or completion amount
- **Completion Percentage** - Shows daily completion percentage (0-100%)
- **Completion Status** - Shows detailed status (COMPLETED, MISSED, PARTIALLY_COMPLETED, etc.)

All three are enabled by default. Disable any you don't need to reduce clutter.

#### Features

- **Mark Done Buttons** - Creates a button for each habit to quickly log completion (enabled by default)
- **Medal/Achievement Tracking** - Tracks medals and achievements (currently placeholder for future expansion)

## Entities Created

For each habit with enabled sensor types, the integration creates:

### Value Sensor
- **Entity ID**: `sensor.{habit_name}_value`
- **State**: Today's record value or completion status
- **Attributes**: Record UUID, epoch day, completion type

### Percentage Sensor
- **Entity ID**: `sensor.{habit_name}_percentage`
- **State**: Daily completion percentage (0-100)
- **Unit of Measurement**: %
- **Attributes**: Current medal, habit UUID

### Status Sensor
- **Entity ID**: `sensor.{habit_name}_status`
- **State**: Completion status
- **Possible Values**: COMPLETED, MISSED, PARTIALLY_COMPLETED, COMPLETED_BY_OTHER_RECORDS, FAILED, DISABLED
- **Attributes**: Record value, epoch day

### Mark Done Button
- **Entity ID**: `button.{habit_name}_mark_done`
- **Action**: Logs a habit completion with value 1.0 for today
- **Automatic Refresh**: Sensors refresh immediately after pressing

## Usage

### In Automations

Mark a habit as done when a specific condition is met:

```yaml
alias: Mark Exercise Done
trigger:
	platform: numeric_state
	entity_id: sensor.treadmill_distance
	above: 5
action:
	service: button.press
	target:
		entity_id: button.exercise_mark_done
```

### In Scripts

Create a script to mark multiple habits at once:

```yaml
script:
	mark_morning_habits:
		sequence:
			- service: button.press
				target:
					entity_id:
						- button.morning_brush_mark_done
						- button.meditation_mark_done
						- button.exercise_mark_done
```

### In Templates

Use habit sensors in templates:

```yaml
template:
	- binary_sensor:
			- name: "All Daily Habits Complete"
				state: "{{ is_state('sensor.habit1_status', 'COMPLETED') and is_state('sensor.habit2_status', 'COMPLETED') }}"
```

## Documentation

For more information, visit the [repository](https://github.com/jamespdat-spec/habitsync-ha-intergration).

## Support

Issues and feature requests: [GitHub Issues](https://github.com/jamespdat-spec/habitsync-ha-intergration/issues)
