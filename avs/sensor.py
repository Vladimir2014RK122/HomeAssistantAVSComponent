"""Support for AVS sensors."""
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_NAME, CONF_TYPE, TEMP_CELSIUS
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity


from . import DATA_AVS, Telegram

CONF_STATE_ADDRESS = "state_address"
CONF_SYNC_STATE = "sync_state"
DEFAULT_NAME = "AVS Sensor"

CUSTOM_UNITS = "units"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_SYNC_STATE, default=True): cv.boolean,
        vol.Required(CONF_STATE_ADDRESS): cv.string,
        vol.Required(CONF_TYPE): cv.string,
        vol.Required(CUSTOM_UNITS): cv.string,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    async_add_entities_config(hass, config, async_add_entities)

@callback
def async_add_entities_config(hass, config, async_add_entities):
    
    device = {
                "platform" : hass.data[DATA_AVS],
                "name" : config[CONF_NAME],
                "state_address" : config.get(CONF_STATE_ADDRESS),
                "type" : config.get(CONF_TYPE),
                "units" : config.get(CUSTOM_UNITS),
                "ha_bus_address" : hass.data[DATA_AVS].getHaBusAddr()
            }
    async_add_entities([AVSSensor(device, hass)])

class AVSSensor(Entity):
    """Representation of a KNX sensor."""

    def __init__(self, device, hass):
        """Initialize of a KNX sensor."""
        self.device = device
        self._state = 0

        if self.device['state_address'] != None:
            hass.bus.async_listen("avs_bus_event/" + self.device['state_address'], self.getEvent) 

        self.getStatuses(hass)

    def getStatuses(self, hass):
        #on/off status
        if self.device['state_address'] != None:
            readState = Telegram()
            readState.initWithData("read", int(self.device['ha_bus_address']), int(self.device['state_address']), 6, 0)
            hass.data[DATA_AVS].sendTelegram(readState)

    async def getEvent(self, event):

        myEvent = event.as_dict()['data']

        if myEvent['address'] == int(self.device['state_address']):
            self._state = myEvent['data']

        self.schedule_update_ha_state()

    @property
    def name(self):
        return self.device['name']

    @property
    def available(self):
        return True

    @property
    def should_poll(self):
        return False

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self.device['units']

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self.device['type']

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return None