from serial import Serial

from carmen_communication import CarmenCommunication
from carmen import Carmen

ser = Serial('/dev/tty.usbserial-AH3Z6ZWF')
communication = CarmenCommunication(ser)
carmen = Carmen(communication)

success, typeplate = carmen.read_typeplate()
if success:
    print('{}'.format(typeplate))
else:
    print('Cannot read typeplate!')
