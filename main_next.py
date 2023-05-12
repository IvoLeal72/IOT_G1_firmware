
# Test Display SSD1306 controller
# ESP32 Pin assignment
# i2c = I2C(0, mode=I2C.MASTER, pins=('G21','G22'), baudrate=100000)

# oled_width = 128
# oled_height = 64
# oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
# line=0
# for option in ('A....', 'B....','C....'):
#     oled.text(option, 0, line)
#     line+=8
# oled.text('A...',0,0,0,0)
# pdata=[0,] * 100
# for i in range(100):
#     pdata[i]=int((math.cos(i/5)+1)*20.0)
# oled.plot(1,pdata)
# oled.show()

# my_gps=gps.GPS()
# gps_uart=UART(2, pins=(gps.GPS_TX_PIN, gps.GPS_RX_PIN))
# while True:
#     line=gps_uart.readline()
#     if line!=None:
#         my_gps.update(line)
#         print(my_gps.latitude_string())
#         print(my_gps.longitude_string())
#         print(my_gps.compass_direction())

#from lib.door_sensor import DoorSensor
#ds=DoorSensor('G36', lambda x: print(x))

#from lib.tamper import Tamper
#tamp=Tamper('G39', lambda x: print(x))

#from lib.door_control import DoorControl
# dc=DoorControl('G0')

#from lib.bt_server import BTServer
#bt=BTServer('t1 g1', lambda x:print(x), ['12346'])

import machine
import utime
import pycom
from lib import settings
from lib.door_sensor import DoorSensor, DoorSensorEvent, MemoryDoorSensorEvent
from lib.tamper import Tamper
from lib.door_control import DoorControl
from lib.bt_server import BTServer
from lib import gps
from network import LoRa
from lib import axp202
import socket
import ubinascii
import struct

ds_events = []


def door_sensor_handler(open):
    ds_events.append(DoorSensorEvent(open))


def bt_cred_handler(valid):
    pass


def get_saved_events():
    saved_events = pycom.nvs_get('e_count')
    if saved_events is None:
        saved_events = 0
    mem_events = []
    for i in range(saved_events):
        mem_events.append(MemoryDoorSensorEvent(pycom.nvs_get('e'+str(i))))
    return mem_events


def save_events():
    if not ds_events:
        return
    my_gps = gps.GPS()
    gps_uart = machine.UART(2, pins=(gps.GPS_TX_PIN, gps.GPS_RX_PIN))
    while True:
        line = gps_uart.readline()
        if line != None:
            my_gps.update(line)
            if my_gps.time_since_fix() != 0:
                break
            
    time = my_gps.time_string()
    date = my_gps.date_string('s_dmy')
    time_split = time.split(':')
    hours = int(time_split[0])
    minutes = int(time_split[1])
    seconds = int(time_split[2])
    date_split = date.split('/')
    day = int(date_split[0])
    month = int(date_split[1])
    year = int(date_split[2])

    ts = utime.mktime((year, month, day, hours, minutes, seconds, None, None))
    ts_ticks = my_gps.fix_time
    saved_events = pycom.nvs_get('e_count')
    if saved_events is None:
        saved_events = 0
    for event in ds_events:
        pycom.nvs_set('e'+str(saved_events), event.to_memory(ts, ts_ticks))


def shutdown():
    pass


reason, detail = machine.wake_reason()

has_tamper = False
check_ds = False
enable_bt = False
send_events = False

if reason == machine.PIN_WAKE:
    if settings.TAMPER_SENSOR in detail:
        has_tamper = True
    if settings.DOOR_SENSOR in detail:
        check_ds = True
    if settings.BTN_PIN in detail:
        enable_bt = True
if reason == machine.RTC_WAKE:
    send_events = True

if not send_events and machine.remaining_sleep_time() < 15*60*1000:
    send_events = True

tamper = Tamper(settings.TAMPER_SENSOR, has_tamper)
door_sensor = DoorSensor(settings.DOOR_SENSOR, door_sensor_handler, check_ds)
door_control = DoorControl(settings.DOOR_RELAY)

lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
dev_addr = struct.unpack(">l", ubinascii.unhexlify('260B004D'))[0]
nwk_swkey = ubinascii.unhexlify('F049E015F2331D2A678C9C9C87DFD04B')
app_swkey = ubinascii.unhexlify('BDE7A8238E6354F64A8D10726E7A2B92')

if not tamper.active and not send_events and not enable_bt:
    save_events()
    shutdown()
