from typing import List, Tuple

from carmen_communication import CarmenCommunication


class Carmen(object):

    def __init__(self, communication: CarmenCommunication) -> None:
        self._communication = communication

    def _execute_simple_command(self, command: int, size: int) -> Tuple[bool, List[int]]:
        data = []
        success = self._communication.send(command)
        if success:
            success, data = self._communication.receive(size)
            if success:
                success = data[0] == command
                if not success:
                    data = []
                    print('!!!!! INVALID ANSWER !!!!!')
        return success, data

    def stop_dsp(self) -> Tuple[bool, List[int]]:
        return self._execute_simple_command(0xA0, 4)

    def continue_dsp(self) -> Tuple[bool, List[int]]:
        return self._execute_simple_command(0xA1, 4)

    def soft_reset(self) -> Tuple[bool, List[int]]:
        return self._execute_simple_command(0x5A, 4)

    def read_measurement_frame1(self) -> Tuple[bool, List[int]]:
        return self._execute_simple_command(0x35, 13)

    def read_eeprom(self, address: int, size: int = 1) -> Tuple[bool, List[int]]:
        command = 0x03
        data = []
        success = self._communication.send(command, [address >> 8, address & 0xFF, size])
        if success:
            success, data = self._communication.receive(size * 4 + 5)
            if success:
                success = data[0] == command and data[2] == size
                if not success:
                    data = []
                    print('!!!!! INVALID ANSWER !!!!!')
        return success, data

    def read_serial_number(self) -> Tuple[bool, str]:
        serial_number = ''
        success, _ = self.stop_dsp()
        if success:
            success, data = self.read_eeprom(0x0190, 3)
            if success:
                data = data[3:-2]
                buffer = [data[3], data[2], data[1],
                          data[7], data[6], data[5], data[4],
                          data[11], data[10], data[9], data[8]]
                serial_number = ''.join(chr(c) for c in buffer)
        _, _ = self.continue_dsp()

        return success, serial_number
