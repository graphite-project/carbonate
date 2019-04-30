import logging
import os
import whisper

AGGREGATION = {
    'last': 'last',
    'g': 'last',

    'sum': 'sum',
    'c': 'sum',
    'C': 'sum',

    'average': None,  # set by graphite
    'ms': None,       # set by graphite
    'h': None,        # set by graphite
    'internal': None
}


def setAggregation(path, mode):

    if not mode:
        return 0

    if not os.path.exists(path):
        return 0

    try:
        whisper.setAggregationMethod(path, mode)
        return 1
    except whisper.WhisperException as exc:
        logging.warning("%s failed (%s)" % (path, str(exc)))
