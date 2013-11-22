import errno
import os
import re
import sys

from .util import common_parser


def main():
    parser = common_parser('List the metrics this carbon node contains')

    parser.add_argument(
        '-d', '--storage-dir',
        default='/opt/graphite/storage/whisper',
        help='Storage dir')

    args = parser.parse_args()

    metric_suffix = 'wsp'
    metric_regex = re.compile(".*\.%s$" % metric_suffix)

    try:
        for root, dirnames, filenames in os.walk(args.storage_dir):
            for filename in filenames:
                if metric_regex.match(filename):
                    root_path = root[len(args.storage_dir) + 1:]
                    m_path = os.path.join(root_path, filename)
                    m_name, m_ext = os.path.splitext(m_path)
                    m_name = m_name.replace('/', '.')
                    print m_name
    except IOError as e:
        if e.errno == errno.EPIPE:
            pass  # we got killed, lol
        else:
            raise SystemExit(e)
    except KeyboardInterrupt:
        sys.exit(1)
