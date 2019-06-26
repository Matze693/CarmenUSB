from unittest import TestCase

from carmen_utils import convert_digout
from crc16 import calculate_crc16


class __TestCarmenUtils(TestCase):

    def test_convert_digout(self):
        self.assertAlmostEqual(-0.170959, convert_digout(0xFA8782, 24, -1, 2), 5)
        self.assertAlmostEqual(23.925781, convert_digout(0xFEC0, 16, -20, 80, offset=25), 5)


class __TestCRC16(TestCase):

    def test_calculate_crc16(self):
        test_data = {0xA0: 0xFEC2,
                     0xA1: 0x7EC7,
                     0x5A: 0xFCDE,
                     0x35: 0xFDBC}

        for data, crc in test_data.items():
            if not isinstance(data, (tuple, list, set)):
                data = [data]
            self.assertEqual(crc, calculate_crc16(data))

        self.assertEqual(0xCD9F, calculate_crc16([0x35, 0x85, 0x0C, 0x00, 0xCE, 0xFD, 0xCF, 0xF2 , 0x00, 0x00, 0x80]))
