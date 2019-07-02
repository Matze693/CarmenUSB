import logging
from typing import List, Tuple

from serial import Serial

from crc16 import calculate_crc16


class CommunicationCarmen(object):
    """
    Simple class to handle the communication to the Carmen sensor.
    """

    def __init__(self, serial: Serial, baudrate: int = 57600) -> None:
        """
        Initializes the communication.

        :param serial: Reference to a serial connection.
        :param baudrate: Connection baudrate. Default is 57600.
        """
        self.__serial = serial

        # close if serial is open to set baudrate and timeout
        if self.__serial.is_open:
            self.__serial.close()
        self.__serial.baudrate = baudrate
        self.__serial.timeout = 1

        self.__serial.open()

        # check if serial is open
        if not self.__serial.is_open:
            raise IOError('Cannot open serial "{}"'.format(serial.name))

        logging.info('serial "{}" is open'.format(self.__serial.name))

    def __del__(self) -> None:
        """
        Finalizes the communication.
        """
        self.__serial.close()

    def _send_raw(self, data: List[int]) -> bool:
        """
        Sends the given data to the Carmen sensor.

        :param data: Date to send.
        :return: True on success, else false.
        """
        logging.info('send -> {}'.format(' '.join('0x{:02X}'.format(x) for x in data)))
        written_bytes_len = self.__serial.write(bytes(data))
        return written_bytes_len == len(data)

    def send(self, command: int, data: List[int] = None) -> bool:
        """
        Sends a command with the given data to the Carmen sensor.
        The CRC16 is calculated and appended.

        :param command: Command to send.
        :param data: Data to send if necessary. Default ist None.
        :return: True on success, else false.
        """
        if data is None:
            data = []
        crc = calculate_crc16([command] + data)
        return self._send_raw([command] + data + [crc & 0xFF, crc >> 8])

    def _receive_raw(self, size: int) -> Tuple[bool, List[int]]:
        """
        Receives data from the Carmen sensor.

        :param size: Number of bytes to receive.
        :return: True on success, else false.
        :return: The received data.
        """
        data = list(self.__serial.read(size))
        logging.info('read <- {}'.format(' '.join('0x{:02X}'.format(x) for x in data)))
        success = size == len(data)
        if not success:
            logging.error('read timeout after {} s'.format(self.__serial.timeout))
            data = []
        return success, data

    def receive(self, size: int) -> Tuple[bool, List[int]]:
        """
        Receives data from the Carmen sensor.
        The CRC16 is checked.

        :param size:
        :return: True on success, else false.
        :return: The received data.
        """
        success, data = self._receive_raw(size)
        if success:
            # check crc
            success = calculate_crc16(data[:-2]) == (data[-2] + (data[-1] << 8))
            if not success:
                logging.error('invalid crc')
        return success, data
