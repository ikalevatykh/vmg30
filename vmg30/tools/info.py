"""This application show information about of the glove."""

import argparse

from ..glove import Glove
from ..error import GloveError

parser = argparse.ArgumentParser('Glove info')
parser.add_argument('--port', type=str, default='/dev/ttyUSB0', help='Glove serial port')


def info(port):
    """Show info.

    Args:
        port (str): serial device name
    """
    try:
        with Glove(port=args.port) as glove:
            print(f'Device "{port}"')
            print(f'- id: {glove.device_id}')
            print(f'- label: "{glove.label}"')
            print(f'- firmware: {glove.firmware}')
            print(f'- has WIFI module: {glove.has_wifi_module}')
    except GloveError as ex:
        print(ex)


if __name__ == '__main__':
    args = parser.parse_args()
    info(args.port)
