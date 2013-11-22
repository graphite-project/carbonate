import unittest
from mock import Mock

from carbonate.cluster import Cluster
from carbonate.lookup import lookup


class LookupTest(unittest.TestCase):

    def setUp(self):
        self.config = Mock()

    def test_lookup(self):
        self.config.replication_factor = Mock(return_value=2)
        self.config.destinations = Mock(
            return_value=['192.168.9.13:2124:0', '192.168.9.15:2124:0',
                          '192.168.6.20:2124:0', '192.168.6.19:2124:0',
                          '192.168.6.16:2124:0']
            )

        self.cluster = Cluster(self.config)

        assert lookup('metric.one', self.cluster) == \
            ['192.168.6.16:2124:0', '192.168.6.19:2124:0']
