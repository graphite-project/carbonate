# original work: https://github.com/graphite-project/whisper/issues/22

# whisper-fill: unlike whisper-merge, don't overwrite data that's
# already present in the target file, but instead, only add the missing
# data (e.g. where the gaps in the target file are).  Because no values
# are overwritten, no data or precision gets lost.  Also, unlike
# whisper-merge, try to take the highest-precision archive to provide
# the data, instead of the one with the largest retention.
# Using this script, reconciliation between two replica instances can be
# performed by whisper-fill-ing the data of the other replica with the
# data that exists locally, without introducing the quite remarkable
# gaps that whisper-merge leaves behind (filling a higher precision
# archive with data from a lower precision one)

# Work performed by author while working at Booking.com.

from whisper import info, fetch, update_many

try:
    from whisper import operator
    HAS_OPERATOR = True
except ImportError:
    HAS_OPERATOR = False

import itertools
import time


def itemgetter(*items):
    if HAS_OPERATOR:
        return operator.itemgetter(*items)
    else:
        if len(items) == 1:
            item = items[0]

            def g(obj):
                return obj[item]
        else:

            def g(obj):
                return tuple(obj[item] for item in items)
        return g


def fill(src, dst, tstart, tstop):
    # fetch range start-stop from src, taking values from the highest
    # precision archive, thus optionally requiring multiple fetch + merges
    srcHeader = info(src)

    srcArchives = srcHeader['archives']
    srcArchives.sort(key=itemgetter('retention'))

    # find oldest point in time, stored by both files
    srcTime = int(time.time()) - srcHeader['maxRetention']

    if tstart < srcTime and tstop < srcTime:
        return

    # we want to retain as much precision as we can, hence we do backwards
    # walk in time

    # skip forward at max 'step' points at a time
    for archive in srcArchives:
        # skip over archives that don't have any data points
        rtime = time.time() - archive['retention']
        if tstop <= rtime:
            continue

        untilTime = tstop
        fromTime = rtime if rtime > tstart else tstart

        (timeInfo, values) = fetch(src, fromTime, untilTime)
        (start, end, archive_step) = timeInfo
        pointsToWrite = list(itertools.ifilter(
            lambda points: points[1] is not None,
            itertools.izip(xrange(start, end, archive_step), values)))
        # order points by timestamp, newest first
        pointsToWrite.sort(key=lambda p: p[0], reverse=True)
        update_many(dst, pointsToWrite)

        tstop = fromTime

        # can stop when there's nothing to fetch any more
        if tstart == tstop:
            return


def fill_archives(src, dst, startFrom, endAt=0, overwrite=False):
    """
    Fills gaps in dst using data from src.

    src is the path as a string
    dst is the path as a string
    startFrom is the latest timestamp (archives are read backward)
    endAt is the earliest timestamp (archives are read backward).
          if absent, we take the earliest timestamp in the archive
    overwrite will write all non nullpoints from src dst.
    """
    header = info(dst)
    archives = header['archives']
    archives = sorted(archives, key=lambda t: t['retention'])

    for archive in archives:
        fromTime = max(endAt, time.time() - archive['retention'])
        if fromTime >= startFrom:
            continue

        (timeInfo, values) = fetch(dst, fromTime, untilTime=startFrom)
        (start, end, step) = timeInfo
        gapstart = None
        for value in values:
            has_value = bool(value and not overwrite)
            if not has_value and not gapstart:
                gapstart = start
            elif has_value and gapstart:
                # ignore single units lost
                if (start - gapstart) > archive['secondsPerPoint']:
                    fill(src, dst, gapstart - step, start)
                gapstart = None
            elif gapstart and start == end - step:
                fill(src, dst, gapstart - step, start)

            start += step

        # The next archive only needs to be filled up to the latest point
        # in time we updated.
        startFrom = fromTime
