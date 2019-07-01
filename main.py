import logging
from serial import Serial

from carmen_communication import CommunicationCarmen
from carmen import Carmen

# constants
LOG_FILE = 'carmen.log'

# logging
console_logging = logging.StreamHandler()
console_logging.setLevel(logging.ERROR)

file_logging = logging.FileHandler(LOG_FILE)
file_logging.setLevel(logging.NOTSET)

logging.basicConfig(level=logging.NOTSET,
                    handlers=[console_logging, file_logging],
                    format='%(asctime)23s - %(levelname)8s - %(module)25s - %(funcName)25s - %(message)s'
                    )


ser = Serial('/dev/tty.usbserial-AH3Z6ZWF')
communication = CommunicationCarmen(ser)
carmen = Carmen(communication)

success, typeplate = carmen.read_typeplate()
if success:
    print('{}'.format(typeplate))
else:
    print('Cannot read typeplate!')

success, pressure, temperature, status = carmen.read_measurement()
if success:
    print('   Pressure: {: 8.4f} {}'.format(pressure, typeplate.xRV_1_Unit))
    print('Temperature: {: 8.4f} {}'.format(temperature, typeplate.xRV_2_Unit))
    print('     Status: 0x{:06X}'.format(status))
else:
    print('Cannot read measurement')
