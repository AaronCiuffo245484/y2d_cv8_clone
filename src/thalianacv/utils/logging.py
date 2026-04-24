# thalianacv/utils/logging.py
"""Logging configuration and base exception for thalianacv.

This module provides a consistently configured logger factory and the base
exception class used across the package. All submodules should obtain their
logger via get_logger() rather than calling logging.getLogger() directly,
so that handler and formatter configuration is applied uniformly.

Example:
    >>> from thalianacv.utils.logging import get_logger, ThalianaCVError
    >>> logger = get_logger(__name__)
    >>> logger.info("Pipeline started")
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Return a consistently configured logger for the given name.

    Creates a logger with a stdout StreamHandler and a standard formatter
    if one has not already been attached. Safe to call multiple times with
    the same name — returns the existing logger on subsequent calls.

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        Configured logging.Logger instance.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting inference")
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

    return logger


class ThalianaCVError(Exception):
    """Base exception for all thalianacv errors.

    Raise this or a subclass whenever the package needs to signal a
    recoverable or unrecoverable error to the caller. Catching this base
    class is sufficient to handle any package-level exception.

    Example:
        >>> raise ThalianaCVError("Model weights not found at path: /tmp/model.h5")
    """
