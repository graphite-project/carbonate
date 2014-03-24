import os
from time import time

from .util import metric_path
from .fill import fill_archives


def deleteMetric(metric,
                 storage_dir='/opt/graphite/storage/whisper',
                 trash_dir="/opt/graphite/storage/whisper/trash"):
    oldMetric = metric_path(metric, storage_dir)
    newMetric = metric_path(metric, trash_dir)

    if os.path.isfile(oldMetric):
        try:
            os.makedirs(os.path.dirname(newMetric))
        except os.error:
            pass

        startFrom = time()
        fill_archives(oldMetric, newMetric, startFrom)
