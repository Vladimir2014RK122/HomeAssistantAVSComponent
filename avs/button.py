from typing import List, Optional

import voluptuous as vol

from homeassistant.components.button import PLATFORM_SCHEMA, ButtonEntity
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

CONF_NAME = "name"  # name
CONF_ADDRESS = "address"  # avs address
CONF_DPT = "dpt"  # DPT
CONF_DATA = "data"  # data for sending of pressing


DEFAULT_NAME = "AVS Button"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_ADDRESS): cv.string,
        vol.Required(CONF_DPT): cv.positive_int,
        vol.Optional(CONF_DATA): cv.string,
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
        CONF_DPT: config.get(CONF_DPT),
        CONF_DATA: config.get(CONF_DATA),
    }
    async_add_entities([AVSButton(device, hass)])


class AVSButton(ButtonEntity):
    def __init__(self, device, hass):

        self.device = device
        self.attr_name = self.device[CONF_NAME]

    def press(self) -> None:
        value = self.device[CONF_DATA]
        if value is None:
            return None

        dpt = self.device[CONF_DPT]
        if dpt == AVS_DPT6:
            value = float(value)
        else:
            value = int(value)

        if self.device[CONF_ADDRESS] is not None:
            press_telegram = Telegram()
            press_telegram.initWithData(
                "write",
                int(self.device["ha_bus_address"]),
                int(self.device[CONF_ADDRESS]),
                dpt,
                value,
            )
            self.hass.data[DATA_AVS].sendTelegram(press_telegram)
        return None

    @property
    def name(self):
        return self.attr_name
