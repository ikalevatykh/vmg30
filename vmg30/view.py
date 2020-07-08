"""This module contains the hand visualisation helper."""

from typing import Tuple

import numpy as np
from transforms3d.quaternions import axangle2quat, mat2quat

from panda3d_viewer import Viewer

from .data import GloveSample
from .model import HandModel

__all__ = ('HandView')


Vec4f = Tuple[(float, float, float, float)]
Mat4f = np.ndarray


class HandView:
    """Hand visualisation helper class."""

    def __init__(self,
                 viewer: Viewer,
                 hand_name: str = 'hand',
                 hand_model: HandModel = HandModel(),
                 thickness: float = 0.005):
        """Append the hand model to the viewer.

        Arguments:
            viewer {Viewer} -- viewer to attach the visualization

        Keyword Arguments:
            hand_name {str} -- hand name on the scene (default: {'hand'})
            hand_model {HandModel} -- hand model (default: {HandModel()})
            thickness {float} -- bones thickness (default: {0.005})
        """
        self._viewer = viewer
        self._name = hand_name
        self._model = hand_model
        self._clock = 0.0
        self._viewer.append_group(self._name)
        for link in self._model.links:
            frame = ((-link.length / 2.0, 0.0, 0.0), axangle2quat((0.0, -1.0, 0.0), np.pi / 2.0))
            self._viewer.append_capsule(self._name, link.name, thickness, link.length, frame)

    def set_color(self, color_rgba: Vec4f):
        """Change color of the hand model.

        Arguments:
            color_rgba {Vec4f} -- color components
        """
        for link in self._model.links:
            self._viewer.set_material(self._name, link.name, color_rgba)

    def update(self,
               sample: GloveSample,
               fixed_frame: Tuple[str, Mat4f] = None,
               rate_limit: float = 60.0) -> None:
        """Update link positions and pressures status.

        Arguments:
            sample {GloveSample} -- data from the glove

        Keyword Arguments:
            fixed_frame {Tuple(str, Mat4f)} --  known link frame transformation (default: {None})
            rate_limit {float} -- maximum update rate (Hz) (default: {60.0})
        """
        if sample.clock - self._clock > 1.0 / rate_limit or sample.clock < self._clock:
            frames = self._model.frames(sample, fixed_frame)
            tips = self._model.tip_names
            colors = {tip: _rgba(p) for tip, p in zip(tips, sample.pressures)}
            self._viewer.move_nodes('hand', frames)
            self._viewer.set_materials('hand', colors)
            self._clock = sample.clock

    def remove(self) -> None:
        """Remove the hand model from the viewer."""
        self._viewer.remove_group(self._name)


def _pose(matrix):
    return (matrix[:3, 3], mat2quat(matrix[:3, :3]))


def _rgba(pressure):
    return (1.0, 1.0 - pressure, 1.0 - pressure, 1.0)
