"""Constants for the HabitSync integration."""

DOMAIN = "habitsync"

# Sensor types
SENSOR_TYPE_VALUE = "sensor_value"
SENSOR_TYPE_PERCENTAGE = "sensor_percentage"
SENSOR_TYPE_STATUS = "sensor_status"

DEFAULT_SENSOR_TYPES = {SENSOR_TYPE_VALUE, SENSOR_TYPE_PERCENTAGE, SENSOR_TYPE_STATUS}

SENSOR_TYPES = {
	SENSOR_TYPE_VALUE: "Current Value",
	SENSOR_TYPE_PERCENTAGE: "Completion Percentage",
	SENSOR_TYPE_STATUS: "Completion Status",
}

# Feature flags
FEATURE_BUTTONS = "feature_buttons"
FEATURE_MEDALS = "feature_medals"

DEFAULT_FEATURES = {FEATURE_BUTTONS}

FEATURES = {
	FEATURE_BUTTONS: "Mark Done Buttons",
	FEATURE_MEDALS: "Medal/Achievement Tracking",
}
