import time
import os

import whisper


def _to_sec(hours):
    return hours * 60 * 60


def data(path, hours, offset=0):
    """
    Does the metric at ``path`` have any whisper data newer than ``hours``?

    If ``offset`` is not None, view the ``hours`` prior to ``offset`` hours
    ago, instead of from right now.
    """
    now = time.time()
    end = now - _to_sec(offset)  # Will default to now
    start = end - _to_sec(hours)
    _data = whisper.fetch(path, start, end)
    return all(x is None for x in _data[-1])


def stat(path, hours, offset=None):
    """
    Has the metric file at ``path`` been modified since ``hours`` ago?

    .. note::
        ``offset`` is only for compatibility with ``data()`` and is ignored.
    """
    return os.stat(path).st_mtime < (time.time() - _to_sec(hours))
