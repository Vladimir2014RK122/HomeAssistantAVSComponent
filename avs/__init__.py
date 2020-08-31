import logging

import crcmod
import numpy as np

import socket
import struct
import asyncio
import selectors

import voluptuous as vol

_LOGGER = logging.getLogger(__name__)


_LOGGER.warning("Start AVS Custom component")


from homeassistant.const import (
    CONF_ENTITY_ID,
    CONF_HOST,
    CONF_PORT,
    EVENT_HOMEASSISTANT_STOP,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import callback
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import async_track_state_change
from homeassistant.helpers.script import Script

_LOGGER = logging.getLogger(__name__)

DOMAIN = "avs"
DATA_AVS = "data_avs"

CONF_AVS_MCAST_GROUP = "mcast_group"
CONF_AVS_HA_ADDRESS = "ha_avs_address"


AVS_DPT1 = 1
AVS_DPT2 = 2
AVS_DPT3 = 3
AVS_DPT4 = 4
AVS_DPT5 = 5
AVS_DPT6 = 6
AVS_DPT7 = 7
AVS_DPT8 = 8
AVS_DPT9 = 9
AVS_DPT10 = 10
AVS_DPT11 = 11



CONFIG_SCHEMA = vol.Schema(
    {
      DOMAIN: vol.Schema({
        vol.Required(CONF_AVS_MCAST_GROUP): cv.string,
        vol.Required(CONF_AVS_HA_ADDRESS): cv.string,
        
      })
      
    }, extra=vol.ALLOW_EXTRA
)



config_map = {
    "mcast_group": "239.1.1.11",
    "mcast_port": "3000",
    "ha_avs_address": "12345"
}


async def async_setup(hass, config):
    """Set up the AVS component."""
    text = config[DOMAIN].get(CONF_AVS_MCAST_GROUP, "None group")
    _LOGGER.warning("AVS Component is ready "+ text)

    crc8 = crcmod.predefined.mkPredefinedCrcFun('crc-8-maxim')
    # print (hex(crc8(bytes([10,11,12,13]))))
    
    hass.data[DATA_AVS] = AVSModule(config_map)
    hass.loop.create_task(hass.data[DATA_AVS].listenGroup(hass))
    hass.loop.create_task(hass.data[DATA_AVS].checkOutputTelQueue(hass))
    
    return True
    
    

inputTelegramsQueue = list()

class AVSModule:
    def __init__(self, config):
        # print(config["mcast_group"])
        self.inputTelegramsQueue = list()
        self.outputTelegramsQueue = list()

        self.config = config
        self.ha_bus_address = config.get(CONF_AVS_HA_ADDRESS)

        self.sockRead = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sockRead.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sockRead.bind(('', int(config["mcast_port"])))
        mreq = struct.pack("4sl", socket.inet_aton(config["mcast_group"]), socket.INADDR_ANY)
        self.sockRead.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self.multicast_group = (config["mcast_group"], int(config["mcast_port"]))
        self.sockSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ttl = struct.pack('b', 1)
        self.sockSend.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    def getHaBusAddr(self):
        return self.ha_bus_address

    async def listenGroup(self, hass):
        # print("Start listening group")
        selector = selectors.DefaultSelector()
        selector.register(self.sockRead, selectors.EVENT_READ, readInputData)
        while True:
            events = selector.select(timeout=0.01)
            if events:
                for key, event in events:
                    callback = key.data
                    callback(hass, key.fileobj)
            else:
                await asyncio.sleep(0)
           
    async def isAlive(self):
        # print("Start listening group")
        while True:
            _LOGGER.warning('alive')
            await asyncio.sleep(5)

    def sendTelegram(self, telegram):
        self.outputTelegramsQueue.append(telegram)

    async def checkOutputTelQueue(self, hass):
        while True:
            if len(self.outputTelegramsQueue) != 0:
                # print("in output queue " + str(len(self.outputTelegramsQueue)) + " telegrams")
                self.sockSend.sendto(self.outputTelegramsQueue.pop(0).getByteView(), self.multicast_group)

            await asyncio.sleep(0.1)


def readInputData(hass, sockRead):
    message, address = sockRead.recvfrom(4096)
    inputTelegram = Telegram()
    if inputTelegram.initWithByteView(message) == True :

        # print(' AVS receive Data from:' + str(address[0]) + ': ' + inputTelegram.teltoStr())
        # print("get_Host_name_IP() = " + str(get_Host_name_IP()) + " type: " + str(type(get_Host_name_IP())))
        # print("address[0] = " + str(address[0]) + " type: " + str(type(address[0])))

        if get_ip() != address[0]:
            # _LOGGER.warning(' AVS receive Data from:' + str(address[0]) + ': ' + inputTelegram.teltoStr())
            #print(' AVS receive Data from:' + str(address[0]) + ': ' + inputTelegram.teltoStr())
        
            hass.bus.async_fire("avs_bus_event/" + str(inputTelegram.getTelAddress()),
                {"address": inputTelegram.getTelAddress(), "data_type": inputTelegram.getDataType(), "source": inputTelegram.getSrcAddress(),"data": inputTelegram.getData()},)
    

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

    





TELEGRAM_TYPE_WRITE = "write"
TELEGRAM_TYPE_READ = "read"
TELEGRAM_TYPE_RESPONSE = "response"

class Telegram:
    
    def initWithData(self, telegram_type, source_address, telegram_address, data_type, data=0):
        self.telegram_type = telegram_type
        self.source_address = source_address
        self.telegram_address = telegram_address
        self.data_type = data_type
        self.data = data


        self.byteView = self.getByteView()
    
    def initWithByteView(self, byteList):
        self.byteView = byteList
        return self.convertFromByteView()
        
    def setData(self, data):
        self.data = data

    def getByteView(self):

        byteList = []

        crc8 = crcmod.predefined.mkPredefinedCrcFun('crc-8-maxim')

        if self.telegram_type == TELEGRAM_TYPE_WRITE or self.telegram_type == TELEGRAM_TYPE_RESPONSE:

            if self.telegram_type == TELEGRAM_TYPE_WRITE: t_type = 0x1F # WRITE
            else: t_type = 0x17 # RESPONSE

            byteList.append(0xBF)
            byteList.append((self.source_address >> 8) & 0xFF)
            byteList.append(self.source_address & 0xFF)
            byteList.append((self.telegram_address >> 8) & 0xFF)
            byteList.append(self.telegram_address & 0xFF)   

            if self.data_type == 1 or self.data_type == 2 or self.data_type == 4:
                data_len = 1
                byteList.append(0x80 + data_len)
                byteList.append(t_type) # WRITE
                byteList.append(self.data_type)

                byteList.append(self.data)       
                byteList.append(crc8(bytes(byteList)))
            if self.data_type == 3:
                data_len = 1
                byteList.append(0x80 + data_len)
                byteList.append(t_type) # WRITE
                byteList.append(self.data_type) 

                byteList.append(self.data & 0xFF)       
                byteList.append(crc8(bytes(byteList)))
            elif self.data_type == 5:
                data_len = 2
                byteList.append(0x80 + data_len)
                byteList.append(t_type) # WRITE
                byteList.append(self.data_type)

                byteList.append((self.data >> 8) & 0xFF   )
                byteList.append(self.data & 0xFF)
                byteList.append(crc8(bytes(byteList)))
            elif self.data_type == 6:
                data_len = 4
                byteList.append(0x80 + data_len)
                byteList.append(t_type) # WRITE
                byteList.append(self.data_type)

                ba = bytearray(struct.pack("f", self.data)) 

                byteList.append(ba[3]) 
                byteList.append(ba[2]) 
                byteList.append(ba[1]) 
                byteList.append(ba[0])
                byteList.append(crc8(bytes(byteList)))
            elif self.data_type >= 7 and self.data_type <= 8:
                data_len = 4
                byteList.append(0x80 + data_len)
                byteList.append(t_type) # WRITE
                byteList.append(self.data_type)

                byteList.append(0)
                byteList.append((self.data >> 16) & 0xFF)
                byteList.append((self.data >> 8) & 0xFF)
                byteList.append((self.data >> 0) & 0xFF)
                byteList.append(crc8(bytes(byteList)))
            elif self.data_type >= 9 and self.data_type <= 11:
                data_len = 4
                byteList.append(0x80 + data_len)
                byteList.append(t_type) # WRITE
                byteList.append(self.data_type)

                byteList.append((self.data >> 24) & 0xFF) 
                byteList.append((self.data >> 16) & 0xFF) 
                byteList.append((self.data >> 8) & 0xFF) 
                byteList.append((self.data >> 0) & 0xFF)     
                byteList.append(crc8(bytes(byteList)))
        else:
            t_type = 0x0F # READ

            byteList.append(0xBF)
            byteList.append((self.source_address >> 8) & 0xFF)
            byteList.append(self.source_address & 0xFF)
            byteList.append((self.telegram_address >> 8) & 0xFF)
            byteList.append(self.telegram_address & 0xFF)

            crc8 = crcmod.predefined.mkPredefinedCrcFun('crc-8-maxim')

            data_len = 1
            byteList.append(0x80 + data_len)
            byteList.append(t_type) # WRITE
            byteList.append(self.data_type)
            byteList.append(crc8(bytes(byteList)))
        
        return bytes(byteList)

    def convertFromByteView(self):

        crc8 = crcmod.predefined.mkPredefinedCrcFun('crc-8-maxim')

        payloadData = [self.byteView[i] for i in range(len(self.byteView) - 1)]

        if self.byteView[0] == 0xBF and self.byteView[len(self.byteView) - 1] == crc8(bytes(payloadData)):

            self.source_address = ((0x00FF & self.byteView[1]) << 8) | self.byteView[2]
            if self.byteView[6] == 0x1F:
                self.telegram_type = TELEGRAM_TYPE_WRITE
            elif self.byteView[6] == 0x17:
                self.telegram_type = TELEGRAM_TYPE_RESPONSE
            else:
                self.telegram_type = TELEGRAM_TYPE_READ
            
            self.telegram_address = ((0x00FF & self.byteView[3]) << 8) | self.byteView[4]
            self.data_type = self.byteView[7]
            if self.telegram_type == TELEGRAM_TYPE_WRITE or self.telegram_type == TELEGRAM_TYPE_RESPONSE:

                if self.data_type == 1 or self.data_type == 2  or self.data_type == 4:
                    self.data = self.byteView[8]
                elif self.data_type == 3:
                    self.data = np.int8(self.byteView[8])
                elif self.data_type == 5:
                    self.data = ((0x00FF & self.byteView[8]) << 8) | self.byteView[9]
                elif self.data_type == 6:
                    self.data = struct.unpack('f', bytearray([self.byteView[11], self.byteView[10], self.byteView[9], self.byteView[8]]))[0]
                elif self.data_type == 7 or self.data_type == 8:  
                    self.data = ((0x0000FF & self.byteView[8]) << 16) | ((0x0000FF & self.byteView[9]) << 16) | ((0x0000FF & self.byteView[10]) << 8) | self.byteView[11]
                elif self.data_type == 9 or self.data_type == 10: 
                    self.data = ((0x0000FF & self.byteView[8]) << 24) | ((0x0000FF & self.byteView[9]) << 16) | ((0x0000FF & self.byteView[10]) << 8) | self.byteView[11]
                elif self.data_type == 11: 
                    self.data = self.data = struct.unpack('i', bytearray([self.byteView[11], self.byteView[10], self.byteView[9], self.byteView[8]]))[0]
            else:
                self.data = 0
            return True
        else:
            print("ERROR DATA")
            return False

    def getData(self):
        return self.data

    def getDataType(self):
        return self.data_type
    
    def getTelType(self):
        return self.telegram_type

    def getTelAddress(self):
        return self.telegram_address

    def getSrcAddress(self):
        return self.source_address

    def teltoStr(self):

        telStr = "Telegram [ tel type: " + self.telegram_type
        telStr += ", source: " + str(self.source_address)
        telStr += ", address: " + str(self.telegram_address)
        telStr += ", data type: " + str(self.data_type)
        telStr += ", data: " + str(self.data)
        return telStr

