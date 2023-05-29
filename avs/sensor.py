"""Support for AVS sensors."""
import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
    SensorDeviceClass,
)
from homeassistant.const import CONF_NAME, CONF_TYPE, TEMP_CELSIUS
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

# from homeassistant.helpers.entity import Entity


from . import DATA_AVS, Telegram

CONF_STATE_ADDRESS = "state_address"
CONF_DPT = "dpt"
CONF_SYNC_STATE = "sync_state"
CONF_UNITS = "units"


DEFAULT_NAME = "AVS Sensor"


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_SYNC_STATE, default=True): cv.boolean,
        vol.Required(CONF_STATE_ADDRESS): cv.positive_int,
        vol.Required(CONF_DPT): cv.positive_int,
        vol.Optional(CONF_TYPE): cv.string,
        vol.Optional(CONF_UNITS, default=TEMP_CELSIUS): cv.string,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities_config(hass, config, async_add_entities)


@callback
def async_add_entities_config(hass, config, async_add_entities):

    device = {
        "platform": hass.data[DATA_AVS],
        "ha_bus_address": hass.data[DATA_AVS].getHaBusAddr(),
        CONF_NAME: config[CONF_NAME],
        CONF_STATE_ADDRESS: config.get(CONF_STATE_ADDRESS),
        CONF_DPT: config.get(CONF_DPT),
        CONF_TYPE: config.get(CONF_TYPE),
        CONF_UNITS: config.get(CONF_UNITS),
    }
    async_add_entities([AVSSensor(device, hass)])


class AVSSensor(SensorEntity):
    """Representation of a KNX sensor."""

    def __init__(self, device, hass):
        """Initialize of a KNX sensor."""
        self.device = device
        self._state = 0
        self._dpt = self.device[CONF_DPT]

        if self.device[CONF_STATE_ADDRESS] != None:
            hass.bus.async_listen(
                "avs_bus_event/" + str(self.device[CONF_STATE_ADDRESS]), self.getEvent
            )

        self.getStatuses(hass)

    def getStatuses(self, hass):
        if self.device[CONF_STATE_ADDRESS] is not None:
            read_state = Telegram()
            read_state.initWithData(
                "read",
                int(self.device["ha_bus_address"]),
                int(self.device[CONF_STATE_ADDRESS]),
                self._dpt,
                0,
            )
            hass.data[DATA_AVS].sendTelegram(read_state)

    async def getEvent(self, event):

        myEvent = event.as_dict()["data"]

        if myEvent["address"] == self.device[CONF_STATE_ADDRESS]:
            self._state = myEvent["data"]
            if self._dpt == 6:
                self._state = round(self._state, 2)

        self.schedule_update_ha_state()

    @property
    def name(self):
        return self.device["name"]

    @property
    def available(self):
        return True

    @property
    def should_poll(self):
        return False

    @property
    def native_value(self):
        return self._state

    @property
    def native_unit_of_measurement(self):
        return self.device[CONF_UNITS]

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self.device[CONF_TYPE]

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return None

    @property
    def native_precision(self):
        return 2
