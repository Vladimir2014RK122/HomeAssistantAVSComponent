from typing import List, Optional

import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
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
    AVS_DPT11,
)

CONF_NAME = "name"
CONF_ADDRESS = "address"
CONF_STATE_ADDRESS = "state_address"
CONF_DPT = "dpt"
CONF_DATA_0 = "data_0"
CONF_DATA_1 = "data_1"
CONF_POLL = "poll"

DEFAULT_NAME = "AVS Switch"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_ADDRESS): cv.string,
        vol.Required(CONF_STATE_ADDRESS): cv.string,
        vol.Required(CONF_DPT): cv.positive_int,
        vol.Required(CONF_DATA_0): cv.string,
        vol.Required(CONF_DATA_1): cv.string,
        vol.Optional(CONF_POLL, default=False): cv.boolean,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up lights for KNX platform."""
    async_add_entities_config(hass, config, async_add_entities)


@callback
def async_add_entities_config(hass, config, async_add_entities):
    """Set up light for KNX platform configured within platform."""
    device = {
        "platform": hass.data[DATA_AVS],
        "ha_bus_address": hass.data[DATA_AVS].getHaBusAddr(),
        CONF_NAME: config[CONF_NAME],
        CONF_ADDRESS: config.get(CONF_ADDRESS),
        CONF_STATE_ADDRESS: config.get(CONF_STATE_ADDRESS),
        CONF_DPT: config.get(CONF_DPT),
        CONF_DATA_0: config.get(CONF_DATA_0),
        CONF_DATA_1: config.get(CONF_DATA_1),
        CONF_POLL: config.get(CONF_POLL),
    }
    # hass.data[DATA_AVS].xknx.devices.add(light)
    async_add_entities([AVSSwitch(device, hass)])


class AVSSwitch(SwitchEntity):
    def __init__(self, device, hass):

        self.device = device

        self._state = 0
        self._poll = device["poll"]
        self._name = self.device["name"]

        if self.device[CONF_STATE_ADDRESS] != None:
            hass.bus.async_listen(
                "avs_bus_event/" + self.device[CONF_STATE_ADDRESS], self.getEvent
            )

        self.getStatuses(hass)

    def getStatuses(self, hass):

        # on/off status
        if self.device[CONF_STATE_ADDRESS] != None:
            dpt = self.device[CONF_DPT]
            readOnOff = Telegram()
            readOnOff.initWithData(
                "read",
                int(self.device["ha_bus_address"]),
                int(self.device[CONF_STATE_ADDRESS]),
                dpt,
                0,
            )
            hass.data[DATA_AVS].sendTelegram(readOnOff)

    async def getEvent(self, event):

        myEvent = event.as_dict()["data"]

        if self.device[CONF_STATE_ADDRESS] != None and myEvent["address"] == int(
            self.device[CONF_STATE_ADDRESS]
        ):
            dpt = self.device[CONF_DPT]
            if myEvent["data_type"] == self.device[CONF_DPT]:

                data0 = 0
                if dpt == 6:
                    data0 = float(self.device[CONF_DATA_0])
                else:
                    data0 = int(self.device[CONF_DATA_0])

                if myEvent["data"] == data0:
                    self._state = 0
                else:
                    self._state = 1

        self.schedule_update_ha_state()

    @property
    def name(self):
        """Return the name of the KNX device."""
        return self._name

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
        if self._state == 0:
            return False
        else:
            return True

    async def async_turn_on(self, **kwargs):

        self._state = 1
        dpt = self.device[CONF_DPT]
        data1 = 0
        if dpt == 6:
            data1 = float(self.device[CONF_DATA_1])
        else:
            data1 = int(self.device[CONF_DATA_1])
        sendOn = Telegram()
        sendOn.initWithData(
            "write",
            int(self.device["ha_bus_address"]),
            int(self.device[CONF_ADDRESS]),
            dpt,
            data1,
        )
        self.hass.data[DATA_AVS].sendTelegram(sendOn)

    async def async_turn_off(self, **kwargs):

        self._state = 0
        dpt = self.device[CONF_DPT]
        data0 = 0
        if dpt == 6:
            data0 = float(self.device[CONF_DATA_0])
        else:
            data0 = int(self.device[CONF_DATA_0])
        sendOff = Telegram()
        sendOff.initWithData(
            "write",
            int(self.device["ha_bus_address"]),
            int(self.device[CONF_ADDRESS]),
            dpt,
            data0,
        )
        self.hass.data[DATA_AVS].sendTelegram(sendOff)

    async def async_toggle(self, **kwargs):
        """Toggle the entity."""
        dpt = self.device[CONF_DPT]
        data0 = 0
        data1 = 0
        if dpt == 6:
            data0 = float(self.device[CONF_DATA_0])
            data1 = float(self.device[CONF_DATA_1])
        else:
            data0 = int(self.device[CONF_DATA_0])
            data1 = int(self.device[CONF_DATA_1])

        sendToggle = Telegram()
        if self._state == 1:
            sendToggle.initWithData(
                "write",
                int(self.device["ha_bus_address"]),
                int(self.device[CONF_ADDRESS]),
                dpt,
                data0,
            )
        else:
            sendToggle.initWithData(
                "write",
                int(self.device["ha_bus_address"]),
                int(self.device[CONF_ADDRESS]),
                dpt,
                data1,
            )
            self.hass.data[DATA_AVS].sendTelegram(sendToggle)
