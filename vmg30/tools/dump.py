"""This application record data from the glove."""

import argparse
import pickle
from threading import Event, Thread

from ..glove import Glove

parser = argparse.ArgumentParser('Record glove data')
parser.add_argument('-p', '--port', type=str, default='/dev/ttyUSB0', help='Glove serial port')
parser.add_argument('-o', '--file', type=str, default='glove_data.pkl',
                    help='Path to output pickle file')


def record(port, out_file, stop_event):
    """Record samples.

    Args:
        port (str): serial device name
        out_file (str): output pickle file
        stop_event (Event): stop flag
    """
    samples = []
    with Glove(port) as glove:
        with glove.sampling():
            while not stop_event.is_set():
                samples.append(glove.next_sample())

    print(f'Saving {len(samples)} samples to "{out_file}"...')
    with open(out_file, 'wb') as pklfile:
        pickle.dump(samples, pklfile)
    print('Done.')


if __name__ == '__main__':
    args = parser.parse_args()
    stop = Event()
    task = Thread(target=record, args=(args.port, args.file, stop))
    task.start()
    input('Press Enter to exit.')
    stop.set()
    task.join()
