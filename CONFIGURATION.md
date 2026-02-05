# HabitSync Integration Configuration Guide

## Overview

The HabitSync Home Assistant integration is now fully configurable. Users can choose which sensors and features to enable to customize their setup.

## Configuration Flow

### 1. Initial Setup (Config Flow)
- Host: Your HabitSync API server URL
- API Key: Your HabitSync API authentication key

### 2. Options (Customization)

After initial setup, users can customize the integration by:
1. Going to **Settings → Devices & Services**
2. Finding the HabitSync entry
3. Clicking the three-dot menu → **Options**
4. Selecting preferred sensor types and features

## Available Sensor Types

Each habit can have up to 3 sensor types. All are enabled by default.

### Current Value
- **ID**: `sensor_value`
- **Shows**: Today's record value or completion amount
- **Example States**: `1.0`, `5`, `completed`
- **Use When**: You want to see the actual recorded value for a habit

### Completion Percentage
- **ID**: `sensor_percentage`
- **Shows**: Daily completion percentage (0-100%)
- **Example States**: `75.5`, `100`, `0`
- **Use When**: You want to track percentage-based progress

### Completion Status
- **ID**: `sensor_status`
- **Shows**: Detailed completion status
- **Possible Values**:
  - `COMPLETED` - Habit fully completed
  - `MISSED` - Habit was missed
  - `PARTIALLY_COMPLETED` - Partially done
  - `COMPLETED_BY_OTHER_RECORDS` - Completed via other method
  - `FAILED` - Habit failed
  - `DISABLED` - Habit disabled
- **Use When**: You need detailed status information

## Available Features

### Mark Done Buttons
- **ID**: `feature_buttons`
- **Enabled By Default**: Yes
- **What It Does**: Creates a button for each habit to quickly mark it as done
- **Button Names**: `{Habit Name} — Mark Done`
- **When Disabled**: No buttons are created; only sensors appear
- **Why Disable**: If you don't need quick-log functionality or want to reduce clutter

### Medal/Achievement Tracking
- **ID**: `feature_medals`
- **Enabled By Default**: No
- **What It Does**: Tracks and displays medals/achievements (placeholder for future)
- **Status**: Currently shows medal data from API when available
- **Why Enable**: For future integration with medal tracking features

## Configuration Storage

All configuration is stored in Home Assistant's `.storage` directory once the user customizes options. If users never access the options, defaults are used.

## Backwards Compatibility

Entries created before options support are automatically migrated to use defaults when first accessed.

## Automation Examples

### Example 1: Mark Multiple Habits
```yaml
automation:
  - alias: "Morning Routine"
    trigger:
      platform: time
      at: "08:00:00"
    action:
      - service: button.press
        target:
          entity_id:
            - button.morning_stretch_mark_done
            - button.meditation_mark_done
            - button.shower_mark_done
```

### Example 2: Conditional Marking
```yaml
automation:
  - alias: "Mark Exercise if Treadmill Used"
    trigger:
      platform: numeric_state
      entity_id: sensor.fitness_tracker_steps
      above: 10000
    action:
      - service: button.press
        target:
          entity_id: button.exercise_mark_done
      - service: notify.send
        data:
          message: "Exercise habit completed!"
```

### Example 3: Daily Progress Report
```yaml
automation:
  - alias: "Evening Habit Report"
    trigger:
      platform: time
      at: "20:00:00"
    condition:
      - condition: template
        value_template: >
          {{ is_state('sensor.habit1_status', 'COMPLETED') and
             is_state('sensor.habit2_status', 'COMPLETED') }}
    action:
      - service: notify.send
        data:
          message: "All today's habits completed! 🎉"
```

## Sensor Naming

Entities are named based on habit names with a suffix indicating type:

- Value sensor: `sensor.{habit_name}_value`
- Percentage sensor: `sensor.{habit_name}_percentage`
- Status sensor: `sensor.{habit_name}_status`
- Mark Done button: `button.{habit_name}_mark_done`

Example for "Morning Brush" habit:
- `sensor.morning_brush_value`
- `sensor.morning_brush_percentage`
- `sensor.morning_brush_status`
- `button.morning_brush_mark_done`

## Performance Considerations

### API Calls Per Update

With default configuration (all sensors enabled):
- Per habit: 2 API calls per `scan_interval` (typically 60 seconds)
  - 1 call to get record data (for Value and Status sensors)
  - 1 call to get habit details (for Percentage sensor)

### Reducing API Load

To reduce API calls:
1. Disable unused sensor types in Options
2. Increase the `scan_interval` in Home Assistant configuration
3. Disable Mark Done buttons if not needed

### Recommended Minimal Setup

If you only need completion status:
- Enable: `sensor_status` only
- Disable: `sensor_value`, `sensor_percentage`
- Result: 1 API call per habit per interval

## Troubleshooting Configuration

### Options Not Saving

1. Check Home Assistant logs for errors
2. Verify the configuration entry exists
3. Try refreshing the page and trying again

### Expected Sensors Missing

1. Check integration options - they may be disabled
2. Reload the integration via **Developer Tools → YAML → recheck config**
3. Restart Home Assistant

### Performance Issues

1. Check if you're creating too many sensors
2. Try disabling unused sensor types
3. Increase the `scan_interval` value

## Adding New Configuration Options

To add new sensor types or features in the future:

1. Add constant to `const.py`
2. Update `SENSOR_TYPES` or `FEATURES` dict
3. Update `config_flow.py` options
4. Update translations in `en.json`
5. Implement logic in appropriate platform file

