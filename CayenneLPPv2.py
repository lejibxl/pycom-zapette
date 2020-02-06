"""
based on : https:#github.com/simonqbs/cayennelpp-python
and : http:#upfiles.heclouds.com/forum-app/2018/07/15/673e6333f545809ddfae2f98ee4a4a73.pdf
No Complet !!!!
version : 2019-09-11
"""

import struct
import math
import logging.logging as logging
l = logging.getLogger(__name__)

LPP_DIGITAL_INPUT            = 0     # 1 byte
LPP_DIGITAL_OUTPUT           = 1     # 1 byte
LPP_ANALOG_INPUT             = 2     # 2 bytes, 0.01 signed
LPP_ANALOG_OUTPUT            = 3     # 2 bytes, 0.01 signed
LPP_GENERIC_SENSOR           = 4     # 4 bytes, unsigned (100)
LPP_LUMINOSITY               = 5     # 2 bytes, 1 lux unsigned
LPP_PRESENCE                 = 6     # 1 byte, bool
LPP_TEMPERATURE              = 7     # 2 bytes, 0.1°C signed
LPP_RELATIVE_HUMIDITY        = 8     # 1 byte, 0.5% unsigned
LPP_ACCELEROMETER            = 9     # 2 bytes per axis, 0.001G
LPP_BAROMETRIC_PRESSURE      = 10    # 2 bytes 0.1hPa unsigned
LPP_VOLTAGE                  = 11    # 2 bytes 0.01V unsigned
LPP_CURRENT                  = 12    # 2 bytes 0.001A unsigned
LPP_FREQUENCY                = 13    # 4 bytes 1Hz unsigned
LPP_PERCENTAGE               = 14    # 1 byte 1-100% unsigned
LPP_ALTITUDE                 = 15    # 2 byte 1m signed
LPP_POWER                    = 16    # 2 byte, 1W, unsigned
LPP_DISTANCE                 = 17    # 4 byte, 0.001m, unsigned
LPP_ENERGY                   = 18    # 4 byte, 0.001kWh, unsigned
LPP_DIRECTION                = 19    # 2 bytes, 1deg, unsigned
LPP_UNIXTIME                 = 20    # 4 bytes, unsigned
LPP_GYROMETER                = 21    # 2 bytes per axis, 0.01 °/s
LPP_GPS                      = 21    # 3 byte lon/lat 0.0001 °, 3 bytes alt 0.01 meter
LPP_SWITCH                   = 23    # 1 byte, 0/1
LPP_TEXT                     = 24    # 20 byte
LPP_BATTERY_LEVEL            = 25    # 1 byte en %

# Only Data Size
LPP_DIGITAL_INPUT_SIZE       = 1
LPP_DIGITAL_OUTPUT_SIZE      = 1
LPP_ANALOG_INPUT_SIZE        = 2
LPP_ANALOG_OUTPUT_SIZE       = 2
LPP_GENERIC_SENSOR_SIZE      = 4
LPP_LUMINOSITY_SIZE          = 2
LPP_PRESENCE_SIZE            = 1
LPP_TEMPERATURE_SIZE         = 2
LPP_RELATIVE_HUMIDITY_SIZE   = 1
LPP_ACCELEROMETER_SIZE       = 6
LPP_BAROMETRIC_PRESSURE_SIZE = 2
LPP_VOLTAGE_SIZE             = 2
LPP_CURRENT_SIZE             = 2
LPP_FREQUENCY_SIZE           = 4
LPP_PERCENTAGE_SIZE          = 1
LPP_ALTITUDE_SIZE            = 2
LPP_POWER_SIZE               = 2
LPP_DISTANCE_SIZE            = 4
LPP_ENERGY_SIZE              = 4
LPP_DIRECTION_SIZE           = 2
LPP_UNIXTIME_SIZE            = 4
LPP_GYROMETER_SIZE           = 6
LPP_GPS_SIZE                 = 9
LPP_SWITCH_SIZE              = 1
LPP_TEXT_SIZE                = None
LPP_BATTERY_LEVEL_SIZE       = 1

# Multipliers
LPP_DIGITAL_INPUT_MULT         = 1
LPP_DIGITAL_OUTPUT_MULT        = 1
LPP_ANALOG_INPUT_MULT          = 100
LPP_ANALOG_OUTPUT_MULT         = 100
LPP_GENERIC_SENSOR_MULT        = 1
LPP_LUMINOSITY_MULT            = 1
LPP_PRESENCE_MULT              = 1
LPP_TEMPERATURE_MULT           = 10
LPP_RELATIVE_HUMIDITY_MULT     = 2
LPP_ACCELEROMETER_MULT         = 1000
LPP_BAROMETRIC_PRESSURE_MULT   = 10
LPP_VOLTAGE_MULT               = 100
LPP_CURRENT_MULT               = 1000
LPP_FREQUENCY_MULT             = 1
LPP_PERCENTAGE_MULT            = 1
LPP_ALTITUDE_MULT              = 1
LPP_POWER_MULT                 = 1
LPP_DISTANCE_MULT              = 1000
LPP_ENERGY_MULT                = 1000
LPP_DIRECTION_MULT             = 1
LPP_UNIXTIME_MULT              = 1
LPP_GYROMETER_MULT             = 100
LPP_GPS_LAT_LON_MULT           = 10000
LPP_GPS_ALT_MULT               = 100
LPP_SWITCH_MULT                = 1
LPP_TEXT_MULT                  = None
LPP_BATTERY_LEVEL_MULT         = 1

LPP_ERROR_OK                    = 0
LPP_ERROR_OVERFLOW              = 1
LPP_ERROR_UNKOWN_TYPE           = 2

class LPP:
    def __init__(self):
        self.buffer = bytearray()
        #header = (batterylevel << 3) | 0b000
        #self.buffer.extend(struct.pack('b', header))

    def get_buffer(self):
        return self.buffer

    def reset(self):
        self.buffer = bytearray()

    def get_size(self):
        return len(self.buffer)

    def addField(self, type, channel, value) :

         # Check type
        if (not self._isType(type)):
            _error = LPP_ERROR_UNKOWN_TYPE
            return 0

        # Type definition
        size = self._getTypeSize(type)
        multiplier = self._getTypeMultiplier(type)
        is_signed = self._getTypeSigned(type)

        # get value to store
        v = math.floor(value * multiplier)

        # header
        self.buffer.extend(struct.pack('b', type))
        self.buffer.extend(struct.pack('b', channel))

        # add bytes (MSB first)
        for i in range(0,size):
            self.buffer.extend(struct.pack('b',(v & 0xFF)))
            v = v >> 8
            #v = long(v / 256)

        # update & return _cursor
        return size

    def add_temperature(self, channel, value):
        val = math.floor(value * 10)
        if channel > 0 :
            self.buffer.extend(struct.pack('b', LPP_TEMPERATURE))
            self.buffer.extend(struct.pack('b', channel))
        else:
            self.buffer.extend(struct.pack('b', LPP_TEMPERATURE + 0x80 ))
        self.buffer.extend(struct.pack('b', val >> 8))
        self.buffer.extend(struct.pack('b', val))

    def add_relative_humidity(self, channel, value):
        val = math.floor(value * 2)

        if channel > 0 :
            self.buffer.extend(struct.pack('b', LPP_RELATIVE_HUMIDITY))
            self.buffer.extend(struct.pack('b', channel))
        else:
            self.buffer.extend(struct.pack('b', LPP_RELATIVE_HUMIDITY + 0x80 ))
        self.buffer.extend(struct.pack('b', val))

    def add_digital_input(self, channel, value):

        if channel > 0 :
            self.buffer.extend(struct.pack('b', LPP_DIGITAL_INPUT))
            self.buffer.extend(struct.pack('b', channel))
        else:
            self.buffer.extend(struct.pack('b', LPP_DIGITAL_INPUT + 0x80 ))
        self.buffer.extend(struct.pack('b', value))

    def add_digital_output(self, channel, value):

        if channel > 0 :
            self.buffer.extend(struct.pack('b', LPP_DIGITAL_OUTPUT))
            self.buffer.extend(struct.pack('b', channel))
        else:
            self.buffer.extend(struct.pack('b', LPP_DIGITAL_OUTPUT + 0x80 ))
        self.buffer.extend(struct.pack('b', value))

    def add_analog_input(self, channel, value):
        val = math.floor(value * 100)

        if channel > 0 :
            self.buffer.extend(struct.pack('b', LPP_ANALOG_INPUT))
            self.buffer.extend(struct.pack('b', channel))
        else:
            self.buffer.extend(struct.pack('b', LPP_ANALOG_INPUT + 0x80 ))
        self.buffer.extend(struct.pack('b', val >> 8))
        self.buffer.extend(struct.pack('b', val))

    def add_analog_output(self, channel, value):
        val = math.floor(value * 100)

        if channel > 0 :
            self.buffer.extend(struct.pack('b', LPP_ANALOG_OUTPUT))
            self.buffer.extend(struct.pack('b', channel))
        else:
            self.buffer.extend(struct.pack('b', LPP_ANALOG_OUTPUT + 0x80 ))
        self.buffer.extend(struct.pack('b', val >> 8))
        self.buffer.extend(struct.pack('b', val))

    def add_luminosity(self, channel, value):

        if channel > 0 :
            self.buffer.extend(struct.pack('b', LPP_LUMINOSITY))
            self.buffer.extend(struct.pack('b', channel))
        else:
            self.buffer.extend(struct.pack('b', LPP_LUMINOSITY + 0x80 ))
        self.buffer.extend(struct.pack('b', value >> 8))
        self.buffer.extend(struct.pack('b', value))

    def add_presence(self, channel, value):

        if channel > 0 :
            self.buffer.extend(struct.pack('b', LPP_PRESENCE))
            self.buffer.extend(struct.pack('b', channel))
        else:
            self.buffer.extend(struct.pack('b', LPP_PRESENCE + 0x80 ))
        self.buffer.extend(struct.pack('b', value))

    def add_accelerometer(self, channel, x, y, z):
        vx = math.floor(x * 1000)
        vy = math.floor(y * 1000)
        vz = math.floor(z * 1000)

        if channel > 0 :
            self.buffer.extend(struct.pack('b', LPP_ACCELEROMETER))
            self.buffer.extend(struct.pack('b', channel))
        else:
            self.buffer.extend(struct.pack('b', LPP_ACCELEROMETER + 0x80 ))
        self.buffer.extend(struct.pack('b', vx >> 8))
        self.buffer.extend(struct.pack('b', vx))
        self.buffer.extend(struct.pack('b', vy >> 8))
        self.buffer.extend(struct.pack('b', vy))
        self.buffer.extend(struct.pack('b', vz >> 8))
        self.buffer.extend(struct.pack('b', vz))

    def add_barometric_pressure(self, channel, value):
        val = math.floor(value * 10)

        if channel > 0 :
            self.buffer.extend(struct.pack('b', LPP_BAROMETRIC_PRESSURE))
            self.buffer.extend(struct.pack('b', channel))
        else:
            self.buffer.extend(struct.pack('b', LPP_BAROMETRIC_PRESSURE + 0x80 ))
        self.buffer.extend(struct.pack('b', val >> 8))
        self.buffer.extend(struct.pack('b', val))

    def add_altitude(self, channel, meters):
        alt = math.floor(meters)

        if channel > 0 :
            self.buffer.extend(struct.pack('b', LPP_ALTITUDE))
            self.buffer.extend(struct.pack('b', channel))
        else:
            self.buffer.extend(struct.pack('b', LPP_ALTITUDE + 0x80 ))
        self.buffer.extend(struct.pack('b', alt >> 8))
        self.buffer.extend(struct.pack('b', alt))

    def add_gryrometer(self, channel, x, y, z):
        vx = math.floor(x * 100)
        vy = math.floor(y * 100)
        vz = math.floor(z * 100)

        if channel > 0 :
            self.buffer.extend(struct.pack('b', LPP_GYROMETER))
            self.buffer.extend(struct.pack('b', channel))
        else:
            self.buffer.extend(struct.pack('b', LPP_GYROMETER + 0x80 ))
        self.buffer.extend(struct.pack('b', vx >> 8))
        self.buffer.extend(struct.pack('b', vx))
        self.buffer.extend(struct.pack('b', vy >> 8))
        self.buffer.extend(struct.pack('b', vy))
        self.buffer.extend(struct.pack('b', vz >> 8))
        self.buffer.extend(struct.pack('b', vz))

    def add_gps(self, channel, latitude, longitude, meters):
        lat = math.floor(latitude * 10000)
        lon = math.floor(longitude * 10000)

        if channel > 0 :
            self.buffer.extend(struct.pack('b', LPP_GPS))
            self.buffer.extend(struct.pack('b', channel))
        else:
            self.buffer.extend(struct.pack('b', LPP_GPS + 0x80 ))
        self.buffer.extend(struct.pack('b', lat >> 16))
        self.buffer.extend(struct.pack('b', lat >> 8))
        self.buffer.extend(struct.pack('b', lat))
        self.buffer.extend(struct.pack('b', lon >> 16))
        self.buffer.extend(struct.pack('b', lon >> 8))
        self.buffer.extend(struct.pack('b', lon))

    def add_battery_level(self, channel, value):

        if channel > 0 :
            self.buffer.extend(struct.pack('b', LPP_BATTERY_LEVEL))
            self.buffer.extend(struct.pack('b', channel))
        else:
            self.buffer.extend(struct.pack('b', LPP_BATTERY_LEVEL + 0x80 ))
        self.buffer.extend(struct.pack('b', value))

    def add_text(self, channel, value):
        val = value[:16] # size max= 16
        if channel > 0 :
            self.buffer.extend(struct.pack('b', LPP_TEXT))
            self.buffer.extend(struct.pack('b', channel))
        else:
            self.buffer.extend(struct.pack('b', LPP_TEXT + 0x80 ))
        self.buffer.extend(struct.pack('b',len(value)))
        self.buffer.extend(value)

    def decode(self, buffer):
        count = 0
        index = 0
        bufferSize=len(buffer)
        datas=[]
        while ((index + 2) < bufferSize):
            count +=1
            # Get data type
            type = buffer[index]
            index +=1
            if type >=0x80 :
                type = type - 0x80
                channel = 0x00
            else:
                # Get channel #
                channel = buffer[index]
                index +=1

            if (not self._isType(type)):
                _error = LPP_ERROR_UNKOWN_TYPE
                return 0
            # Type definition
            size = self._getTypeSize(type)
            if size == None :
                 size = buffer[index]
                 index +=1
            multiplier = self._getTypeMultiplier(type)
            is_signed = self._getTypeSigned(type)

            # Check buffer size
            if (index + size > bufferSize) :
                _error = LPP_ERROR_OVERFLOW
                return 0

            # Init object
            data = {}
            data["channel"] = channel
            data["type"] = type
            data["name"] = self._getTypeName(type)

            # Parse types
            if (LPP_ACCELEROMETER == type or LPP_GYROMETER == type) :
                valuedict={}
                valuedict["x"] = self._getValue(buffer[index:index+2], multiplier, is_signed)
                valuedict["y"] = self._getValue(buffer[index+2:index+4], multiplier, is_signed)
                valuedict["z"] = self._getValue(buffer[index+4:index+6], multiplier, is_signed)
                data["value"]  = valuedict
            elif (LPP_GPS == type) :
                valuedict={}
                valuedict["latitude"] = self._getValue(buffer[index:index+3], 10000, is_signed)
                valuedict["longitude"] = self._getValue(buffer[index+3:index+6], 10000, is_signed)
                valuedict["altitude"] = self._getValue(buffer[index+6:index+9], 100, is_signed)
                data["value"]  = valuedict
            elif (LPP_TEXT == type):
                 data["value"] = buffer[index:index+size]
            else:
                 data["value"] = self._getValue(buffer[index:index+size], multiplier, is_signed)
            datas.append(data)
            index += size
        return datas

    def _isType(self, type):
        if (LPP_DIGITAL_INPUT == type) : return True
        if (LPP_DIGITAL_OUTPUT == type) : return True
        if (LPP_ANALOG_INPUT == type) : return True
        if (LPP_ANALOG_OUTPUT == type) : return True
        if (LPP_GENERIC_SENSOR == type) : return True
        if (LPP_LUMINOSITY == type) : return True
        if (LPP_PRESENCE == type) : return True
        if (LPP_TEMPERATURE == type) : return True
        if (LPP_RELATIVE_HUMIDITY == type) : return True
        if (LPP_ACCELEROMETER == type) : return True
        if (LPP_BAROMETRIC_PRESSURE == type) : return True
        if (LPP_VOLTAGE == type) : return True
        if (LPP_CURRENT == type) : return True
        if (LPP_FREQUENCY == type) : return True
        if (LPP_PERCENTAGE == type) : return True
        if (LPP_ALTITUDE == type) : return True
        if (LPP_POWER == type) : return True
        if (LPP_DISTANCE == type) : return True
        if (LPP_ENERGY == type) : return True
        if (LPP_DIRECTION == type) : return True
        if (LPP_UNIXTIME == type) : return True
        if (LPP_GYROMETER == type) : return True
        if (LPP_GPS == type) : return True
        if (LPP_SWITCH == type) : return True
        if (LPP_TEXT == type) : return True
        return False

    def _getTypeSize(self, type):
        if (LPP_DIGITAL_INPUT == type) : return LPP_DIGITAL_INPUT_SIZE
        if (LPP_DIGITAL_OUTPUT == type) : return LPP_DIGITAL_OUTPUT_SIZE
        if (LPP_ANALOG_INPUT == type) : return LPP_ANALOG_INPUT_SIZE
        if (LPP_ANALOG_OUTPUT == type) : return LPP_ANALOG_OUTPUT_SIZE
        if (LPP_GENERIC_SENSOR == type) : return LPP_GENERIC_SENSOR_SIZE
        if (LPP_LUMINOSITY == type) : return LPP_LUMINOSITY_SIZE
        if (LPP_PRESENCE == type) : return LPP_PRESENCE_SIZE
        if (LPP_TEMPERATURE == type) : return LPP_TEMPERATURE_SIZE
        if (LPP_RELATIVE_HUMIDITY == type) : return LPP_RELATIVE_HUMIDITY_SIZE
        if (LPP_ACCELEROMETER == type) : return LPP_ACCELEROMETER_SIZE
        if (LPP_BAROMETRIC_PRESSURE == type) : return LPP_BAROMETRIC_PRESSURE_SIZE
        if (LPP_VOLTAGE == type) : return LPP_VOLTAGE_SIZE
        if (LPP_CURRENT == type) : return LPP_CURRENT_SIZE
        if (LPP_FREQUENCY == type) : return LPP_FREQUENCY_SIZE
        if (LPP_PERCENTAGE == type) : return LPP_PERCENTAGE_SIZE
        if (LPP_ALTITUDE == type) : return LPP_ALTITUDE_SIZE
        if (LPP_POWER == type) : return LPP_POWER_SIZE
        if (LPP_DISTANCE == type) : return LPP_DISTANCE_SIZE
        if (LPP_ENERGY == type) : return LPP_ENERGY_SIZE
        if (LPP_DIRECTION == type) : return LPP_DIRECTION_SIZE
        if (LPP_UNIXTIME == type) : return LPP_UNIXTIME_SIZE
        if (LPP_GYROMETER == type) : return LPP_GYROMETER_SIZE
        if (LPP_GPS == type) : return LPP_GPS_SIZE
        if (LPP_SWITCH == type) : return LPP_SWITCH_SIZE
        if (LPP_TEXT == type) : return LPP_TEXT_SIZE
        return 0

    def _getTypeMultiplier(self, type) :
    	if (LPP_DIGITAL_INPUT == type): return LPP_DIGITAL_INPUT_MULT
    	if (LPP_DIGITAL_OUTPUT == type): return LPP_DIGITAL_OUTPUT_MULT
    	if (LPP_ANALOG_INPUT == type): return LPP_ANALOG_INPUT_MULT
    	if (LPP_ANALOG_OUTPUT == type): return LPP_ANALOG_OUTPUT_MULT
    	if (LPP_GENERIC_SENSOR == type): return LPP_GENERIC_SENSOR_MULT
    	if (LPP_LUMINOSITY == type): return LPP_LUMINOSITY_MULT
    	if (LPP_PRESENCE == type): return LPP_PRESENCE_MULT
    	if (LPP_TEMPERATURE == type): return LPP_TEMPERATURE_MULT
    	if (LPP_RELATIVE_HUMIDITY == type): return LPP_RELATIVE_HUMIDITY_MULT
    	if (LPP_BAROMETRIC_PRESSURE == type): return LPP_BAROMETRIC_PRESSURE_MULT
    	if (LPP_VOLTAGE == type): return LPP_VOLTAGE_MULT
    	if (LPP_CURRENT == type): return LPP_CURRENT_MULT
    	if (LPP_FREQUENCY == type): return LPP_FREQUENCY_MULT
    	if (LPP_PERCENTAGE == type): return LPP_PERCENTAGE_MULT
    	if (LPP_ALTITUDE == type): return LPP_ALTITUDE_MULT
    	if (LPP_POWER == type): return LPP_POWER_MULT
    	if (LPP_DISTANCE == type): return LPP_DISTANCE_MULT
    	if (LPP_ENERGY == type): return LPP_ENERGY_MULT
    	if (LPP_DIRECTION == type): return LPP_DIRECTION_MULT
    	if (LPP_UNIXTIME == type): return LPP_UNIXTIME_MULT
    	if (LPP_SWITCH == type): return LPP_SWITCH_MULT
        return 0

    def _getTypeSigned(self, type) :
    	if (LPP_ANALOG_INPUT == type): return True
    	if (LPP_ANALOG_OUTPUT == type): return True
    	if (LPP_TEMPERATURE == type): return True
    	if (LPP_ACCELEROMETER == type): return True
    	if (LPP_ALTITUDE == type): return True
    	if (LPP_GYROMETER == type): return True
    	if (LPP_GPS == type): return True
    	return False

    def _getValue(self, buffer, multiplier, is_signed) :
        #à vérifier
    	value = 0
        size = len(buffer)
        #print(buffer,value,size)
    	for i in buffer:
    		value = (value * 256) + i

    	sign = 1
    	if (is_signed) :
    		bit = 1 << ((size * 8) - 1)
    		if ((value & bit) == bit) :
    			value = (bit << 1) - value
    			sign = -1

    	return sign * (float(value / multiplier))

    def _getTypeName(self, type) :
    	if (LPP_DIGITAL_INPUT == type):  return "digital_input"
    	if (LPP_DIGITAL_OUTPUT == type):  return "digital_output"
    	if (LPP_ANALOG_INPUT == type):  return "analog_input"
    	if (LPP_ANALOG_OUTPUT == type):  return "analog_output"
    	if (LPP_GENERIC_SENSOR == type):  return "generic"
    	if (LPP_LUMINOSITY == type):  return "luminosity"
    	if (LPP_PRESENCE == type):  return "presence"
    	if (LPP_TEMPERATURE == type):  return "temperature"
    	if (LPP_RELATIVE_HUMIDITY == type):  return "humidity"
    	if (LPP_ACCELEROMETER == type):  return "accelerometer"
    	if (LPP_BAROMETRIC_PRESSURE == type):  return "pressure"
    	if (LPP_VOLTAGE == type):  return "voltage"
    	if (LPP_CURRENT == type):  return "current"
    	if (LPP_FREQUENCY == type):  return "frequency"
    	if (LPP_PERCENTAGE == type):  return "percentage"
    	if (LPP_ALTITUDE == type):  return "altitude"
    	if (LPP_POWER == type):  return "power"
    	if (LPP_DISTANCE == type):  return "distance"
    	if (LPP_ENERGY == type):  return "energy"
    	if (LPP_DIRECTION == type):  return "direction"
    	if (LPP_UNIXTIME == type):  return "time"
    	if (LPP_GYROMETER == type):  return "gyrometer"
    	if (LPP_GPS == type):  return "gps"
    	if (LPP_SWITCH == type):  return "switch"
        if (LPP_TEXT == type):  return "text"
    	return 0

if __name__ == '__main__' :
    myLPP = LPP()
    #buffer= bytearray([0x03,0x67,0x01,0x10 ,0x05 ,0x67 ,0x00 ,0xFF])
    #buffer= bytearray([0x01,0x88,0x06,0x76,0x5f,0xf2,0x96,0x0a,0x00,0x03,0xe8])
    #buffer= bytearray([0x01,0x01,0x01])
    #print(myLPP.decode(buffer))
    myLPP.add_text(1,"rrr")
    print(myLPP.get_buffer())
    print(myLPP.decode(myLPP.get_buffer()))
