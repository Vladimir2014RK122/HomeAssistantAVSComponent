from typing import List, Optional

import voluptuous as vol

from homeassistant.components.cover import (
    PLATFORM_SCHEMA,
    CoverEntity,
    CoverDeviceClass,
    CoverEntityFeature,
    ATTR_POSITION,
    ATTR_CURRENT_POSITION,
)
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
CONF_ADDR_OPEN = "addr_open"  # dpt1
CONF_ADDR_CLOSE = "addr_close"  # dpt1
CONF_ADDR_STOP = "addr_stop"  # dpt1
CONF_ADDR_POSITION = "addr_set_position"  # dpt2 0-255
CONF_ADDR_STATUS = "addr_status"  # dpt2 0-255
CONF_OPEN_VALUE = "open_val"  # 0/1
CONF_CLOSE_VALUE = "close_val"  # 0/1
CONF_STOP_VALUE = "stop_val"  # 0/1
CONF_DEVICE_CLASS = (
    "device_class"  # awning/blind/curtain/danper/door/garage/gate/shade/shutter/window
)


DEFAULT_NAME = "AVS Cover"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_DEVICE_CLASS): cv.string,
        vol.Required(CONF_ADDR_OPEN): cv.positive_int,
        vol.Required(CONF_ADDR_CLOSE): cv.positive_int,
        vol.Required(CONF_ADDR_STOP): cv.positive_int,
        vol.Required(CONF_OPEN_VALUE): cv.positive_int,
        vol.Required(CONF_CLOSE_VALUE): cv.positive_int,
        vol.Required(CONF_STOP_VALUE): cv.positive_int,
        vol.Optional(CONF_ADDR_POSITION): cv.positive_int,
        vol.Optional(CONF_ADDR_STATUS): cv.positive_int,
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
        CONF_DEVICE_CLASS: config.get(CONF_DEVICE_CLASS),
        CONF_ADDR_OPEN: config.get(CONF_ADDR_OPEN),
        CONF_ADDR_CLOSE: config.get(CONF_ADDR_CLOSE),
        CONF_ADDR_STOP: config.get(CONF_ADDR_STOP),
        CONF_OPEN_VALUE: config.get(CONF_OPEN_VALUE),
        CONF_CLOSE_VALUE: config.get(CONF_CLOSE_VALUE),
        CONF_STOP_VALUE: config.get(CONF_STOP_VALUE),
        CONF_ADDR_POSITION: config.get(CONF_ADDR_POSITION),
        CONF_ADDR_STATUS: config.get(CONF_ADDR_STATUS),
    }
    async_add_entities([AVSCover(device, hass)])


class AVSCover(CoverEntity):
    def __init__(self, device, hass):

        self.device = device
        self.attr_name = self.device[CONF_NAME]
        self._position = 0

        self.getStatuses(hass)

    def getStatuses(self, hass):
        if self.device[CONF_ADDR_STATUS] is not None:
            read_state = Telegram()
            read_state.initWithData(
                "read",
                int(self.device["ha_bus_address"]),
                int(self.device[CONF_ADDR_STATUS]),
                AVS_DPT2,
                0,
            )
            hass.data[DATA_AVS].sendTelegram(read_state)

    async def getEvent(self, event):

        myEvent = event.as_dict()["data"]

        if myEvent["address"] == self.device[CONF_ADDR_STATUS]:
            self._position = int((myEvent["data"] / 255.0) * 100)

        self.schedule_update_ha_state()

    @property
    def name(self):
        return self.attr_name

    @property
    def is_closed(self):
        if self.device[CONF_ADDR_STATUS] is not None:
            if self._position == 255:
                return True
            elif self._position == 0:
                return False
            else:
                return None
        else:
            return None

    @property
    def current_cover_position(self):
        if self.device[CONF_ADDR_STATUS] is not None:
            return self._position
        else:
            return None

    @property
    def device_class(self):
        dev_class = self.device[CONF_DEVICE_CLASS]

        if dev_class is CoverDeviceClass.AWNING:
            return CoverDeviceClass.AWNING
        elif dev_class is CoverDeviceClass.BLIND:
            return CoverDeviceClass.BLIND
        elif dev_class is CoverDeviceClass.CURTAIN:
            return CoverDeviceClass.CURTAIN
        elif dev_class is CoverDeviceClass.DAMPER:
            return CoverDeviceClass.DAMPER
        elif dev_class is CoverDeviceClass.DOOR:
            return CoverDeviceClass.DOOR
        elif dev_class is CoverDeviceClass.GARAGE:
            return CoverDeviceClass.GARAGE
        elif dev_class is CoverDeviceClass.GATE:
            return CoverDeviceClass.GATE
        elif dev_class is CoverDeviceClass.SHADE:
            return CoverDeviceClass.SHADE
        elif dev_class is CoverDeviceClass.SHUTTER:
            return CoverDeviceClass.SHUTTER
        elif dev_class is CoverDeviceClass.WINDOW:
            return CoverDeviceClass.WINDOW
        else:
            return None

    @property
    def supported_features(self):

        features = (
            CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
        )

        if self.device[CONF_ADDR_POSITION] is not None:
            features |= CoverEntityFeature.SET_POSITION

        return features

    async def async_open_cover(self, **kwargs):
        open_telegram = Telegram()
        open_telegram.initWithData(
            "write",
            int(self.device["ha_bus_address"]),
            int(self.device[CONF_ADDR_OPEN]),
            AVS_DPT1,
            self.device[CONF_OPEN_VALUE],
        )
        self.hass.data[DATA_AVS].sendTelegram(open_telegram)

    async def async_close_cover(self, **kwargs):
        close_telegram = Telegram()
        close_telegram.initWithData(
            "write",
            int(self.device["ha_bus_address"]),
            int(self.device[CONF_ADDR_CLOSE]),
            AVS_DPT1,
            self.device[CONF_CLOSE_VALUE],
        )
        self.hass.data[DATA_AVS].sendTelegram(close_telegram)

    async def async_stop_cover(self, **kwargs):
        stop_telegram = Telegram()
        stop_telegram.initWithData(
            "write",
            int(self.device["ha_bus_address"]),
            int(self.device[CONF_ADDR_STOP]),
            AVS_DPT1,
            self.device[CONF_STOP_VALUE],
        )
        self.hass.data[DATA_AVS].sendTelegram(stop_telegram)

    async def async_set_cover_position(self, **kwargs):
        print(kwargs)
        position_telegram = Telegram()
        position_telegram.initWithData(
            "write",
            int(self.device["ha_bus_address"]),
            int(self.device[CONF_ADDR_POSITION]),
            AVS_DPT2,
            int((kwargs.get(ATTR_POSITION) / 100.0) * 255),
        )
        self.hass.data[DATA_AVS].sendTelegram(position_telegram)

        self._position = kwargs.get(ATTR_POSITION)

    async def async_open_cover_tilt(self, **kwargs):
        """Open the cover tilt."""

    async def async_close_cover_tilt(self, **kwargs):
        """Close the cover tilt."""

    async def async_stop_cover_tilt(self, **kwargs):
        """Stop the cover."""

    async def async_set_cover_tilt_position(self, **kwargs):
        """Move the cover tilt to a specific position."""
