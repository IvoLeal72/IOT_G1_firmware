from lib import gps
import machine

# my_gps = gps.GPS()
# gps_uart = machine.UART(2, pins=(gps.GPS_TX_PIN, gps.GPS_RX_PIN))
# while True:
#     line = gps_uart.readline()
#     if line != None:
#         my_gps.update(line)
#         print(line)
#         print(my_gps.satellites_visible())
#         print(my_gps.time_string())
#         print(my_gps.latitude_string())
#         print(my_gps.longitude_string())
#         print()
#         if my_gps.valid:
#             break

# time = my_gps.time_string()
# date = my_gps.date_string('s_dmy')
# time_split = time.split(':')
# hours = int(time_split[0])
# minutes = int(time_split[1])
# seconds = int(time_split[2])
# date_split = date.split('/')
# day = int(date_split[0])
# month = int(date_split[1])
# year = int(date_split[2])

# print(time)
# print(time_split)
# print(hours)
# print(minutes)
# print(seconds)
# print(date)
# print(date_split)
# print(day)
# print(month)
# print(year)
