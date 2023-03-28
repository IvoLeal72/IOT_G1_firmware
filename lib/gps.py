import axp202
import micropyGPS

GPS_RX_PIN = 'G34'
GPS_TX_PIN = 'G12'


class GPS(micropyGPS.MicropyGPS):
    def __init__(self):
        super(location_formatting='dd')
        axp = axp202.PMU()
        axp.setLDO3Voltage(3300)
        axp.enablePower(axp202.AXP192_LDO3)

    def update(self, uart_line):
        for element in range(0, len(uart_line)):
            super().update(chr(uart_line[element]))
