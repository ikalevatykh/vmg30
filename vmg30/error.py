"""This module contains glove specific errors."""


__all__ = ('GloveError', 'GloveConnectionError', 'GloveTimeoutError', 'GlovePacketError')


class GloveError(Exception):
    """Bese glove error."""


class GloveConnectionError(GloveError):
    """Connection establishing error."""


class GloveTimeoutError(GloveError):
    """Connection timeout error."""


class GlovePacketError(GloveError):
    """Damaged packet error."""
