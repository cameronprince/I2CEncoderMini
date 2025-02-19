from machine import I2C
import struct
import time

# Encoder register definition
REG_GCONF = 0x00
REG_INTCONF = 0x01
REG_ESTATUS = 0x02
REG_CVALB4 = 0x03
REG_CVALB3 = 0x04
REG_CVALB2 = 0x05
REG_CVALB1 = 0x06
REG_CMAXB4 = 0x07
REG_CMAXB3 = 0x08
REG_CMAXB2 = 0x09
REG_CMAXB1 = 0x0A
REG_CMINB4 = 0x0B
REG_CMINB3 = 0x0C
REG_CMINB2 = 0x0D
REG_CMINB1 = 0x0E
REG_ISTEPB4 = 0x0F
REG_ISTEPB3 = 0x10
REG_ISTEPB2 = 0x11
REG_ISTEPB1 = 0x12
REG_DPPERIOD = 0x13
REG_ADDRESS = 0x14
REG_IDCODE = 0x70
REG_VERSION = 0x71
REG_I2CADDRESS = 0x72
REG_EEPROMS = 0x81

# Encoder configuration bit. Use with GCONF
WRAP_ENABLE = 0x01
WRAP_DISABLE = 0x00
DIRE_LEFT = 0x02
DIRE_RIGHT = 0x00
IPUP_ENABLE = 0x04
IPUP_DISABLE = 0x00
RMOD_X4 = 0x10
RMOD_X2 = 0x08
RMOD_X1 = 0x00
RESET = 0x80

# Encoder status bits and setting. Use with INTCONF for set and with ESTATUS for read the bits
PUSHR = 0x01
PUSHP = 0x02
PUSHD = 0x04
PUSHL = 0x08
RINC = 0x10
RDEC = 0x20
RMAX = 0x40
RMIN = 0x80

class i2cEncoderMiniLib:
    onButtonRelease = None
    onButtonPush = None
    onButtonDoublePush = None
    onButtonLongPush = None
    onIncrement = None
    onDecrement = None
    onChange = None
    onMax = None
    onMin = None
    onMinMax = None

    stat = 0
    gconf = 0

    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address

    def begin(self, conf):
        self.writeEncoder8(REG_GCONF, conf & 0xFF)
        self.gconf = conf

    def reset(self):
        self.writeEncoder8(REG_GCONF, RESET)

    def eventCaller(self, event):
        if event:
            event()

    def updateStatus(self):
        self.stat = self.readEncoder8(REG_ESTATUS)
        if self.stat == 0:
            return False

        if self.stat & PUSHR:
            self.eventCaller(self.onButtonRelease)
        if self.stat & PUSHP:
            self.eventCaller(self.onButtonPush)
        if self.stat & PUSHL:
            self.eventCaller(self.onButtonLongPush)
        if self.stat & PUSHD:
            self.eventCaller(self.onButtonDoublePush)
        if self.stat & RINC:
            self.eventCaller(self.onIncrement)
            self.eventCaller(self.onChange)
        if self.stat & RDEC:
            self.eventCaller(self.onDecrement)
            self.eventCaller(self.onChange)
        if self.stat & RMAX:
            self.eventCaller(self.onMax)
            self.eventCaller(self.onMinMax)
        if self.stat & RMIN:
            self.eventCaller(self.onMin)
            self.eventCaller(self.onMinMax)

        return True

    def readInterruptConfig(self):
        return self.readEncoder8(REG_INTCONF)

    def readStatus(self, status):
        return bool(self.stat & status)

    def readStatusRaw(self):
        return self.stat

    def readCounter32(self):
        return self.readEncoder32(REG_CVALB4)

    def readCounter16(self):
        return self.readEncoder16(REG_CVALB2)

    def readCounter8(self):
        return self.readEncoder8(REG_CVALB1)

    def readMax(self):
        return self.readEncoder32(REG_CMAXB4)

    def readMin(self):
        return self.readEncoder32(REG_CMINB4)

    def readStep(self):
        return self.readEncoder16(REG_ISTEPB4)

    def readDoublePushPeriod(self):
        return self.readEncoder8(REG_DPPERIOD)

    def readIDCode(self):
        return self.readEncoder8(REG_IDCODE)

    def readVersion(self):
        return self.readEncoder8(REG_VERSION)

    def readEEPROM(self, add):
        return self.readEncoder8(add)

    def writeInterruptConfig(self, interrupt):
        self.writeEncoder8(REG_INTCONF, interrupt)

    def autoconfigInterrupt(self):
        reg = 0
        if self.onButtonRelease:
            reg |= PUSHR
        if self.onButtonPush:
            reg |= PUSHP
        if self.onButtonDoublePush:
            reg |= PUSHD
        if self.onButtonLongPush:
            reg |= PUSHL
        if self.onIncrement:
            reg |= RINC
        if self.onDecrement:
            reg |= RDEC
        if self.onChange:
            reg |= RINC | RDEC
        if self.onMax:
            reg |= RMAX
        if self.onMin:
            reg |= RMIN
        if self.onMinMax:
            reg |= RMAX | RMIN
        self.writeEncoder8(REG_INTCONF, reg)

    def writeCounter(self, value):
        self.writeEncoder32(REG_CVALB4, value)

    def writeMax(self, max):
        self.writeEncoder32(REG_CMAXB4, max)

    def writeMin(self, min):
        self.writeEncoder32(REG_CMINB4, min)

    def writeStep(self, step):
        self.writeEncoder32(REG_ISTEPB4, step)

    def writeDoublePushPeriod(self, dperiod):
        self.writeEncoder8(REG_DPPERIOD, dperiod)

    def writeEEPROM(self, add, data):
        self.writeEncoder8(add, data)
        time.sleep(0.001)

    def writeEncoder8(self, reg, value):
        self.i2c.writeto_mem(self.address, reg, bytes([value]))

    def writeEncoder32(self, reg, value):
        data = struct.pack('>i', value)
        self.i2c.writeto_mem(self.address, reg, data)

    def readEncoder8(self, reg):
        return self.i2c.readfrom_mem(self.address, reg, 1)[0]

    def readEncoder16(self, reg):
        data = self.i2c.readfrom_mem(self.address, reg, 2)
        return struct.unpack('>h', data)[0]

    def readEncoder32(self, reg):
        data = self.i2c.readfrom_mem(self.address, reg, 4)
        return struct.unpack('>i', data)[0]