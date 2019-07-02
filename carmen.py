import logging
from typing import List, Tuple

from carmen_communication import CommunicationCarmen
from carmen_utils import CarmenTypeplate, analyse_typeplate, convert_digout


class Carmen(object):
    """
    Simple class to handle the Carmen sensor functions.
    """

    def __init__(self, communication: CommunicationCarmen) -> None:
        """
        Initializes a instance of Carmen.

        :param communication: Communication for the Carmen sensor.
        """
        self._communication = communication
        self._typeplate = None

    def _execute_simple_command(self, command: int, size: int) -> Tuple[bool, List[int]]:
        """
        Executes a simple command.

        :param command: Command to execute.
        :param size: Response size for the given command.
        :return: True on success, else false.
        :return: The received data.
        """
        response = []
        success = self._communication.send(command)
        if success:
            success, response = self._communication.receive(size)
            if success:
                success = response[0] == command
                if not success:
                    response = []
                    logging.error('invalid answer, wrong command')
        return success, response

    def stop_dsp(self) -> Tuple[bool, List[int]]:
        """
        Executes the command "Stop DSP".

        :return: True on success, else false.
        :return: The received data.
        """
        logging.info('execute command "Stop DSP"')
        return self._execute_simple_command(0xA0, 4)

    def continue_dsp(self) -> Tuple[bool, List[int]]:
        """
        Executes the command "Continue DSP".

        :return: True on success, else false.
        :return: The received data.
        """
        logging.info('execute command "Continue DSP"')
        return self._execute_simple_command(0xA1, 4)

    def soft_reset(self) -> Tuple[bool, List[int]]:
        """
        Executes the command "Soft Reset".

        :return: True on success, else false.
        :return: The received data.
        """
        logging.info('execute command "Soft Reset"')
        return self._execute_simple_command(0x5A, 4)

    def read_measurement_frame1(self) -> Tuple[bool, List[int]]:
        """
        Executes the command "Read Measurement Frame1".

        :return: True on success, else false.
        :return: The received data.
        """
        logging.info('execute command "Read Measurement Frame1"')
        return self._execute_simple_command(0x35, 13)

    def read_eeprom(self, address: int, size: int = 1) -> Tuple[bool, List[int]]:
        """
        Executes the command "Read EEPROM".

        :param address: Start address to read from EEPROM.
        :param size: Block size to read.
        :return: True on success, else false.
        :return: The received data.
        """
        logging.info('execute command "Read EEPROM"')
        command = 0x03
        response = []
        success = self._communication.send(command, [address >> 8, address & 0xFF, size])
        if success:
            success, response = self._communication.receive(size * 4 + 5)
            if success:
                success = response[0] == command and response[2] == size
                if not success:
                    response = []
                    logging.error('invalid answer, wrong command or invalid size')
        return success, response

    def read_typeplate(self) -> Tuple[bool, CarmenTypeplate]:
        """
        Reads the typeplate information.

        :return: True on success, else false.
        :return: Typeplate information.
        """
        typeplate = CarmenTypeplate()
        success, _ = self.stop_dsp()
        if success:
            success, response = self.read_eeprom(0x0190, 12)
            if success:
                success, typeplate = analyse_typeplate(response[3:-2])
                if success:
                    self._typeplate = typeplate
        _, _ = self.continue_dsp()
        return success, typeplate

    def read_measurement(self) -> Tuple[bool, float, float, int]:
        """
        Reads a measurement (pressure, temperature, status) from the Carmen sensor.

        :return: True on success, else false.
        :return: Pressure value.
        :return: Temperature value.
        :return: Actual status.
        """
        pressure = 0.0
        temperature = 0.0
        status = 0xFFFFFF
        success = True
        if self._typeplate is None:
            success, _ = self.read_typeplate()
        if success:
            success, data = self.read_measurement_frame1()
            if success:
                pressure_value = data[1] | (data[2] << 8) | (data[3] << 16)
                pressure = convert_digout(pressure_value, 24, self._typeplate.LRV_1, self._typeplate.URV_1)
                temperature_value = data[4] | (data[5] << 8)
                temperature = convert_digout(temperature_value, 16, self._typeplate.LRV_2, self._typeplate.URV_2, 25)
                status = data[8] | (data[9] << 8) | (data[10] << 16)
        return success, pressure, temperature, status
