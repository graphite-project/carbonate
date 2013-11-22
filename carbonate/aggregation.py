#!/usr/bin/env python

import argparse
import fileinput
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
    except whisper.WhisperException, exc:
        logging.warning("%s failed (%s)" % (path, str(exc)))


def main():
    parser = argparse.ArgumentParser(
        description='Set aggregation for whisper-backed metrics this carbon ' +
                    'instance contains',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-f', '--metrics-file',
        default='-',
        help='File containing metric names and aggregation modes, or \'-\' ' +
             'to read from STDIN')

    parser.add_argument(
        '-d', '--storage-dir',
        default='/opt/graphite/storage/whisper',
        help='Whisper storage directory')

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    if args.metrics_file and args.metrics_file[0] != '-':
        fi = args.metrics_file
        metrics = map(lambda s: s.strip(), fileinput.input(fi))
    else:
        metrics = map(lambda s: s.strip(), fileinput.input([]))

    metrics_count = 0

    for metric in metrics:
        name, t = metric.strip().split('|')

        mode = AGGREGATION[t]
        if mode is not None:
            cname = name.replace('.', '/')
            path = os.path.join(args.storage_dir, cname + '.wsp')
            metrics_count = metrics_count + setAggregation(path, mode)

    logging.info('Successfully set aggregation mode for ' +
                 '%d of %d metrics' % (metrics_count, len(metrics)))
