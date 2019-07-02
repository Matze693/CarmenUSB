import logging
from unittest import TestCase
from unittest.mock import Mock

from carmen_communication import CommunicationCarmen
from carmen_utils import convert_digout
from crc16 import calculate_crc16

# disable logging output
logging.disable()


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

        self.assertEqual(0xCD9F, calculate_crc16([0x35, 0x85, 0x0C, 0x00, 0xCE, 0xFD, 0xCF, 0xF2, 0x00, 0x00, 0x80]))


class __TestCommunicationCarmen(TestCase):

    def setUp(self) -> None:
        self.serial = Mock()

    def test___init__(self):
        self.serial.is_open = True
        self.assertIsNotNone(CommunicationCarmen(self.serial))

        self.serial.is_open = False
        with self.assertRaises(IOError):
            _ = CommunicationCarmen(self.serial)

    def test__send_raw(self):
        data = [0] * 10
        c = CommunicationCarmen(self.serial)

        self.serial.write = Mock(side_effect=lambda x: len(x))
        self.assertTrue(c._send_raw(data))

        self.serial.write = Mock(side_effect=lambda x: len(x) + 1)
        self.assertFalse(c._send_raw(data))

    def test_send(self):
        cmd = 1
        data = [0] * 10
        c = CommunicationCarmen(self.serial)

        self.serial.write = Mock(side_effect=lambda x: len(x))
        self.assertTrue(c.send(cmd, data))

        self.serial.write = Mock(side_effect=lambda x: len(x) + 1)
        self.assertFalse(c.send(cmd, data))

    def test__receive_raw(self):
        data_length = 10
        c = CommunicationCarmen(self.serial)

        self.serial.read = Mock(side_effect=lambda x: [0] * x)
        success, data = c._receive_raw(data_length)
        self.assertTrue(success)
        self.assertEqual(data_length, len(data))

        self.serial.read = Mock(side_effect=lambda x: [0] * (x - 1))
        success, data = c._receive_raw(data_length)
        self.assertFalse(success)
        self.assertEqual(0, len(data))

    def test_receive(self):
        def side_effect(size):
            d = [0] * (size - 2)
            crc = calculate_crc16(d)
            return d + [crc & 0xFF, crc >> 8]

        data_length = 10
        c = CommunicationCarmen(self.serial)

        self.serial.read = Mock(side_effect=side_effect)
        success, data = c.receive(data_length + 2)
        self.assertTrue(success)
        self.assertEqual(data_length + 2, len(data))

        self.serial.read = Mock(side_effect=lambda x: [0] * x)
        success, data = c.receive(data_length)
        self.assertFalse(success)
        self.assertEqual(data_length, len(data))

        self.serial.read = Mock(side_effect=lambda x: [0] * (x - 1))
        success, data = c.receive(data_length)
        self.assertFalse(success)
        self.assertEqual(0, len(data))
