from typing import List, Optional

import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA,SwitchEntity
import homeassistant.helpers.config_validation as cv
from homeassistant.core import callback

from . import DATA_AVS, Telegram
from . import (
AVS_DPT1,
AVS_DPT2,
AVS_DPT3,
AVS_DPT4,
AVS_DPT5,
AVS_DPT6,
AVS_DPT7,
AVS_DPT8,
AVS_DPT9,
AVS_DPT10,
AVS_DPT11
)

CONF_NAME = "name"
CONF_ADDRESS = "address"
CONF_STATE_ADDRESS = "state_address"
CONF_POLL = "poll"

DEFAULT_NAME = "AVS Switch"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_ADDRESS): cv.string,
        vol.Required(CONF_STATE_ADDRESS): cv.string,
        vol.Optional(CONF_POLL, default=False): cv.boolean
    }
)

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up lights for KNX platform."""
    async_add_entities_config(hass, config, async_add_entities)


@callback
def async_add_entities_config(hass, config, async_add_entities):
    """Set up light for KNX platform configured within platform."""
    device = {
                "platform" : hass.data[DATA_AVS],
                "name" : config[CONF_NAME],
                "address" : config.get(CONF_ADDRESS),
                "state_address" : config.get(CONF_STATE_ADDRESS),
                "poll" : config.get(CONF_POLL),

                "ha_bus_address" : hass.data[DATA_AVS].getHaBusAddr()
            }
   #hass.data[DATA_AVS].xknx.devices.add(light)
    async_add_entities([AVSSwitch(device, hass)])

class AVSSwitch(SwitchEntity):

    def __init__(self, device, hass):

        self.device = device

        self._is_on = False
        self._poll = device['poll']
        self.myName = self.device['name']


        if self.device['state_address'] != None:
            hass.bus.async_listen("avs_bus_event/" + self.device['state_address'], self.getEvent) 

        self.getStatuses(hass)

    def getStatuses(self, hass):
    
        #on/off status
        if self.device['state_address'] != None:
            readOnOff = Telegram()
            readOnOff.initWithData("read", int(self.device['ha_bus_address']), int(self.device['state_address']), AVS_DPT1, 0)
            hass.data[DATA_AVS].sendTelegram(readOnOff)

    async def getEvent(self, event):

        myEvent = event.as_dict()['data']

        if self.device['state_address'] != None and myEvent['address'] == int(self.device['state_address']) and myEvent['data_type'] == AVS_DPT1:
            if myEvent['data'] == 0:
                self._is_on = False
            else:
                self._is_on = True

        self.schedule_update_ha_state()

    @property
    def name(self):
        """Return the name of the KNX device."""
        return self.myName

    @property
    def available(self):
        """Return true if entity is available."""
        return True

    @property
    def should_poll(self):
        """Return the polling state. Not needed within KNX."""
        return self._poll

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        sendOn = Telegram()
        sendOn.initWithData("write", int(self.device['ha_bus_address']), int(self.device['address']), AVS_DPT1, int(1))
        self.hass.data[DATA_AVS].sendTelegram(sendOn)

    async def async_turn_off(self, **kwargs):
        sendOff = Telegram()
        sendOff.initWithData("write", int(self.device['ha_bus_address']), int(self.device['address']), AVS_DPT1, int(0))
        self.hass.data[DATA_AVS].sendTelegram(sendOff)

    async def async_toggle(self, **kwargs):
        """Toggle the entity."""
        sendToggle = Telegram()
        if self._is_on == True:
            sendToggle.initWithData("write", int(self.device['ha_bus_address']), int(self.device['address']), AVS_DPT1, int(0))
        else:
            sendToggle.initWithData("write", int(self.device['ha_bus_address']), int(self.device['address']), AVS_DPT1, int(1))
            self.hass.data[DATA_AVS].sendTelegram(sendToggle)