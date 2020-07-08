"""This application visualise the hand skeleton using a real time or prerecorded glove data."""

import argparse
import pickle
import sys
from itertools import cycle
from typing import Iterable

try:
    from panda3d_viewer import Viewer, ViewerConfig
except ModuleNotFoundError:
    sys.exit('You need to install necessary dependencies: pip install panda3d_viewer')

from ..glove import Glove, GloveSample
from ..view import HandView

parser = argparse.ArgumentParser('Show hand skeleton')
parser.add_argument('-p', '--port', type=str, default='/dev/ttyUSB0', help='Glove serial port')
parser.add_argument('-f', '--file', type=str, default=None, help='Path to recorded pickle data')


def show(samples: Iterable[GloveSample]) -> None:
    """Visualise the hand's skeleton.

    Args:
        samples (Iterable[GloveSample]): data from glove sensors
    """
    config = ViewerConfig(scene_scale=10.0, show_grid=False)

    with Viewer(window_title='VMG30', config=config) as viewer:
        viewer.reset_camera(pos=(5, 5, 5), look_at=(0, 0, 0))
        hand_view = HandView(viewer)
        for sample in samples:
            hand_view.update(sample)


if __name__ == '__main__':
    args = parser.parse_args()

    if args.file:
        with open(args.file, 'rb') as f:
            list_samples = pickle.load(f)
        show(cycle(list_samples))

    elif args.port:
        with Glove(args.port) as glove:
            with glove.sampling() as iter_samples:
                show(iter_samples)
