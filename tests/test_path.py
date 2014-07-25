import unittest

from carbonate.util import metric_to_fs


class PathTest(unittest.TestCase):
    def test_metric_to_fs_no_prepend(self):
        in_ = "servers.s0123.foo.bar"
        out = "servers/s0123/foo/bar.wsp"
        assert metric_to_fs(in_) == out

    def test_metric_to_fs_prepend(self):
        in_ = "servers.s0123.foo.bar"
        out = "/mnt/data/whisper/servers/s0123/foo/bar.wsp"
        assert metric_to_fs(in_, prepend='/mnt/data/whisper') == out
