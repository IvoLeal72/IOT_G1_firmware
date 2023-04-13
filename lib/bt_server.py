from lib.ble_util import BluetoothUuid
from network import Bluetooth

SERVICE_UUID = BluetoothUuid.to_bytes_le(
    '581f6305-2e3e-43c0-918f-daaba87370e0')
CHR_UUID = BluetoothUuid.to_bytes_le(
    'f41f77d9-5f18-4b03-92f0-c71a268b4b0a')


class BTServer:

    def __init__(self, name: str, callback=None, card_list=None):
        def conn_handler(bt):
            events = bt.events()
            if events & Bluetooth.CLIENT_DISCONNECTED:
                self.state = 'waiting'

        def chr1_handler(chr, data):
            events = chr.events()
            if events & Bluetooth.CHAR_WRITE_EVENT:
                if self.state in ('granted', 'denied'):
                    return
                card = data[1].decode('ASCII')
                valid = False
                if card in self.card_list:
                    valid = True
                self.state = 'granted' if valid else 'denied'
                if self.callback:
                    self.callback(valid)
                chr.value(self.state)

        self.state = 'waiting'
        if card_list is not None:
            self.card_list = card_list
        else:
            self.card_list = []
        self.callback = callback
        bt = Bluetooth()
        bt.set_advertisement(
            name=name, service_uuid=SERVICE_UUID)
        bt.callback(trigger=Bluetooth.CLIENT_DISCONNECTED,
                    handler=conn_handler)
        bt.advertise(True)
        srv1 = bt.service(uuid=SERVICE_UUID,
                          isprimary=True, nbr_chars=1)
        chr1 = srv1.characteristic(uuid=CHR_UUID)
        chr1.callback(trigger=(Bluetooth.CHAR_WRITE_EVENT),
                      handler=chr1_handler)

    def add_card(self, card):
        self.card_list.append(card)

    def remove_card(self, card) -> bool:
        try:
            self.card_list.remove(card)
            return True
        except ValueError:
            return False

    def update_card_list(self, card_list):
        self.card_list = card_list
