import logging
from serial import Serial

from carmen_communication import CarmenCommunication
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
communication = CarmenCommunication(ser)
carmen = Carmen(communication)

success, typeplate = carmen.read_typeplate()
if success:
    print('{}'.format(typeplate))
else:
    print('Cannot read typeplate!')
