import colorsys
"""Support for KNX/IP lights."""
from enum import Enum

import voluptuous as vol

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    ATTR_WHITE_VALUE,
    PLATFORM_SCHEMA,
    SUPPORT_BRIGHTNESS,
    SUPPORT_COLOR,
    SUPPORT_COLOR_TEMP,
    SUPPORT_WHITE_VALUE,
    LightEntity,
)
from homeassistant.const import CONF_ADDRESS, CONF_NAME
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
import homeassistant.util.color as color_util

from . import (DATA_AVS, Telegram)

CONF_STATE_ADDRESS = "state_address"
CONF_BRIGHTNESS_ADDRESS = "brightness_address"
CONF_BRIGHTNESS_STATE_ADDRESS = "brightness_state_address"
CONF_COLOR_ADDRESS = "color_address"
CONF_COLOR_STATE_ADDRESS = "color_state_address"
CONF_COLOR_TEMP_ADDRESS = "color_temperature_address"
CONF_COLOR_TEMP_STATE_ADDRESS = "color_temperature_state_address"
CONF_COLOR_TEMP_MODE = "color_temperature_mode"
CONF_RGBW_ADDRESS = "rgbw_address"
CONF_HUE_ADDRESS = "hue_address"
CONF_HUE_STATE_ADDRESS = "hue_state_address"
CONF_RGBW_STATE_ADDRESS = "rgbw_state_address"
CONF_WHITE_ADDRESS = "white_address"
CONF_WHITE_STATE_ADDRESS = "white_state_address"
CONF_MIN_KELVIN = "min_kelvin"
CONF_MAX_KELVIN = "max_kelvin"

DEFAULT_NAME = "Avs Light"
DEFAULT_COLOR = (0.0, 0.0)
DEFAULT_BRIGHTNESS = 255
DEFAULT_COLOR_TEMP_MODE = "absolute"
DEFAULT_WHITE_VALUE = 255
DEFAULT_MIN_KELVIN = 2700  # 370 mireds
DEFAULT_MAX_KELVIN = 6000  # 166 mireds


class ColorTempModes(Enum):
    """Color temperature modes for config validation."""

    absolute = "absolute"
    relative = "relative"


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_ADDRESS): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_STATE_ADDRESS): cv.string,
        vol.Optional(CONF_BRIGHTNESS_ADDRESS): cv.string,
        vol.Optional(CONF_BRIGHTNESS_STATE_ADDRESS): cv.string,
        vol.Optional(CONF_COLOR_ADDRESS): cv.string,
        vol.Optional(CONF_COLOR_STATE_ADDRESS): cv.string,
        vol.Optional(CONF_COLOR_TEMP_ADDRESS): cv.string,
        vol.Optional(CONF_COLOR_TEMP_STATE_ADDRESS): cv.string,
        vol.Optional(CONF_COLOR_TEMP_MODE, default=DEFAULT_COLOR_TEMP_MODE): cv.enum(
            ColorTempModes
        ),
        vol.Optional(CONF_RGBW_ADDRESS): cv.string,
        vol.Optional(CONF_RGBW_STATE_ADDRESS): cv.string,
        vol.Optional(CONF_WHITE_ADDRESS): cv.string,
        vol.Optional(CONF_WHITE_STATE_ADDRESS): cv.string,
        vol.Optional(CONF_HUE_ADDRESS): cv.string,
        vol.Optional(CONF_HUE_STATE_ADDRESS): cv.string,
        vol.Optional(CONF_MIN_KELVIN, default=DEFAULT_MIN_KELVIN): vol.All(
            vol.Coerce(int), vol.Range(min=1)
        ),
        vol.Optional(CONF_MAX_KELVIN, default=DEFAULT_MAX_KELVIN): vol.All(
            vol.Coerce(int), vol.Range(min=1)
        ),
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
                "address" : config[CONF_ADDRESS],
                "state_address" : config.get(CONF_STATE_ADDRESS),
                "brightness_address" : config.get(CONF_BRIGHTNESS_ADDRESS),
                "brightness_state_address" : config.get(CONF_BRIGHTNESS_STATE_ADDRESS),
                "color_address" : config.get(CONF_COLOR_ADDRESS),
                "color_state_address" : config.get(CONF_COLOR_STATE_ADDRESS),
                "color_temperature_address" : config.get(CONF_COLOR_TEMP_ADDRESS),
                "color_temperature_state_address" : config.get(CONF_COLOR_TEMP_STATE_ADDRESS),
                "color_temperature_mode" : config.get(CONF_BRIGHTNESS_ADDRESS),
                "rgb_address" : config.get(CONF_RGBW_ADDRESS),
                "rgb_state_address" : config.get(CONF_RGBW_STATE_ADDRESS),
                "white_address" : config.get(CONF_WHITE_ADDRESS),
                "white_state_address" : config.get(CONF_WHITE_STATE_ADDRESS),
                "hue_address" : config.get(CONF_RGBW_ADDRESS),
                "hue_state_address" : config.get(CONF_RGBW_STATE_ADDRESS),
                "min_kelvin" : config.get(CONF_MIN_KELVIN),
                "max_kelvin" : config.get(CONF_MAX_KELVIN),
                "ha_bus_address" : hass.data[DATA_AVS].getHaBusAddr()

            }
   #hass.data[DATA_AVS].xknx.devices.add(light)
    async_add_entities([AVSLight(device, hass)])

    



class AVSLight(LightEntity):

    """Representation of a AVS light."""

    def __init__(self, device, hass):
        """Initialize of AVS light."""
        self.device = device
        self._is_on = False
        self._brightness = 0
        self._color = 0
        self._color_temp = 1
        self._rgb_value = 0
        self._hue_value = 0
        self._saturation_value = 0
        self._white_value = 0

        # print(self.device)
        self.myName = self.device['name']


        if self.device['state_address'] != None:
            hass.bus.async_listen("avs_bus_event/" + self.device['state_address'], self.getEvent) 
        if self.device['brightness_state_address'] != None:
            hass.bus.async_listen("avs_bus_event/" + self.device['brightness_state_address'], self.getEvent) 
        if self.device['color_state_address'] != None:
            hass.bus.async_listen("avs_bus_event/" + self.device['color_state_address'], self.getEvent) 
        if self.device['color_temperature_state_address'] != None:
            hass.bus.async_listen("avs_bus_event/" + self.device['color_temperature_state_address'], self.getEvent) 
        if self.device['rgb_state_address'] != None:
            hass.bus.async_listen("avs_bus_event/" + self.device['rgb_state_address'], self.getEvent) 
        if self.device['white_state_address'] != None:
            hass.bus.async_listen("avs_bus_event/" + self.device['white_state_address'], self.getEvent) 

        self.getStatuses(hass)
        
      
    def getStatuses(self, hass):
        #on/off status
        if self.device['state_address'] != None:
            readState = Telegram()
            readState.initWithData("read", int(self.device['ha_bus_address']), int(self.device['state_address']), 1, 0)
            hass.data[DATA_AVS].sendTelegram(readState)

        if self.device['brightness_state_address'] != None:
            readBrightness = Telegram()
            readBrightness.initWithData("read", int(self.device['ha_bus_address']), int(self.device['brightness_state_address']), 1, 0)
            hass.data[DATA_AVS].sendTelegram(readBrightness)

        if self.device['color_state_address'] != None:
            readColorState = Telegram()
            readColorState.initWithData("read", int(self.device['ha_bus_address']), int(self.device['color_state_address']), 1, 0)
            hass.data[DATA_AVS].sendTelegram(readColorState)

        if self.device['color_temperature_state_address'] != None:
            readColorTempState = Telegram()
            readColorTempState.initWithData("read", int(self.device['ha_bus_address']), int(self.device['color_temperature_state_address']), 2, 0)
            hass.data[DATA_AVS].sendTelegram(readColorTempState)

        if self.device['rgb_state_address'] != None:
            readRgbwState = Telegram()
            readRgbwState.initWithData("read", int(self.device['ha_bus_address']), int(self.device['rgb_state_address']), 7, 0)
            hass.data[DATA_AVS].sendTelegram(readRgbwState)

        if self.device['white_state_address'] != None:
            readRgbwState = Telegram()
            readRgbwState.initWithData("read", int(self.device['ha_bus_address']), int(self.device['white_state_address']), 2, 0)
            hass.data[DATA_AVS].sendTelegram(readRgbwState)
        

    @property
    def name(self):
        """Return the name of the KNX device."""
        return self.myName

    @property
    def available(self):
        """Return True if entity is available."""
        return True

    @property
    def should_poll(self):
        """No polling needed within KNX."""
        return True

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._is_on

    @property   
    def supported_features(self):
        """Flag supported features."""
        flags = 0      
        if self.device['brightness_address'] != None and self.device['brightness_state_address']:
            flags |= SUPPORT_BRIGHTNESS
        if self.device['color_address'] != None and self.device['color_state_address'] != None:
            flags |= SUPPORT_COLOR | SUPPORT_WHITE_VALUE | SUPPORT_BRIGHTNESS
        if self.device['color_temperature_address'] != None and self.device['color_temperature_state_address']:
            flags |= SUPPORT_COLOR_TEMP
        return flags

    @property
    def brightness(self):
        """Return the brightness of this light between 0..255."""
        return self._brightness

    @property
    def hs_color(self):   
        return [self._hue_value, self._saturation_value]

    @property
    def _hsv_color(self):
        return [self._hue_value, self._saturation_value, self.brightness]

    @property
    def white_value(self):
        return self._white_value

    @property
    def color_temp(self):
        return self._color_temp

    @property
    def min_mireds(self):
        return 1

    @property
    def max_mireds(self):
        return 255

    async def async_turn_off(self, **kwargs):
        """Turn the light off."""
        self._is_on = False
        self._brightness = 0

        self.schedule_update_ha_state()

        telegram = Telegram()
        telegram.initWithData("write", int(self.device['ha_bus_address']), int(self.device['address']), 1, 0)
        self.hass.data[DATA_AVS].sendTelegram(telegram)

        # print("Light kwargs: "  + str(kwargs))

    async def async_turn_on(self, **kwargs):
        """Turn the light off."""
        # print(kwargs)
        if kwargs.get(ATTR_BRIGHTNESS) or kwargs.get(ATTR_HS_COLOR):

            if kwargs.get(ATTR_BRIGHTNESS):
                self._brightness = kwargs.get(ATTR_BRIGHTNESS)
            elif kwargs.get(ATTR_HS_COLOR):
                self._hue_value = kwargs.get(ATTR_HS_COLOR)[0]
                self._saturation_value = kwargs.get(ATTR_HS_COLOR)[1]  
            

            if self.device['color_address'] != None and self.device['color_state_address'] != None:
                self.fromHSVToRGBW()
                telegramRGBW = Telegram()
                telegramRGBW.initWithData("write", int(self.device['ha_bus_address']), int(self.device['color_address']), 7, int(self._rgb_value))
                self.hass.data[DATA_AVS].sendTelegram(telegramRGBW)
            elif self.device['brightness_address'] != None and self.device['brightness_state_address']:
                telegramBrightness = Telegram()
                telegramBrightness.initWithData("write", int(self.device['ha_bus_address']), int(self.device['brightness_address']), 2, int(self._brightness))
                self.hass.data[DATA_AVS].sendTelegram(telegramBrightness)

        elif kwargs.get(ATTR_WHITE_VALUE) or kwargs.get(ATTR_WHITE_VALUE) == 0:
            self._white_value = kwargs.get(ATTR_WHITE_VALUE)
            telegramWhite = Telegram()
            telegramWhite.initWithData("write", int(self.device['ha_bus_address']), int(self.device[CONF_WHITE_ADDRESS]), 2, int(self._white_value))
            self.hass.data[DATA_AVS].sendTelegram(telegramWhite)
            # print("self._white_value = " +str(self._white_value))
        elif kwargs.get(ATTR_COLOR_TEMP) != None:
            print("kwargs.get(ATTR_COLOR_TEMP) = " + str(kwargs.get(ATTR_COLOR_TEMP))) 
            self._color_temp = kwargs.get(ATTR_COLOR_TEMP)
            telegramLightTemp = Telegram()
            telegramLightTemp.initWithData("write", int(self.device['ha_bus_address']), int(self.device[CONF_COLOR_TEMP_ADDRESS]), 2, int(self._color_temp))
            self.hass.data[DATA_AVS].sendTelegram(telegramLightTemp)
        else:
            telegramOn = Telegram()
            telegramOn.initWithData("write", int(self.device['ha_bus_address']), int(self.device['address']), 1, 1)
            self.hass.data[DATA_AVS].sendTelegram(telegramOn)
   
        
        self._is_on = True
        self.schedule_update_ha_state()
    

    async def async_added_to_hass(self):
        """Store register state change callback."""
        #print("Light added to hass")

    async def async_update(self):
        """Request a state update from KNX bus."""
        #print("Light update")

    async def getEvent(self, event):

        myEvent = event.as_dict()['data']

        if self.device['state_address'] != None and myEvent['address'] == int(self.device['state_address']) and myEvent['data_type'] == 1:
            if myEvent['data'] == 0:
                self._is_on = False
            else:
                self._is_on = True
        elif self.device['brightness_state_address'] != None and myEvent['address'] == int(self.device['brightness_state_address']) and myEvent['data_type'] == 2:
            self._brightness = myEvent['data']
        elif self.device['color_state_address'] != None and myEvent['address'] == int(self.device['color_state_address']) and myEvent['data_type'] == 7:
            self._rgb_value = myEvent['data']
            self.fromRGBToHSV()
        elif self.device['color_temperature_state_address'] != None and myEvent['address'] == int(self.device['color_temperature_state_address']) and myEvent['data_type'] == 2:
            self._color_temp = myEvent['data']
            # print("color temp = " + str(self._color_temp)) 
        elif self.device['rgb_state_address'] != None and myEvent['address'] == int(self.device['rgb_state_address']) and myEvent['data_type'] == 7:
            self._rgbw_value = myEvent['data']
        elif self.device['white_state_address'] != None and myEvent['address'] == int(self.device['white_state_address']) and myEvent['data_type'] == 2:
            self._white_value = myEvent['data']
        elif self.device['hue_state_address'] != None and myEvent['address'] == int(self.device['hue_state_address']) and myEvent['data_type'] == 2:
            self._hue_value = myEvent['data']

        self.schedule_update_ha_state()
        


    def fromHSVToRGBW(self):  
        r,g,b = colorsys.hsv_to_rgb(int(self._hue_value)/360, int(self._saturation_value)/100, int(self._brightness)/255)
        self._rgb_value = ((0x0000FF & int(r*255))<<16) | ((0x0000FF & int(g*255))<<8) | ((0x0000FF & int(b*255))<<0)

    def fromRGBToHSV(self):
        h,s,v = colorsys.rgb_to_hsv(((0x00FF0000 &self._rgb_value)>>16)/255, ((0x0000FF00 &self._rgb_value)>>8)/255, ((0x000000FF &self._rgb_value)>>0)/255)
        self._hue_value  = int(h*360)
        self._saturation_value = int(s*100)
        self._brightness = int(v*255)
                  





    