import logging
from typing import List, Tuple
from unittest import TestCase
from unittest.mock import Mock

from carmen import Carmen
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

    @classmethod
    def setUpClass(cls) -> None:
        cls.serial = Mock()

    def setUp(self) -> None:
        self.serial.is_open = True
        self.serial.write = Mock(side_effect=lambda x: len(x))
        self.serial.read = Mock(side_effect=lambda x: [0] * x)

    def test___init__(self):
        self.assertIsNotNone(CommunicationCarmen(self.serial))

        self.serial.is_open = False
        with self.assertRaises(IOError):
            _ = CommunicationCarmen(self.serial)

    def test__send_raw(self):
        data = [0] * 10
        c = CommunicationCarmen(self.serial)

        self.assertTrue(c._send_raw(data))

        self.serial.write = Mock(side_effect=lambda x: len(x) + 1)
        self.assertFalse(c._send_raw(data))

    def test_send(self):
        cmd = 1
        data = [0] * 10
        c = CommunicationCarmen(self.serial)

        self.assertTrue(c.send(cmd, data))

        self.serial.write = Mock(side_effect=lambda x: len(x) + 1)
        self.assertFalse(c.send(cmd, data))

    def test__receive_raw(self):
        data_length = 10
        c = CommunicationCarmen(self.serial)

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


class __TestCarmen(TestCase):
    __valid_responses = {0xA0: [0xA0, 0x80, 0x04, 0xC3],
                         0xA1: [0xA1, 0x80, 0x07, 0x45],
                         0x5A: [0x5A, 0x80, 0x0B, 0x5F],
                         0x35: [0x35, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x80, 0x6E, 0x5F]}

    def mock_send(self, command: int, data: List[int] = None) -> bool:
        self.__received_command = command
        self.__received_data = data
        return True

    def mock_receive(self, _: int) -> Tuple[bool, List[int]]:
        data = None
        if self.__received_data:
            if self.__received_command == 0x03:
                data = [0x03, 0x80, self.__received_data[2]] + [0x00] * self.__received_data[2] * 4
                crc = calculate_crc16(data)
                data += [crc & 0xFF, crc >> 8]
        else:
            data = self.__valid_responses[self.__received_command]
        return True, data

    def mock_receive_invalid(self, size: int) -> Tuple[bool, List[int]]:
        return True, [-0x01] * size

    @classmethod
    def setUpClass(cls) -> None:
        cls.communication = Mock()

    def setUp(self) -> None:
        self.communication.send = Mock(side_effect=self.mock_send)
        self.communication.receive = Mock(side_effect=self.mock_receive)

    def test__execute_simple_command(self):
        c = Carmen(self.communication)

        success, data = c._execute_simple_command(0xA0, 4)
        self.assertTrue(success)
        self.assertEqual(4, len(data))

        self.communication.receive = Mock(side_effect=self.mock_receive_invalid)
        success, data = c._execute_simple_command(0xA0, 4)
        self.assertFalse(success)
        self.assertEqual(0, len(data))

    def test_stop_dsp(self):
        c = Carmen(self.communication)

        success, data = c.stop_dsp()
        self.assertTrue(success)
        self.assertEqual(4, len(data))

        self.communication.receive = Mock(side_effect=self.mock_receive_invalid)
        success, data = c.stop_dsp()
        self.assertFalse(success)
        self.assertEqual(0, len(data))

    def test_continue_dsp(self):
        c = Carmen(self.communication)

        success, data = c.continue_dsp()
        self.assertTrue(success)
        self.assertEqual(4, len(data))

        self.communication.receive = Mock(side_effect=self.mock_receive_invalid)
        success, data = c.continue_dsp()
        self.assertFalse(success)
        self.assertEqual(0, len(data))

    def test_soft_reset(self):
        c = Carmen(self.communication)

        success, data = c.soft_reset()
        self.assertTrue(success)
        self.assertEqual(4, len(data))

        self.communication.receive = Mock(side_effect=self.mock_receive_invalid)
        success, data = c.soft_reset()
        self.assertFalse(success)
        self.assertEqual(0, len(data))

    def test_read_measurement_frame1(self):
        c = Carmen(self.communication)

        success, data = c.read_measurement_frame1()
        self.assertTrue(success)
        self.assertEqual(13, len(data))

        self.communication.receive = Mock(side_effect=self.mock_receive_invalid)
        success, data = c.read_measurement_frame1()
        self.assertFalse(success)
        self.assertEqual(0, len(data))

    def test_read_eeprom(self):
        start = 0x123
        size = 2
        c = Carmen(self.communication)

        success, data = c.read_eeprom(start, size)
        self.assertTrue(success)
        self.assertEqual(5 + 4 * size, len(data))

        self.communication.receive = Mock(side_effect=self.mock_receive_invalid)
        success, data = c.read_eeprom(start, size)
        self.assertFalse(success)
        self.assertEqual(0, len(data))
