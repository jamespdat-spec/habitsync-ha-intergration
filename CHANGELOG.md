# Version 0.1.0 - Full Feature Configuration Release

## Summary

The HabitSync Home Assistant integration now features full user configuration for sensors and features. Users can customize which sensor types and features are enabled through the Home Assistant options interface.

## New Features

### 1. Options Flow
- Users can now customize the integration after setup
- Accessible via: Settings → Devices & Services → HabitSync → Options
- No restart required for option changes to take effect

### 2. Configurable Sensor Types
Three sensor types per habit, all enabled by default:
- **Current Value** (`sensor_value`) - Shows today's record value
- **Completion Percentage** (`sensor_percentage`) - Shows daily percentage (0-100%)
- **Completion Status** (`sensor_status`) - Shows detailed status (COMPLETED, MISSED, etc.)

### 3. Configurable Features
- **Mark Done Buttons** (`feature_buttons`) - Default enabled, creates quick-log buttons
- **Medal/Achievement Tracking** (`feature_medals`) - Placeholder for future expansion

### 4. Enhanced Documentation
- New `CONFIGURATION.md` with detailed configuration guide
- Updated `README.md` with sensor documentation and usage examples
- Translation strings for options flow

## Architecture Changes

### Files Modified

#### `const.py`
- Added sensor type constants: `SENSOR_TYPE_VALUE`, `SENSOR_TYPE_PERCENTAGE`, `SENSOR_TYPE_STATUS`
- Added feature constants: `FEATURE_BUTTONS`, `FEATURE_MEDALS`
- Added `DEFAULT_SENSOR_TYPES` and `DEFAULT_FEATURES` sets
- Added human-readable `SENSOR_TYPES` and `FEATURES` dicts

#### `config_flow.py`
- Added `HabitSyncOptionsFlow` class for configuring sensor types and features
- Added `async_get_options_flow()` callback
- Added validation and multi-select UI for options

#### `sensor.py`
- Modified `async_setup_entry()` to respect configured sensor types
- Added safe fallback for `config_entry.options` (backwards compatibility)

#### `button.py`
- Modified `async_setup_entry()` to only create buttons if feature is enabled
- Added safe fallback for `config_entry.options` (backwards compatibility)

#### `manifest.json`
- Added `"options_flow": true` to enable options interface
- Maintains existing `icon` reference

#### `translations/en.json`
- Added options flow translations
- Added descriptions for configuration options

### Files Created

- `CONFIGURATION.md` - Comprehensive configuration guide with examples
- Already updated: `README.md` - Enhanced with sensor documentation

## Backwards Compatibility

- Existing config entries without options continue to work with defaults
- All three sensor types enabled by default (no behavior change for existing users)
- All features enabled by default except Medal tracking

## User Benefits

1. **Reduced UI Clutter** - Disable unused sensor types
2. **Customizable Features** - Enable/disable buttons and future features
3. **Better Documentation** - Clear guidance on sensor types and configuration
4. **Future Extensibility** - Easy to add new sensor types or features
5. **Performance Control** - Users can reduce API calls by disabling sensors

## Testing

Updated `tests/test_sensor.py`:
- Tests for all three sensor types
- Tests for percentage sensor with `get_habit()` API call
- Tests for status sensor with `get_record()` API call
- Tests for fallback behavior when record API fails

Run tests:
```bash
pytest -q tests/test_sensor.py
```

## Migration Guide for Users

### Existing Installations

1. After update, integration continues to work with all sensors enabled (no change)
2. To customize:
   - Go to Settings → Devices & Services
   - Find HabitSync entry
   - Click menu → Options
   - Select/deselect sensor types and features
   - Save

### First-Time Installations

1. Set up integration with host and API key
2. Options window appears automatically
3. Select desired sensor types (all enabled by default)
4. Select desired features (Mark Done Buttons enabled by default)
5. Save and integration is fully configured

## Future Extensibility

The configuration framework supports adding:
- New sensor types (e.g., streak, total completion, historical data)
- New features (e.g., medal tracking, challenge integration, sharing)
- Per-habit customization (advanced feature)
- Custom polling intervals
- Notification settings

## Performance Impact

### API Call Reduction Examples

**Default (all sensors)**: 2 API calls per habit per interval
- `GET /api/record/{uuid}/simple` (for Value + Status)
- `GET /api/habit/{uuid}` (for Percentage)

**Minimal (status only)**: 1 API call per habit per interval
- `GET /api/record/{uuid}/simple`

**Custom**: Depends on enabled sensors
- Value only: 1 call
- Percentage only: 1 call
- Status only: 1 call
- Value + Percentage: 2 calls
- Value + Status: 1 call (they share the same endpoint)
- Percentage + Status: 2 calls
- All three: 2 calls

## Next Steps

Potential future features suggested by this architecture:
1. Per-habit customization layers
2. Automation triggers based on habit status
3. Monthly/weekly historical data visualization
4. Challenge and streak integration
5. Multi-user/family habit sharing
6. Custom notification rules
7. Advanced filtering and grouping

