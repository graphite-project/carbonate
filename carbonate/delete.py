import os
import logging
from shutil import move

from .util import metric_path


def deleteMetric(metric,
                 storage_dir='/opt/graphite/storage/whisper',
                 trash_dir="/opt/graphite/storage/whisper/trash"):
    old_metric = metric_path(metric, storage_dir)
    new_metric = metric_path(metric, trash_dir)

    if os.path.isfile(old_metric):
        try:
            os.makedirs(os.path.dirname(new_metric))
        except os.error:
            pass
        try:
            move(old_metric, new_metric)
        except IOError as e:
            logging.warn("Failed to delete %s! %s" % (old_metric, e))
