import struct
from enum import Enum
from typing import List, Tuple
from datetime import date


class Units(Enum):
    """
    Enum with all available physical units.
    """
    none = 0
    mbar = 1
    bar = 2
    psi = 3
    Pa = 4
    kPa = 5
    MPa = 6
    mmH2O = 7
    mH2O = 8
    ftH2O = 9
    inH2O = 10
    mmHg = 11

    degC = 32
    kelvin = 64
    degF = 96


class SystemRate(Enum):
    """
    Enum with the available system rates.
    """
    Rate_1_25_ms = 0
    Rate_2_5_ms = 1
    Rate_5_ms = 2
    Rate_10_ms = 3
    Rate_20_ms = 4
    Rate_40_ms = 5
    Rate_80_ms = 6
    Rate_160_ms = 7


class CarmenTypeplate(object):
    """
    Class to store typeplate information.
    """
    TypeplateType = None
    SerialNumber = None
    LRV_1 = None
    URV_1 = None
    xRV_1_Unit = None
    LRV_2 = None
    URV_2 = None
    xRV_2_Unit = None
    LRV_3 = None
    URV_3 = None
    xRV_3_Unit = None
    MWP = None
    MWP_Unit = None
    OPL = None
    OPL_Unit = None
    SystemRate = None
    DateModified = None

    def __str__(self) -> str:
        result = '---------- Typeplate Information ----------\n'
        result += 'TypeplateType: {}\n'.format(self.TypeplateType)
        result += ' SerialNumber: {}\n'.format(self.SerialNumber)
        result += '      DigOut1: {: 6.2f} ... {: 6.2f} {}\n'.format(self.LRV_1, self.URV_1, self.xRV_1_Unit)
        result += '      DigOut2: {: 6.2f} ... {: 6.2f} {}\n'.format(self.LRV_2, self.URV_2, self.xRV_2_Unit)
        result += '      DigOut3: {: 6.2f} ... {: 6.2f} {}\n'.format(self.LRV_3, self.URV_3, self.xRV_3_Unit)
        result += '          MWP: {: 6.2f} {}\n'.format(self.MWP, self.MWP_Unit)
        result += '          OPL: {: 6.2f} {}\n'.format(self.OPL, self.OPL_Unit)
        result += '   SystemRate: {}\n'.format(self.SystemRate)
        result += ' DateModified: {}\n'.format(self.DateModified)
        return result


def analyse_typeplate(buffer: List[int]) -> Tuple[bool, CarmenTypeplate]:
    """
    Analyses the typeplate buffer.

    :param buffer: Typeplate buffer.
    :return: True on success, else false.
    :return: Typeplate information.
    """
    def encode_short_IEEE(data: List[int]) -> float:
        """
        Encodes a short IEEE data to a floating point number.

        :param data: Data to encode. Maximum size is three.
        :return: The encoded floating point number.
        """
        integer = (data[0] | (data[1] << 8) | (data[2] << 16)) << 8
        return struct.unpack('!f', struct.pack('!I', integer))[0]

    info = CarmenTypeplate()
    # typeplate type
    info.TypeplateType = buffer[0]
    # serial number
    serial_number_buffer = [buffer[3], buffer[2], buffer[1],
                            buffer[7], buffer[6], buffer[5], buffer[4],
                            buffer[11], buffer[10], buffer[9], buffer[8]]
    info.SerialNumber = ''.join(chr(c) for c in serial_number_buffer)
    # dig1
    info.xRV_1_Unit = Units(buffer[12])
    info.LRV_1 = encode_short_IEEE(buffer[13:16])
    info.URV_1 = encode_short_IEEE(buffer[17:20])
    # dig2
    info.xRV_2_Unit = Units(buffer[20])
    info.LRV_2 = encode_short_IEEE(buffer[21:24])
    info.URV_2 = encode_short_IEEE(buffer[25:28])
    # dig3
    info.xRV_3_Unit = Units(buffer[28])
    info.LRV_3 = encode_short_IEEE(buffer[29:32])
    info.URV_3 = encode_short_IEEE(buffer[33:36])
    # MWP
    info.MWP_Unit = Units(buffer[36])
    info.MWP = encode_short_IEEE(buffer[37:40])
    # OPL
    info.OPL_Unit = Units(buffer[40])
    info.OPL = encode_short_IEEE(buffer[41:44])
    # system rate
    info.SystemRate = SystemRate(buffer[32] & 0x0007)
    # date modified
    date_buffer = (buffer[45] << 8) | buffer[44]
    year = (date_buffer & 0xFE00) >> 9
    month = (date_buffer & 0x01E0) >> 5
    day = (date_buffer & 0x001F)
    info.DateModified = date(year + 2000, month, day)
    return True, info
