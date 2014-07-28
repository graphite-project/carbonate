import time
import os

import whisper


def _limit(hours):
    return time.time() - (hours * 60 * 60)


def data(path, hours):
    """
    Does the metric at ``path`` have any whisper data newer than ``hours``?
    """
    _data = whisper.fetch(path, _limit(hours))
    return all(x is None for x in _data[-1])


def stat(path, hours):
    """
    Has the metric file at ``path`` been modified since ``hours`` ago?
    """
    return os.stat(path).st_mtime < _limit(hours)
