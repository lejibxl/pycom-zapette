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

# Only Data Size
LPP_Dict = [
    {'ID':0x09,    'name':'LPP_CMD_REFRESH',         'format': '!B'},
    {'ID':0x10,    'name':'LPP_DIGITAL_INPUT',       'format': '!B'},            # 1 byte
    {'ID':0x11,    'name':'LPP_DIGITAL_OUTPUT',      'format': '!B'},           # 1 byte
    {'ID':0x12,    'name':'LPP_ANALOG_INPUT',        'format': '!h'},           # 2 bytes, 0.01 signed
    {'ID':0x13,    'name':'LPP_ANALOG_OUTPUT',       'format': '!h'},
    {'ID':0x14,    'name':'LPP_GENERIC_SENSOR',      'format': '!I'},
    {'ID':0x15,    'name':'LPP_LUMINOSITY',          'format': '!H'},
    {'ID':0x15,    'name':'LPP_PRESENCE',            'format': '!B'},
    {'ID':0x17,    'name':'LPP_TEMPERATURE',         'format': '!h'},
    {'ID':0x18,    'name':'LPP_RELATIVE_HUMIDITY',   'format': '!B'},
    {'ID':0x19,    'name':'LPP_ACCELEROMETER',       'format': '!hhh'},
    {'ID':0x1A,    'name':'LPP_BAROMETRIC_PRESSURE', 'format': '!H'},
    {'ID':0x1B,    'name':'LPP_VOLTAGE',             'format': '!H'},
    {'ID':0x1C,    'name':'LPP_CURRENT',             'format': '!H'},
    {'ID':0x1D,    'name':'LPP_FREQUENCY',           'format': '!I'},
    {'ID':0x1E,    'name':'LPP_PERCENTAGE',          'format': '!B'},
    {'ID':0x1F,    'name':'LPP_ALTITUDE',            'format': '!h'},
    {'ID':0x20,    'name':'LPP_POWER',               'format': '!f'},
    {'ID':0x21,    'name':'LPP_DISTANCE',            'format': '!I'},
    {'ID':0x22,    'name':'LPP_ENERGY',              'format': '!f'},
    {'ID':0x23,    'name':'LPP_DIRECTION',           'format': '!H'},
    {'ID':0x24,    'name':'LPP_UNIXTIME',            'format': '!I'},
    {'ID':0x25,    'name':'LPP_GYROMETER',           'format': '!hhh'},
    {'ID':0x26,    'name':'LPP_GPS',                 'format': '!iih'},
    {'ID':0x27,    'name':'LPP_SWITCH',              'format': '!B'},
    {'ID':0x28,    'name':'LPP_TEXT',                'format': '!s'},
    {'ID':0x29,    'name':'LPP_BATTERY_LEVEL',       'format': '!B'},
]

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

    def get_size(self):
        return len(self.buffer)

    def reset(self):
        self.buffer = bytearray()

    def get_typeByName(self, name):
            for item in LPP_Dict:
                if item['name'] == name:
                    return item
            return None

    def get_typeByID(self, ID):
            for item in LPP_Dict:
                if item['ID'] == ID:
                    return item
            return None
    def addField(self, type, channel, value) :
         # Check type

        buf=bytearray()
        lpp_type = self.get_typeByName(type)
        if lpp_type == None:
            l.error("LPP_ERROR_UNKOWN_TYPE")
            return 0

        # ADD header
        if channel > 0 :
            self.buffer.extend(struct.pack('b', lpp_type['ID']))
            self.buffer.extend(struct.pack('b', channel))
        else:
            self.buffer.extend(struct.pack('b', lpp_type['ID'] + 0x80 ))

        # ADD data
        if isinstance(value, list):
            datas = value
        else :
            datas =[value]
        self.buffer.extend(struct.pack(lpp_type['format'], *datas))
        # update & return _cursor
        return len(self.buffer)


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
        while ((index + 1) < bufferSize):
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

            lpp_type=self.get_typeByID(type)
            if lpp_type == None:
                l.error(LPP_ERROR_UNKOWN_TYPE)
                return 0

            # Type definition
            size = struct.calcsize(lpp_type['format'])
            if size == None :
                 size = buffer[index]
                 index +=1

            # Check buffer size
            if (index + size > bufferSize) :
                l.error(LPP_ERROR_OVERFLOW)
                return 0

            # Init object
            data = {}
            data["channel"] = channel
            data["type"] = type
            data["name"] = lpp_type['name']
            value=struct.unpack(lpp_type['format'],buffer[index:index + size])
            if len(value) == 1 :
                data["value"]=value[0]
            else:
                data["value"]=value
            datas.append(data)
            index += size
        return datas



if __name__ == '__main__' :
    myLPP = LPP()
    #buffer= bytearray([0x03,0x67,0x01,0x10 ,0x05 ,0x67 ,0x00 ,0xFF])
    #buffer= bytearray([0x01,0x88,0x06,0x76,0x5f,0xf2,0x96,0x0a,0x00,0x03,0xe8])
    #buffer= bytearray([0x01,0x01,0x01])
    #print(myLPP.decode(buffer))
    #myLPP.addField(LPP_GENERIC_SENSOR,0,0xF1 * 256 + 0x1F)
    #myLPP.addField("LPP_POWER",0,60)
    #print(myLPP.get_buffer())
    #print(myLPP.decode(myLPP.get_buffer()))
    print(myLPP.decode(b'\x89\x00'))
    #print(int())
