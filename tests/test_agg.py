import unittest

import carbonate.sieve
from carbonate.lookup import lookup

from carbonate.cluster import Cluster
from carbonate.config import Config


class AggLookupSieveTest(unittest.TestCase):

    def setUp(self):
        config_file = "tests/conf/realistic.conf"
        agg_rules_file = "test/conf/aggregation-rules.conf"
        config = Config(config_file)
        self.cluster = Cluster(config, cluster='agg', aggregation_rules=agg_rules_file)

    # testing all aggregation hash tests in one go,
    # otherwise it clashes on reading rules file in twisted
    def test_sieve_lookup_agg(self):
        inputs = ['metric.a.100',
                  'metric.a.101',
                  'metric.a.102',
                  'metric.a.103',
                  'metric.a.104',
                  'metric.a.105',
                  'metric.a.106',
                  'metric.a.107',
                  'metric.a.108',
                  'metric.a.109']

        node = '1.1.1.1'
        node_long = '1.1.1.1:2003:0'
        output = ['metric.a.100',
                  'metric.a.104',
                  'metric.a.105',
                  'metric.a.106',
                  'metric.a.107']

        node2 = '2.2.2.2'
        node2_long = '2.2.2.2:2003:0'
        output2 = ['metric.a.101',
                   'metric.a.102',
                   'metric.a.103',
                   'metric.a.108',
                   'metric.a.109']

        f = list(carbonate.sieve.filterMetrics(inputs, node, self.cluster))
        self.assertEqual(f, output)
        f = list(carbonate.sieve.filterMetrics(inputs, node_long, self.cluster))
        self.assertEqual(f, output)

        f = list(carbonate.sieve.filterMetrics(inputs, node2, self.cluster))
        self.assertEqual(f, output2)
        f = list(carbonate.sieve.filterMetrics(inputs, node2_long, self.cluster))
        self.assertEqual(f, output2)

        f = list(carbonate.sieve.filterMetrics(inputs, node, self.cluster, True))
        self.assertEqual(f, output2)

        f = list(carbonate.sieve.filterMetrics(inputs, node2, self.cluster, True))
        self.assertEqual(f, output)

        f = lookup('metric.a.one', self.cluster)
        self.assertEqual(f, ['2.2.2.2:2003:0'])
