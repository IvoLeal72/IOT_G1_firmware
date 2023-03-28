from network import Bluetooth
from machine import Pin

i=250
led=Pin('G4', mode=Pin.OUT)
led(1)

def conn_cb(chr):
    events = chr.events()
    if events & Bluetooth.CLIENT_CONNECTED:
        print('client connected')
    elif events & Bluetooth.CLIENT_DISCONNECTED:
        led(1)
        print('client disconnected')

def chr1_handler(chr, data):
    global i
    events = chr.events()
    print(data)
    if events & Bluetooth.CHAR_READ_EVENT:
        chr.value(i)
        print("transmitted :", hex(i))
        i=i+1
    if events & Bluetooth.CHAR_WRITE_EVENT:
        i=int.from_bytes(data[1], 'little')
        print("Received: ", hex(i))
        if i==0x72:
            led(0)
            

def main():
    bluetooth = Bluetooth()
    bluetooth.set_advertisement(name='G1 t-beam', service_uuid=0xec00)

    bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=conn_cb)
    bluetooth.advertise(True)

    srv1 = bluetooth.service(uuid=0xec00, isprimary=True, nbr_chars=1)

    chr1 = srv1.characteristic(uuid=0xec0e, value='my_value') 

    chr1.callback(trigger=(Bluetooth.CHAR_READ_EVENT | Bluetooth.CHAR_WRITE_EVENT), handler=chr1_handler)

if __name__=='__main__':
    main()