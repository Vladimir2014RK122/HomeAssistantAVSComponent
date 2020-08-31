from typing import List, Optional

import voluptuous as vol

from homeassistant.components.climate import PLATFORM_SCHEMA, ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    PRESET_AWAY,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_SLEEP,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_TARGET_HUMIDITY,
    SUPPORT_AUX_HEAT
)
from homeassistant.const import ATTR_TEMPERATURE, CONF_NAME, TEMP_CELSIUS
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

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
CONF_THERMOSTAT_MODE = "thermostat_mode"
CONF_ON_OFF_ADDRESS = "on_off"
CONF_ON_OFF_STATUS_ADDRESS = "on_off_status"
CONF_MEASURED_TEMPERATURE_STATUS_ADDRESS = "measured_temperature_status"
CONF_SETPOINT_ADDRESS = "setpoint_temperature"
CONF_SETPOINT_STATUS_ADDRESS = "setpoint_temperature_status"
CONF_OPERATION_MODE_ADDRESS = "operation_mode"
CONF_OPERATION_MODE_STATUS_ADDRESS = "operation_mode_status"
CONF_HEAT_VALUE_STATUS_ADDRESS = "heat_value_status"
CONF_COOL_VALUE_STATUS_ADDRESS = "cool_value_status"
CONF_HEAT_COOL_STATUS_ADDRESS = "heat_cool_status"
CONF_ERROR_STATUS_ADDRESS = "error_status"
CONF_SETPOINT_STEP = "setpoint_step"
CONF_MIN_TEMP = "setpoint_min_temp"
CONF_MAX_TEMP = "setpoint_max_temp"
CONF_USE_HUMIDITY = "use_humidity"
CONF_USE_AUX_HEAT = "use_aux_heat"
CONF_MEASURED_HUMIDITY_STATUS_ADDRESS = "measured_humidity_status"
CONF_SETPOINT_HUMIDITY_ADDRESS = "setpoint_humidity"
CONF_SETPOINT_HUMIDITY_STATUS_ADDRESS = "setpoint_humidity_status"
CONF_AUX_HEAT_ADDRESS = "aux_heat"
CONF_AUX_HEAT_STATUS_ADDRESS = "aux_heat_status"
CONF_POLL = "poll"



DEFAULT_NAME = "AVS Climate"
DEFAULT_THERMOSTAT_MODE_HEAT = "heat"
DEFAULT_THERMOSTAT_MODE_COOL = "cool"
DEFAULT_THERMOSTAT_MODE_HEAT_COOL = "heat_and_cool"
DEFAULT_NAME = "AVS Climate"
DEFAULT_SETPOINT_STEP = 0.5
DEFAULT_MAX_TEMP = 55
DEFAULT_MIN_TEMP = 7
DEFAULT_POLL_PERIOD = 60

OPERATION_MODES = {

    "Auto": HVAC_MODE_AUTO,
    "Heat": HVAC_MODE_HEAT,
    "Cool": HVAC_MODE_COOL,
    "Off": HVAC_MODE_OFF,
    "Fan only": HVAC_MODE_FAN_ONLY,
    "Dry": HVAC_MODE_DRY,
}

OPERATION_MODES_INV = dict(reversed(item) for item in OPERATION_MODES.items())

PRESET_MODES = {
    "Frost Protection": PRESET_ECO,
    "Night": PRESET_SLEEP,
    "Standby": PRESET_AWAY,
    "Comfort": PRESET_COMFORT,
}


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_THERMOSTAT_MODE, default=DEFAULT_THERMOSTAT_MODE_HEAT): cv.string,
        vol.Optional(CONF_ON_OFF_ADDRESS): cv.string,
        vol.Optional(CONF_ON_OFF_STATUS_ADDRESS): cv.string,
        vol.Required(CONF_MEASURED_TEMPERATURE_STATUS_ADDRESS): cv.string,
        vol.Required(CONF_SETPOINT_ADDRESS): cv.string,
        vol.Required(CONF_SETPOINT_STATUS_ADDRESS): cv.string,
        vol.Optional(CONF_OPERATION_MODE_ADDRESS): cv.string,
        vol.Optional(CONF_OPERATION_MODE_STATUS_ADDRESS): cv.string,
        vol.Optional(CONF_HEAT_VALUE_STATUS_ADDRESS): cv.string,
        vol.Optional(CONF_COOL_VALUE_STATUS_ADDRESS): cv.string,
        vol.Optional(CONF_HEAT_COOL_STATUS_ADDRESS): cv.string,
        vol.Optional(CONF_ERROR_STATUS_ADDRESS): cv.string,

        vol.Optional(CONF_SETPOINT_STEP, default=DEFAULT_SETPOINT_STEP): vol.All(float, vol.Range(min=0, max=2)),
        vol.Optional(CONF_MIN_TEMP, default=DEFAULT_MIN_TEMP): vol.All(float, vol.Range(min=-100, max=100)),
        vol.Optional(CONF_MAX_TEMP, default=DEFAULT_MAX_TEMP): vol.All(float, vol.Range(min=-100, max=100)),

        vol.Optional(CONF_USE_HUMIDITY, default=False): cv.boolean,
        vol.Optional(CONF_USE_AUX_HEAT, default=False): cv.boolean,
        vol.Optional(CONF_MEASURED_HUMIDITY_STATUS_ADDRESS): cv.string,
        vol.Optional(CONF_SETPOINT_HUMIDITY_ADDRESS): cv.string,
        vol.Optional(CONF_SETPOINT_HUMIDITY_STATUS_ADDRESS): cv.string,
        vol.Optional(CONF_AUX_HEAT_ADDRESS): cv.string,
        vol.Optional(CONF_AUX_HEAT_STATUS_ADDRESS): cv.string,
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
                "thermostat_mode" : config.get(CONF_THERMOSTAT_MODE),
                "on_off" : config.get(CONF_ON_OFF_ADDRESS),
                "on_off_status" : config.get(CONF_ON_OFF_STATUS_ADDRESS),
                "measured_temperature_status" : config.get(CONF_MEASURED_TEMPERATURE_STATUS_ADDRESS),
                "setpoint_temperature" : config.get(CONF_SETPOINT_ADDRESS),
                "setpoint_temperature_status" : config.get(CONF_SETPOINT_STATUS_ADDRESS),
                "operation_mode" : config.get(CONF_OPERATION_MODE_ADDRESS),
                "operation_mode_status" : config.get(CONF_OPERATION_MODE_STATUS_ADDRESS),
                "heat_value_status" : config.get(CONF_HEAT_VALUE_STATUS_ADDRESS),
                "cool_value_status" : config.get(CONF_COOL_VALUE_STATUS_ADDRESS),
                "heat_cool_status" : config.get(CONF_HEAT_COOL_STATUS_ADDRESS),
                "error_status" : config.get(CONF_ERROR_STATUS_ADDRESS),
                "setpoint_step" : config.get(CONF_SETPOINT_STEP),
                "setpoint_max_temp" : config.get(CONF_MAX_TEMP),
                "setpoint_min_temp" : config.get(CONF_MIN_TEMP),

                "use_humidity" : config.get(CONF_USE_HUMIDITY),
                "use_aux_heat" : config.get(CONF_USE_AUX_HEAT),
                "measured_humidity_status" : config.get(CONF_MEASURED_HUMIDITY_STATUS_ADDRESS),
                "setpoint_humidity" : config.get(CONF_SETPOINT_HUMIDITY_ADDRESS),
                "setpoint_humidity_status" : config.get(CONF_SETPOINT_HUMIDITY_STATUS_ADDRESS),
                "aux_heat" : config.get(CONF_AUX_HEAT_ADDRESS),
                "aux_heat_status" : config.get(CONF_AUX_HEAT_STATUS_ADDRESS),
                "poll" : config.get(CONF_POLL),

                "ha_bus_address" : hass.data[DATA_AVS].getHaBusAddr()
            }
   #hass.data[DATA_AVS].xknx.devices.add(light)
    async_add_entities([AVSClimate(device, hass)])

class AVSClimate(ClimateEntity):

    """Representation of a AVS light."""

    def __init__(self, device, hass):

        """Initialize of AVS light."""
        self.device = device
        self._is_on = True
        self._measured_temperature = -127.0
        self._setpoint_temperature = device['setpoint_min_temp']
        self._operation_mode = 0
        self._heat_value = 0
        self._cool_value = 0
        self._heat_cool_status = 0
        self._error_status = 0
        self._setpoint_step = device['setpoint_step']
        self._setpoint_max = device['setpoint_max_temp']
        self._setpoint_min = device['setpoint_min_temp']
        self._unit_of_measurement = TEMP_CELSIUS

        self._use_humidity = device['use_humidity']
        self._use_aux_heat = device['use_aux_heat']
        self._measured_humidity = 0
        self._setpoint_humidity = 0
        self.is_aux_heat_on = False
        self._poll = device['poll']
        # self.hass = 
        
        # print(self.device)
        self.myName = self.device['name']


        if self.device['on_off_status'] != None:
            hass.bus.async_listen("avs_bus_event/" + self.device['on_off_status'], self.getEvent) 
        if self.device['measured_temperature_status'] != None:
            hass.bus.async_listen("avs_bus_event/" + self.device['measured_temperature_status'], self.getEvent) 
        if self.device['setpoint_temperature_status'] != None:
            hass.bus.async_listen("avs_bus_event/" + self.device['setpoint_temperature_status'], self.getEvent) 
        if self.device['operation_mode_status'] != None:
            hass.bus.async_listen("avs_bus_event/" + self.device['operation_mode_status'], self.getEvent) 
        if self.device['heat_value_status'] != None:
            hass.bus.async_listen("avs_bus_event/" + self.device['heat_value_status'], self.getEvent) 
        if self.device['cool_value_status'] != None:
            hass.bus.async_listen("avs_bus_event/" + self.device['cool_value_status'], self.getEvent) 
        if self.device['heat_cool_status'] != None:
            hass.bus.async_listen("avs_bus_event/" + self.device['heat_cool_status'], self.getEvent) 
        if self.device['error_status'] != None:
            hass.bus.async_listen("avs_bus_event/" + self.device['error_status'], self.getEvent) 

        if self._use_humidity == True:
            if self.device['measured_humidity_status'] != None:
                hass.bus.async_listen("avs_bus_event/" + self.device['measured_humidity_status'], self.getEvent) 
            if self.device['setpoint_humidity_status'] != None:
                hass.bus.async_listen("avs_bus_event/" + self.device['setpoint_humidity_status'], self.getEvent) 
        
        if self._use_aux_heat == True:
            if self.device['aux_heat_status'] != None:
                hass.bus.async_listen("avs_bus_event/" + self.device['aux_heat_status'], self.getEvent) 

        self.getStatuses(hass)
    
    def getStatuses(self, hass):
    
        #on/off status
        if self.device['on_off_status'] != None:
            readOnOff = Telegram()
            readOnOff.initWithData("read", int(self.device['ha_bus_address']), int(self.device['on_off_status']), AVS_DPT1, 0)
            hass.data[DATA_AVS].sendTelegram(readOnOff)

        if self.device['measured_temperature_status'] != None:
            readMeasuredTemp = Telegram()
            readMeasuredTemp.initWithData("read", int(self.device['ha_bus_address']), int(self.device['measured_temperature_status']), AVS_DPT6, 0)
            hass.data[DATA_AVS].sendTelegram(readMeasuredTemp)

        if self.device['setpoint_temperature_status'] != None:
            readSetpoint = Telegram()
            readSetpoint.initWithData("read", int(self.device['ha_bus_address']), int(self.device['setpoint_temperature_status']), AVS_DPT6, 0)
            hass.data[DATA_AVS].sendTelegram(readSetpoint)

        if self.device['operation_mode_status'] != None:
            readOperationMode = Telegram()
            readOperationMode.initWithData("read", int(self.device['ha_bus_address']), int(self.device['operation_mode_status']), AVS_DPT2, 0)
            hass.data[DATA_AVS].sendTelegram(readOperationMode)

        if self.device['heat_value_status'] != None:
            readHeatValue = Telegram()
            readHeatValue.initWithData("read", int(self.device['ha_bus_address']), int(self.device['heat_value_status']), AVS_DPT2, 0)
            hass.data[DATA_AVS].sendTelegram(readHeatValue)

        if self.device['cool_value_status'] != None:
            readCoolValue = Telegram()
            readCoolValue.initWithData("read", int(self.device['ha_bus_address']), int(self.device['cool_value_status']), AVS_DPT2, 0)
            hass.data[DATA_AVS].sendTelegram(readCoolValue)
        
        if self.device['heat_cool_status'] != None:
            readHeatCoolStatus = Telegram()
            readHeatCoolStatus.initWithData("read", int(self.device['ha_bus_address']), int(self.device['heat_cool_status']), AVS_DPT2, 0)
            hass.data[DATA_AVS].sendTelegram(readHeatCoolStatus)
        
        if self.device['error_status'] != None:
            readErrorStatus = Telegram()
            readErrorStatus.initWithData("read", int(self.device['ha_bus_address']), int(self.device['error_status']), AVS_DPT1, 0)
            hass.data[DATA_AVS].sendTelegram(readErrorStatus)

        if self._use_humidity == True:

            if self.device['measured_humidity_status'] != None:
                readMeasuredHumidity = Telegram()
                readMeasuredHumidity.initWithData("read", int(self.device['ha_bus_address']), int(self.device['measured_humidity_status']), AVS_DPT2, 0)
                hass.data[DATA_AVS].sendTelegram(readMeasuredHumidity)

            if self.device['setpoint_humidity_status'] != None:
                readSetpointHumidity = Telegram()
                readSetpointHumidity.initWithData("read", int(self.device['ha_bus_address']), int(self.device['setpoint_humidity_status']), AVS_DPT2, 0)
                hass.data[DATA_AVS].sendTelegram(readSetpointHumidity)
        
        if self._use_aux_heat == True:
            if self.device['aux_heat_status'] != None:
                readAuxHeatStatus = Telegram()
                readAuxHeatStatus.initWithData("read", int(self.device['ha_bus_address']), int(self.device['aux_heat_status']), AVS_DPT1, 0)
                hass.data[DATA_AVS].sendTelegram(readAuxHeatStatus)


    async def getEvent(self, event):

        myEvent = event.as_dict()['data']

        if self.device['on_off_status'] != None and myEvent['address'] == int(self.device['on_off_status']) and myEvent['data_type'] == AVS_DPT1:
            if myEvent['data'] == 0:
                self._is_on = False
            else:
                self._is_on = True
        elif self.device['measured_temperature_status'] != None and myEvent['address'] == int(self.device['measured_temperature_status']) and myEvent['data_type'] == AVS_DPT6:
            self._measured_temperature = myEvent['data']
        elif self.device['setpoint_temperature_status'] != None and myEvent['address'] == int(self.device['setpoint_temperature_status']) and myEvent['data_type'] == AVS_DPT6:
            self._setpoint_temperature = myEvent['data']
        elif self.device['operation_mode_status'] != None and myEvent['address'] == int(self.device['operation_mode_status']) and myEvent['data_type'] == AVS_DPT2:
            self._operation_mode = myEvent['data']
        elif self.device['heat_value_status'] != None and myEvent['address'] == int(self.device['heat_value_status']) and myEvent['data_type'] == AVS_DPT2:
            self._heat_value = myEvent['data']
        elif self.device['cool_value_status'] != None and myEvent['address'] == int(self.device['cool_value_status']) and myEvent['data_type'] == AVS_DPT2:
            self._cool_value = myEvent['data']
        elif self.device['heat_cool_status'] != None and myEvent['address'] == int(self.device['heat_cool_status']) and myEvent['data_type'] == AVS_DPT2:
            self._heat_cool_status = myEvent['data']
        elif self.device['error_status'] != None and myEvent['address'] == int(self.device['error_status']) and myEvent['data_type'] == AVS_DPT1:
            self._error_status = myEvent['data']
        elif self.device['measured_humidity_status'] != None and myEvent['address'] == int(self.device['measured_humidity_status']) and myEvent['data_type'] == AVS_DPT2:
            self._measured_humidity = myEvent['data']
        elif self.device['setpoint_humidity_status'] != None and myEvent['address'] == int(self.device['setpoint_humidity_status']) and myEvent['data_type'] == AVS_DPT2:
            self._setpoint_humidity = myEvent['data']
        elif self.device['aux_heat_status'] != None and myEvent['address'] == int(self.device['aux_heat_status']) and myEvent['data_type'] == AVS_DPT1:
            if myEvent['data'] == 0:
                self.is_aux_heat_on = False
            else:
                self.is_aux_heat_on = True

        self.schedule_update_ha_state()



    @property
    def supported_features(self):
        """Return the list of supported features."""
        #   print("SUPPORT_TARGET_TEMPERATURE = " + str(SUPPORT_TARGET_TEMPERATURE))
        result = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE

        if self.device['use_humidity'] != None:
            result |= SUPPORT_TARGET_HUMIDITY
        if self.device['use_aux_heat'] != None:
            result |= SUPPORT_AUX_HEAT
        return result

    @property
    def name(self):
        """Return the name of the KNX device."""
        return self.myName

    @property
    def available(self):
        """Return True if entity is available."""
        return True

    def update(self):
        """Update unit attributes."""
        # print("UPDATE INVOKE")
        self.getStatuses(self.hass)

    @property
    def should_poll(self):
        """No polling needed within KNX."""
        return self._poll

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        # print("current_temperature(self)")  
        return self._measured_temperature

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        # print("target_temperature_step(self)" + str(self._setpoint_step))
        return self._setpoint_step


    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        # print("target_temperature(self)" + str(self._setpoint_temperature))
        return self._setpoint_temperature

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return self._setpoint_min


    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return self._setpoint_max

    @property
    def hvac_mode(self):
        """Return current operation ie. heat, cool, idle."""
        # print("hvac_mode(self) = " + str(self._heat_cool_status))
        if(self._heat_cool_status == 0) :
            return HVAC_MODE_OFF
        elif(self._heat_cool_status == 1) : 
            return HVAC_MODE_HEAT
        elif(self._heat_cool_status == 2) :
            return HVAC_MODE_COOL
        else :
            return HVAC_MODE_OFF
            

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        if self.device['thermostat_mode'] == DEFAULT_THERMOSTAT_MODE_HEAT:
            return [HVAC_MODE_OFF, HVAC_MODE_HEAT]
        if self.device['thermostat_mode'] == DEFAULT_THERMOSTAT_MODE_COOL:
            return [HVAC_MODE_OFF, HVAC_MODE_COOL]
        if self.device['thermostat_mode'] == DEFAULT_THERMOSTAT_MODE_HEAT_COOL:
            return [HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_COOL]

    @property
    def preset_mode(self):
        """Return the current preset mode, e.g., home, away, temp.
        Requires SUPPORT_PRESET_MODE.
        """
        if(self._operation_mode == 1) :
            return PRESET_AWAY
        elif(self._operation_mode == 2) :
            return PRESET_COMFORT
        elif(self._operation_mode == 3) :
            return PRESET_SLEEP
        else :
            return PRESET_AWAY

    @property
    def preset_modes(self):
        """Return a list of available preset modes.
        Requires SUPPORT_PRESET_MODE.
        """
        return [PRESET_SLEEP, PRESET_AWAY, PRESET_COMFORT]





    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        # print(kwargs)
        sendSetpoint = Telegram()
        sendSetpoint.initWithData("write", int(self.device['ha_bus_address']), int(self.device['setpoint_temperature']), AVS_DPT6, float(kwargs["temperature"]))
        self.hass.data[DATA_AVS].sendTelegram(sendSetpoint)

    # def set_temperature(self, **kwargs):
    #     """Set new target temperature."""
    #     print(kwargs)

    async def async_set_preset_mode(self, preset_mode):
        """Set new preset mode."""
        operation_mode = 0
        if preset_mode == "sleep":
            operation_mode = 3
        elif preset_mode == "comfort":
            operation_mode = 2
        elif preset_mode == "away":
            operation_mode = 1

        # print("async_set_preset_mode(self, preset_mode): " + str(operation_mode) + " " + str(preset_mode) +  " type = " + str(type(preset_mode)))
        sendOperationMode = Telegram()
        sendOperationMode.initWithData("write", int(self.device['ha_bus_address']), int(self.device['operation_mode']), AVS_DPT2, int(operation_mode))
        self.hass.data[DATA_AVS].sendTelegram(sendOperationMode)

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        # print(hvac_mode)  
        # self.schedule_update_ha_state()


    @property
    def current_humidity(self):
        """Return the current humidity."""
        return self._measured_humidity

    @property
    def target_humidity(self):
        """Return the humidity we try to reach."""
        return self._setpoint_humidity

    async def async_set_humidity(self, humidity):
        """Set new target humidity."""
        sendHumidity = Telegram()
        sendHumidity.initWithData("write", int(self.device['ha_bus_address']), int(self.device['setpoint_humidity']), AVS_DPT2, int(humidity))
        self.hass.data[DATA_AVS].sendTelegram(sendHumidity)

    @property
    def is_aux_heat(self):
        """Return true if aux heater.
        Requires SUPPORT_AUX_HEAT.
        """
        # print("is_aux_heat(self)" + str(self.is_aux_heat_on))
        return self.is_aux_heat_on


    async def async_turn_aux_heat_on(self):
        """Turn auxiliary heater on."""
        sendAuxHeatOn = Telegram()
        sendAuxHeatOn.initWithData("write", int(self.device['ha_bus_address']), int(self.device['aux_heat']), AVS_DPT1, int(1))
        self.hass.data[DATA_AVS].sendTelegram(sendAuxHeatOn)

    async def async_turn_aux_heat_off(self):
        """Turn auxiliary heater off."""
        sendAuxHeatOff = Telegram()
        sendAuxHeatOff.initWithData("write", int(self.device['ha_bus_address']), int(self.device['aux_heat']), AVS_DPT1, int(0))
        self.hass.data[DATA_AVS].sendTelegram(sendAuxHeatOff)