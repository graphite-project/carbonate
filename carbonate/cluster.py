import sys

# Inject the graphite libs into the system path
sys.path.insert(0, '/opt/graphite/lib')

# We're going to use carbon's libs directly to do things
try:
    from carbon import util
    from carbon.routers import ConsistentHashingRouter
except ImportError as e:
    raise SystemExit("No bueno. Can't import carbon! (" + str(e) + ")")


class Cluster():
    def __init__(self, config, cluster='main'):
        self.ring = ConsistentHashingRouter(config.replication_factor(cluster))

        try:
            dest_list = config.destinations(cluster)
            self.destinations = util.parseDestinations(dest_list)
        except ValueError as e:
            raise SystemExit("Unable to parse destinations!" + str(e))

        for d in self.destinations:
            self.ring.addDestination(d)

    def getDestinations(self, metric):
        return self.ring.getDestinations(metric)
