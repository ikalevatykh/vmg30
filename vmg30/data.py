"""This module contains glove specific data types."""

from dataclasses import dataclass
from typing import Tuple


__all__ = ('IMUSample', 'GloveSample')


Vec3f = Tuple[float, float, float]
Vec4f = Tuple[float, float, float, float]
Vec5f = Tuple[float, float, float, float, float]


@dataclass(frozen=True)
class IMUSample:
    """IMU sample.

    angular_velocity {Vec3f} -- gyroscope measures (°/sec)
    acceleration {Vec3f} -- accelerometer measures (g)
    magnetic_field {Vec3f} -- magnetometer measures (μT)
    """

    angular_velocity: Vec3f
    acceleration: Vec3f
    magnetic_field: Vec3f


@dataclass(frozen=True)
class GloveSample:
    """Glove data sample.

    device_id {int} -- device identificator
    clock {float} -- internal glove time, sec
    wrist_imu {IMUSample} -- wrist IMU raw data
    hand_imu {IMUSample} -- hand IMU raw data
    wrist_quat {Vec4f} -- wrist quaternion x,y,z,w
    hand_quat {Vec4f} -- hand quaternion x,y,z,w
    pip_joints {Vec5f} -- proximal finger interphalangeal sensors values [0..1]
    dip_joints {Vec5f} -- distal finger interphalangeal sensors values [0..1]
    palm_arch {float} -- palm arch sensor value [0..1]
    thumb_cross_over {float} -- thumb cross over sensor value [0..1]
    abductions {Vec4f} -- abduction sensors values [0..1]
    pressures {Vec5f} -- tip pressure sensors values [0..1]
    battery_charge {float} -- battery charge [0..1]
    """

    device_id: int
    clock: int
    wrist_imu: IMUSample
    hand_imu: IMUSample
    wrist_quat: Vec4f
    hand_quat: Vec4f
    pip_joints: Vec5f
    dip_joints: Vec5f
    palm_arch: float
    thumb_cross_over: float
    abductions: Vec4f
    pressures: Vec5f
    battery_charge: float
