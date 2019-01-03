import os
import re

# Use the built-in version of scandir/walk if possible, otherwise
# use the scandir module version
try:
    from os import scandir, walk  # noqa # pylint: disable=unused-import
except ImportError:
    from scandir import scandir, walk  # noqa # pylint: disable=unused-import


def listMetrics(storage_dir, follow_sym_links=False, metric_suffix='wsp'):
    metric_regex = re.compile(r".*\.%s$" % metric_suffix)

    storage_dir = storage_dir.rstrip(os.sep)

    for root, _, filenames in walk(storage_dir, followlinks=follow_sym_links):
        for filename in filenames:
            if metric_regex.match(filename):
                root_path = root[len(storage_dir) + 1:]
                m_path = os.path.join(root_path, filename)
                m_name, m_ext = os.path.splitext(m_path)
                m_name = m_name.replace('/', '.')
                yield m_name
