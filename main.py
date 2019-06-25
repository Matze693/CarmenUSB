from serial import Serial

from carmen_communication import CarmenCommunication
from carmen import Carmen

ser = Serial('/dev/tty.usbserial-AH3Z6ZWF')
communication = CarmenCommunication(ser)
carmen = Carmen(communication)

success, serial_number = carmen.read_serial_number()
if success:
    print('Serial Number: {}'.format(serial_number))
else:
    print('Cannot read Serial Number!')
