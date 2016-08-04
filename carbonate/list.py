import os
import re


def listMetrics(storage_dir, follow_sym_links=False, metric_suffix='wsp'):
    metric_regex = re.compile(".*\.%s$" % metric_suffix)

    storage_dir = storage_dir.rstrip(os.sep)

    for root, dirnames, filenames in os.walk(storage_dir,
                                             followlinks=follow_sym_links):
        for filename in filenames:
            if metric_regex.match(filename):
                root_path = root[len(storage_dir) + 1:]
                m_path = os.path.join(root_path, filename)
                m_name, m_ext = os.path.splitext(m_path)
                m_name = m_name.replace('/', '.')
                yield m_name
