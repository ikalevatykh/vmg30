"""This module contains the virtual motion glove interface."""

import contextlib
import io
import ipaddress
import struct
import time
from typing import ContextManager, Sequence

import serial

from .data import GloveSample, IMUSample
from .error import GloveConnectionError, GloveError, GlovePacketError, GloveTimeoutError

__all__ = ('Glove')


class Glove:
    """Virtual motion glove (VMG30) interface."""

    def __init__(self, port: str = '/dev/ttyUSB0'):
        """Connect to the glove.

        Keyword Arguments:
            port {str} -- serial device name (default: {'/dev/ttyUSB0'})
        """
        try:
            self._conn = serial.Serial(
                port, baudrate=230400, timeout=2.0, write_timeout=2.0)
            self._buffer = b''

            self.stop_sampling()

            self._label = self._exec(0x11).decode().split('\0', 1)[0]
            self._firmware = '{}.{}.{}'.format(*self._exec(0x13))

            info = struct.unpack('>BBHIIIBB', self._exec(0x0C))
            self._device_type = info[0]
            self._device_id = info[2]
            self._address = ipaddress.ip_address(info[3])
            self._netmask = ipaddress.ip_address(info[4])
            self._gateway = ipaddress.ip_address(info[5])
            self._dhcp = info[6]

        except serial.SerialException as ex:
            raise GloveConnectionError(ex.strerror)
        except GloveTimeoutError:
            raise GloveConnectionError(
                f'The glove on "{port}" is not responding, ensure it is turned on.')

    @property
    def device_id(self) -> int:
        """Device identificator.

        Returns:
            int -- id
        """
        return self._device_id

    @device_id.setter
    def device_id(self, device_id: int) -> None:
        """Update device identificator.

        Arguments:
            device_id {int} -- new id
        """
        echo = self._exec(0x0D, struct.pack('>H', device_id))
        self._device_id = struct.unpack('>H', echo)

    @property
    def label(self) -> str:
        """Device string identificator.

        Returns:
            str -- label
        """
        return self._label

    @label.setter
    def label(self, label: str) -> None:
        """Update label.

        Arguments:
            label {str} -- new label
        """
        echo = self._exec(0x11, struct.pack(
            '16s', label.ljust(16, '\0').encode()))
        self._label = echo.decode().split('\0', 1)[0]

    @property
    def firmware(self) -> str:
        """Firmware version.

        Returns:
            str -- version string x.y.z
        """
        return self._firmware

    @property
    def has_wifi_module(self) -> bool:
        """Device has WIFI module.

        Returns:
            bool -- True if has module
        """
        return self._device_type == 0x02

    def calibration(self):
        """Start self calibration of the dataglove orientation module.

        Yields:
            int -- calibration status (from 0 to 100)
        """
        self._send(0x31)
        stage = 0
        while stage != 100:
            stage, = self._recv(0x31)
            if stage == 255:
                raise GloveError('IMU calibration failed')
            yield stage

    def start_sampling(self, raw=False) -> None:
        """Start data sampling.

        Keyword Arguments:
            raw {bool} -- return IMU data instead of quaternions (default: {False})
        """
        self._send(0x0A, bytes([0x03 if raw else 0x01]))

    def stop_sampling(self) -> None:
        """Stop data sampling."""
        self._send(0x0A, bytes([0x00]))
        time.sleep(0.1)
        self._send(0x0B)
        time.sleep(0.1)

    def next_sample(self) -> GloveSample:
        """Receive next sample."""
        data = io.BytesIO(self._recv(0x0A))
        sample_type, device_id, clock = struct.unpack('>BHI', data.read(7))
        raw = sample_type == 0x03

        if raw:
            values = struct.unpack('>' + 'h' * 18, data.read(36))
            wrist_imu = IMUSample(
                angular_velocity=(*[v / 0x8000 * 10 for v in values[0:3]],),
                acceleration=(*[v / 0x8000 * 4 for v in values[3:6]],),
                magnetic_field=(*values[6:9],))
            hand_imu = IMUSample(
                angular_velocity=(*[v / 0x8000 * 10 for v in values[9:12]],),
                acceleration=(*[v / 0x8000 * 4 for v in values[12:15]],),
                magnetic_field=(*values[15:18],))
        else:
            values = struct.unpack('>' + 'i' * 8, data.read(32))
            wrist_quat = (*[v / 0x10000 for v in values[:4]],)
            hand_quat = (*[v / 0x10000 for v in values[4:]],)

        values = struct.unpack('>' + 'H' * 24, data.read(48))
        return GloveSample(
            device_id=device_id,
            clock=clock / 1000,
            wrist_imu=wrist_imu if raw else None,
            hand_imu=hand_imu if raw else None,
            wrist_quat=wrist_quat if not raw else None,
            hand_quat=hand_quat if not raw else None,
            pip_joints=(*[v / 1000 for v in values[1:10:2]],),
            dip_joints=(*[v / 1000 for v in values[0:10:2]],),
            palm_arch=values[10] / 1000,
            thumb_cross_over=values[12] / 1000,
            pressures=(*[1.0 - v / 999 for v in values[14:19]],),
            abductions=(*[v / 1000 for v in values[19:23]],),
            battery_charge=values[23] / 1000)

    @contextlib.contextmanager
    def sampling(self, raw=False) -> ContextManager:
        """"Start data sampling.

        Keyword Arguments:
            raw {bool} -- return IMU data instead of quaternions (default: {False})
        """
        def _sample_iterator():
            while True:
                yield self.next_sample()

        self.start_sampling(raw)
        yield _sample_iterator()
        self.stop_sampling()

    def set_vibro_feedback(self, levels: Sequence[float]) -> None:
        """Set vibrotactile feedback.

        Arguments:
            levels {Sequence[float]} -- vibro intensity on tips of the fingers [0..1]
        """
        values = [int(min(max(i, 0.0), 1.0) * 140 + 110) for i in levels]
        self._send(0x60, bytes([values] + [0x00]))

    def reboot(self) -> None:
        """Reboot the dataglove."""
        self._send(0x0E)

    def turn_off(self) -> None:
        """Turn off the dataglove."""
        self._send(0x40)
        self.disconnect()

    def disconnect(self) -> None:
        """Close connection."""
        self._conn.close()

    def __enter__(self):
        """Enter context guard.

        Returns:
            Glove -- this glove
        """
        return self

    def __exit__(self, *args, **kwargs):
        """Disconnect the glove at context guard exit."""
        self.disconnect()

    def __repr__(self):
        """String representation.

        Returns:
            str -- string representing the glove
        """
        return f'Glove(port="{self._conn.name}", id={self.device_id}, label="{self.label}")'

    def _read(self, size=1) -> bytes:
        if size > len(self._buffer):
            self._buffer += self._conn.read(
                max(size - len(self._buffer), self._conn.in_waiting))
            if size > len(self._buffer):
                raise GloveTimeoutError('Read timeout')
        data, self._buffer = self._buffer[:size], self._buffer[size:]
        return data

    def _recv(self, package_type: int) -> bytes:
        while True:
            package = self._read(1)
            if package[0] == 0x24:
                package += self._read(2)
                package += self._read(package[2] - 2)
                crc, end = self._read(2)
                if crc != sum(package) % 256 or end != 0x23:
                    raise GlovePacketError()
                if package[1] == package_type:
                    package_data = package[3:]
                    return package_data

    def _send(self, package_type: int, package_data: bytes = None) -> int:
        try:
            package = bytes([0x24, package_type])
            if package_data is not None:
                package += bytes([len(package_data) + 2]) + package_data
            else:
                package += bytes([2])
            crc = sum(package) % 256
            return self._conn.write(package + bytes([crc, 0x23]))
        except serial.SerialTimeoutException:
            raise GloveTimeoutError('Write timeout')

    def _exec(self, package_type: int, package_data: bytes = None) -> bytes:
        self._send(package_type, package_data)
        return self._recv(package_type)
