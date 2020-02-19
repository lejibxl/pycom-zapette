import uos
import zapette.zapetteLPP as zapetteLPP
import utime
from network import LoRa
import socket
import ubinascii
import struct
import logging.logging as logging
#from zapette.zapette_handler import ZapetteHandler
l = logging.getLogger(__name__)
l.setLevel(logging.INFO)
class Zapette:
    def __init__(self, device_id, handler_rx=None, handler_tx=None ):
        #.addHandler(ZapetteHandler("self"),2)
        l.debug("loraBlk init ...")
        self.device_id = bytes([device_id])
        self._user_handler_rx  = handler_rx
        self._user_handler_tx  = handler_tx
        n=uos.urandom(2)
        self.frame_cnt = n[0] + n[1]*256
        self.lpp=zapetteLPP.LPP()
        # initialise LoRa in LORA mode
        self.lora = LoRa(mode=LoRa.LORA,
                    region=LoRa.EU868,
                    sf=12,
                    tx_power=20,
                    public=False,
                    preamble=8, #default
                    bandwidth = LoRa.BW_125KHZ,
                    coding_rate = LoRa.CODING_4_8)
        # create a raw LoRa socket
        self.lora_sock= socket.socket(socket.AF_LORA, socket.SOCK_RAW)
        self.lora_sock.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, True) # selecting confirmed type of messages
        self.lora.callback(trigger=(LoRa.RX_PACKET_EVENT | LoRa.TX_PACKET_EVENT), handler=self._lora_cb)
        self.frame_TX=[]
        self.frame_ACK = None
        self.frame_ACK_stats = None
        self.tx_timeout = 4000
        self.tx_retries = 3

    def _lora_cb(self, lora):
        """
        LoRa radio events callback handler.
        """
        global RX,TX,lpp
        events = lora.events()
        stats = lora.stats()
        l.debug("event: {}".format(events))
        l.debug("stats: {}".format(stats))
        if events & LoRa.RX_PACKET_EVENT:
            rx_frame = self.lora_sock.recv(256)
            l.debug("rx : {}".format(ubinascii.hexlify(rx_frame)))
            #header
            device_from = rx_frame[0:1]
            device_to = rx_frame[1:2]
            frame_type =  rx_frame[2:3]
            frame_cnt = rx_frame[3:5]
            payload = rx_frame[5:-1]
            crc = rx_frame[-1]

            l.debug("device_from:{} ,device_to:{} ,frame_type:{}, frame_cnt:{}, crc:{}, payload:{}".format(device_from,device_to,frame_type,frame_cnt,crc,payload))
            if device_to == self.device_id :
                if frame_type ==  b'\x00' : #RX w/ ACK
                    l.debug("FRAME RX w/ ACK")
                    self._send_frame_ACK(device_from, frame_cnt, stats, b'\x01')
                    if self._user_handler_rx is not None:
                        lpp_rx=self.lpp.decode(payload)
                        if lpp_rx != None:
                            self._user_handler_rx(lpp_rx,{'rssi':stats.rssi,'snr':stats.snr})
                    else:
                        l.debug("no Handler")
                elif frame_type ==  b'\x01' : #RX w/o ACK
                    l.debug("FRAME RX w/o ACK")
                    if self._user_handler_rx is not None:
                        lpp_rx=self.lpp.decode(payload)
                        if lpp_rx != None:
                            self._user_handler_rx(lpp_rx,{'rssi':stats.rssi,'snr':stats.snr})
                    else:
                        l.debug("no Handler")
                elif frame_type ==  b'\x10' : #ACK
                    l.debug("FRAME ACK")
                    #tmp = struct.unpack("bhf",payload) Bug
                    status =  payload[0]
                    rssi = struct.unpack("h",payload[1:3])[0]
                    snr = struct.unpack("f",payload[3:])[0]
                    self.frame_ACK = frame_cnt
                    self.frame_ACK_stats = {'rssi':rssi, 'snr':snr}
                    if self._user_handler_rx is not None:
                        self._user_handler_rx(None,{'rssi':stats.rssi,'snr':stats.snr})
            else:
                l.debug("messages for: {}".format(device_to))

        elif events & LoRa.TX_PACKET_EVENT:
            l.debug("FRAME send")
        else:
            l.debug("???")

    def _send_frame_ACK(self, device_to, frame_cnt, stats, status):
        device_from = self.device_id
        device_to = device_to
        frame_type =  b'\x10'
        frame_cnt = frame_cnt
        rssi = stats.rssi
        snr = stats.snr
        payload = status + struct.pack("h",rssi) + struct.pack("f",snr)
        crc = b'\x00'
        tx_frame = self.device_id + device_to + frame_type + frame_cnt + payload + crc
        l.debug("tx : {}".format(ubinascii.hexlify(tx_frame)))
        self.lora_sock.send(tx_frame)

    def send_frame_TX(self, device_to,msg, ack = True ):
        device_from = self.device_id
        device_to = bytes([device_to])
        frame_type =  b'\x00' if ack == True else b'\x01'
        frame_cnt = b'\x00\x01'
        payload = msg.get_buffer()
        crc = b'\x00'
        msg.reset()
        tx_frame = self.device_id + device_to + frame_type + frame_cnt + payload + crc
        l.debug("tx: {}, ack: {}".format(ubinascii.hexlify(tx_frame),ack))
        if ack == True:
            self.frame_ACK = None
            for i in range(0,self.tx_retries):
                self.lora_sock.send(tx_frame)
                ticks_sign = utime.ticks_diff(1, 2) # get the sign of ticks_diff, e.g. in init code.
                deadline = utime.ticks_add(utime.ticks_ms(), self.tx_timeout)
                if self._user_handler_tx is not None:
                    self._user_handler_tx(i)
                while (utime.ticks_diff(deadline, utime.ticks_ms()) * ticks_sign) < 0:
                    if self.frame_ACK == frame_cnt:
                        l.debug("tx OK")
                        return self.frame_ACK_stats
                l.debug("tx NOK {}/{}".format(i+1,self.tx_retries))
        else:
            self.lora_sock.send(tx_frame)
        return None

def test_rx(lpp_rx,stats):
    print(stats)
    if lpp_rx != None:
        for lpp_action in lpp_rx:
            if lpp_action["type"] == 1 and lpp_action["channel"] == 1 :
                if lpp_action["value"]  == 1 :
                    print ("Turn ON")
                else:
                    print ("Turn OFF")

def test_tx(retries):
    print(retries)

if __name__ == '__main__' and 2 == 1:
    zapette=Zapette(0x02,handler_rx=test_rx,handler_tx=test_tx)
    lpp=zapetteLPP.LPP()
    while True:
        #lpp.add_digital_input(0,1)
        print(zapette.send_frame_TX(0x01, lpp))
        utime.sleep(1)
