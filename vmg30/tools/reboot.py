"""This application reboot the glove."""

import argparse

from ..glove import Glove

parser = argparse.ArgumentParser('Reboot the glove')
parser.add_argument('--port', type=str, default='/dev/ttyUSB0', help='Glove serial port')

if __name__ == '__main__':
    args = parser.parse_args()
    glove = Glove(port=args.port)
    glove.reboot()
