import os
import sys
import logging
import shutil
import subprocess
import time
from datetime import timedelta
from tempfile import mkdtemp, NamedTemporaryFile
from shutil import rmtree
from whisper import CorruptWhisperFile

from .fill import fill_archives


def sync_from_remote(sync_file, remote, staging, rsync_options):
    try:
        os.makedirs(os.path.dirname(staging))
    except OSError:
        pass

    cmd = " ".join(['rsync', rsync_options, '--files-from',
                    sync_file.name, remote, staging + '/'
                    ])

    print("  - Rsyncing metrics: %s" % cmd)

    proc = subprocess.Popen(cmd,
                            shell=True,
                            universal_newlines=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)

    for line in iter(proc.stdout.readline, b''):
        sys.stdout.write(line.decode("utf-8"))
        sys.stdout.flush()

    proc.communicate()
    print("    rc: %d" % proc.returncode)

    if proc.returncode != 0:
        logging.warn("Failed to sync from %s! rsync rc=%d",
                     remote, proc.returncode)
        return False
    return True


def sync_batch(metrics_to_heal, lock_writes=False, overwrite=False):
    batch_start = time.time()
    sync_count = 0
    sync_total = len(metrics_to_heal)
    sync_avg = 0.1
    sync_elapsed = 0
    sync_remain = 'n/a'

    for (staging, local) in metrics_to_heal:
        sync_count += 1
        sync_start = time.time()
        sync_percent = float(sync_count) / sync_total * 100
        status_line = "  - Syncing %d of %d metrics. " \
                      "Avg: %fs  Time Left: %ss (%d%%)" \
                      % (sync_count, sync_total, sync_avg,
                         sync_remain, sync_percent)
        print(status_line)

        # Do not try healing data past the point they were rsync'd
        # as we would not have new points in staging anyway.
        heal_metric(staging, local, end_time=batch_start,
                    overwrite=overwrite,
                    lock_writes=lock_writes)

        sync_elapsed += time.time() - sync_start
        sync_avg = sync_elapsed / sync_count
        sync_remain_s = sync_avg * (sync_total - sync_count)
        sync_remain = str(timedelta(seconds=sync_remain_s))

    batch_elapsed = time.time() - batch_start
    return batch_elapsed


def heal_metric(source, dest, start_time=0, end_time=None, overwrite=False,
                lock_writes=False):
    if end_time is None:
        end_time = time.time()
    try:
        with open(dest):
            try:
                # fill_archives' start and end are the opposite
                # of what you'd expect
                fill_archives(
                    source, dest, startFrom=end_time, endAt=start_time,
                    overwrite=overwrite, lock_writes=lock_writes)
            except CorruptWhisperFile as e:
                if e.path == source:
                    # The source file is corrupt, we bail
                    logging.warn("Source file corrupt, skipping: %s" % source)
                else:
                    # Do it the old fashioned way...possible data loss
                    logging.warn("Overwriting corrupt file: %s" % dest)
                    try:
                        os.makedirs(os.path.dirname(dest))
                    except os.error:
                        pass
                    try:
                        # Make a backup of corrupt file
                        corrupt = dest + ".corrupt"
                        shutil.copyfile(dest, corrupt)
                        logging.warn("Corrupt file saved as %s" % corrupt)
                        shutil.copyfile(source, dest)
                    except IOError as e:
                        logging.warn("Failed to copy %s! %s" % (dest, e))
            except Exception as e:
                logging.warn("Exception during heal: %s" % str(e))
                logging.warn("Skipping heal: %s => %s" % (source, dest))
    except IOError:
        try:
            os.makedirs(os.path.dirname(dest))
        except os.error:
            pass
        try:
            shutil.copyfile(source, dest)
        except IOError as e:
            logging.warn("Failed to copy %s! %s" % (dest, e))


def run_batch(metrics_to_sync, remote, local_storage, rsync_options,
              remote_ip, dirty, lock_writes=False, overwrite=False,
              tmpdir=None, rsync_max_retries=3, rsync_retries_interval=5):
    try:
        staging_dir = mkdtemp(prefix=remote_ip, dir=tmpdir)
    except OSError as e:
        logging.error('Failed to create rsync staging dir %s: %s' %
                      (e.filename, e.strerror))
    else:
        sync_file = NamedTemporaryFile(delete=False, dir=tmpdir)

        metrics_to_heal = []

        for metric in metrics_to_sync:
            staging_file = "%s/%s" % (staging_dir, metric)
            local_file = "%s/%s" % (local_storage, metric)
            metrics_to_heal.append((staging_file, local_file))

        sync_file.write(("\n".join(metrics_to_sync)).encode())
        sync_file.flush()

        sync_tries = 0
        sync_success = False
        rsync_start = time.time()
        while not sync_success and sync_tries < rsync_max_retries:
            sync_tries += 1
            sync_success = sync_from_remote(sync_file, remote, staging_dir,
                                            rsync_options)
            if not sync_success:
                time.sleep(rsync_retries_interval)

        rsync_elapsed = (time.time() - rsync_start)

        if sync_success:
            merge_elapsed = sync_batch(metrics_to_heal,
                                       lock_writes=lock_writes,
                                       overwrite=overwrite)
        else:
            merge_elapsed = 0.0
            with NamedTemporaryFile(delete=False,
                                    dir=tmpdir,
                                    suffix='.failed') as f:
                f.write(("\n".join(metrics_to_sync)).encode())
                print("    Rsync failed; metric names saved to %s" % f.name)

        total_time = rsync_elapsed + merge_elapsed

        print("    --------------------------------------")
        print("    Rsync time: %ss" % rsync_elapsed)
        print("    Merge time: %ss" % merge_elapsed)
        print("    Total time: %ss" % total_time)

        # Cleanup
        if dirty:
            print("    dirty mode: left temporary directory %s" % staging_dir)
        else:
            rmtree(staging_dir)

        os.unlink(sync_file.name)
