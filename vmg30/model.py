"""This module contains kinematic model of a hand compatible with the glove."""

from dataclasses import dataclass
from typing import Dict, Sequence, Tuple

import numpy as np
from transforms3d import affines, euler

from .data import GloveSample

__all__ = ('HandModel')


Vec3f = Tuple[float, float, float]
Mat4f = np.ndarray


@dataclass(frozen=True)
class Link:
    """Link data helper class."""

    name: str
    parent: str
    euler: Vec3f
    length: float


class HandModel:
    """Kinematic hand model to interpret the glove sensor data."""

    def __init__(self):
        """Initialize the model."""
        self._links = (
            Link('wrist', 'root', (0.0, 0.0, 0.0), 0.060),
            Link('hand', 'wrist', (0.0, 0.0, 0.0), 0.030),
            Link('thumb0', 'hand', (0.0, 5.0, 115.0), 0.045),
            Link('thumb1', 'thumb0', (0.0, 0.0, -70.0), 0.060),
            Link('thumb2', 'thumb1', (0.0, 0.0, 0.0), 0.028),
            Link('thumb3', 'thumb2', (0.0, 0.0, 0.0), 0.025),
            Link('index0', 'hand', (0.0, 0.0, 15.0), 0.090),
            Link('index1', 'index0', (0.0, 0.0, 5.0), 0.040),
            Link('index2', 'index1', (0.0, 0.0, 0.0), 0.028),
            Link('index3', 'index2', (0.0, 0.0, 0.0), 0.020),
            Link('middle0', 'hand', (0.0, 0.0, 0.0), 0.085),
            Link('middle1', 'middle0', (0.0, 0.0, 0.0), 0.035),
            Link('middle2', 'middle1', (0.0, 0.0, 0.0), 0.032),
            Link('middle3', 'middle2', (0.0, 0.0, 0.0), 0.025),
            Link('ring0', 'hand', (0.0, 0.0, -15.0), 0.085),
            Link('ring1', 'ring0', (0.0, 0.0, -5.0), 0.030),
            Link('ring2', 'ring1', (0.0, 0.0, 0.0), 0.028),
            Link('ring3', 'ring2', (0.0, 0.0, 0.0), 0.025),
            Link('little0', 'hand', (0.0, 0.0, -35.0), 0.075),
            Link('little1', 'little0', (0.0, 0.0, -5.0), 0.030),
            Link('little2', 'little1', (0.0, 0.0, 0.0), 0.025),
            Link('little3', 'little2', (0.0, 0.0, 0.0), 0.017),
        )

    @property
    def links(self) -> Sequence[Link]:
        """Get links of the hand model.

        Returns:
            Sequence[Link] -- list of links
        """
        return self._links

    @property
    def tip_names(self) -> Sequence[str]:
        """Get names of tip links.

        Returns:
            Sequence[str] -- list of names
        """
        return ['thumb3', 'index3', 'middle3', 'ring3', 'little3']

    def angles(self, sample: GloveSample) -> Dict[str, Vec3f]:
        """Convert sensor data to euler angles in joints.

        Arguments:
            sample {GloveSample} -- data from the glove

        Returns:
            Dict[str, Vec3f] -- euler angles (in degrees) by link name
        """
        # pylint: disable=no-self-use
        w_roll, w_pitch, w_yaw = np.rad2deg(euler.quat2euler(sample.wrist_quat, 'sxyz'))
        _, h_pitch, _ = np.rad2deg(euler.quat2euler(sample.hand_quat, 'sxyz'))
        return {
            'wrist': (-w_roll, -w_pitch, w_yaw),
            'hand': (0.0, w_pitch-h_pitch, 0.0),
            'thumb0': (0.0, 57.5 * (sample.palm_arch + sample.thumb_cross_over), 0.0),
            'thumb1': (0.0, 20.0 * sample.pip_joints[0], -25.0 * sample.abductions[0]),
            'thumb2': (0.0, 30.0 * sample.pip_joints[0], 0.0),
            'thumb3': (0.0, 85.0 * sample.dip_joints[0], 0.0),
            'index0': (0.0, 0.0, 0.0),
            'index1': (0.0, 70.0 * sample.pip_joints[1], -25.0 * sample.abductions[1]),
            'index2': (0.0, 100.0 * sample.dip_joints[1], 0.0),
            'index3': (0.0, 30.0 * sample.dip_joints[1], 0.0),
            'middle0': (0.0, 0.0, 0.0),
            'middle1': (0.0, 70.0 * sample.pip_joints[2], 0.0),
            'middle2': (0.0, 100.0 * sample.dip_joints[2], 0.0),
            'middle3': (0.0, 30.0 * sample.dip_joints[2], 0.0),
            'ring0': (0.0, 0.0, 0.0),
            'ring1': (0.0, 70.0 * sample.pip_joints[3], 25.0 * sample.abductions[2]),
            'ring2': (0.0, 100.0 * sample.dip_joints[3], 0.0),
            'ring3': (0.0, 30.0 * sample.dip_joints[3], 0.0),
            'little0': (0.0, 0.0, 0.0),
            'little1': (0.0, 70.0 * sample.pip_joints[4], 25.0 * sample.abductions[3]),
            'little2': (0.0, 100.0 * sample.dip_joints[4], 0.0),
            'little3': (0.0, 30.0 * sample.dip_joints[4], 0.0),
        }

    def frames(self,
               sample: GloveSample,
               fixed_frame: Tuple[str, Mat4f] = None) -> Dict[str, Mat4f]:
        """Convert sensor data to link frames.

        Arguments:
            sample {GloveSample} -- data from the glove

        Keyword Arguments:
            fixed_frame {Tuple[str, Mat4f]} -- known link frame transformation (default: {None})

        Returns:
            Dict[str, Mat4f] -- dict of link frame transformation matrix (4x4) by link name
        """
        joints = self.angles(sample)
        frames = {'root': np.eye(4)}
        for link in self._links:
            rotate = euler.euler2mat(*np.deg2rad(np.add(link.euler, joints[link.name])), 'sxyz')
            frame = affines.compose(np.dot(rotate, [link.length, 0, 0]), rotate, [1, 1, 1])
            frames[link.name] = np.dot(frames[link.parent], frame)

        if fixed_frame is not None:
            link_name, frame = fixed_frame
            shift = np.dot(frame, np.linalg.inv(frames[link_name]))
            for link_name in frames:
                frames[link_name] = np.dot(shift, frames[link_name])

        return frames

    def points(self,
               sample: GloveSample,
               fixed_frame: Tuple[str, Mat4f] = None) -> Dict[str, Vec3f]:
        """Convert sensor data to link positions.

        Arguments:
            sample {GloveSample} -- data from the glove

        Keyword Arguments:
            fixed_frame {Tuple[str, Mat4f]} -- known frame transformation (default: {None})

        Returns:
            Dict[str, Vec3f] -- dict of link frame position by link name
        """
        frames = self.frames(sample, fixed_frame)
        points = {link: (*m44[:3, 3],) for link, m44 in frames.items()}

        return points
