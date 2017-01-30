import os
import sys
import inspect

# Inject the graphite libs into the system path
venv_root = ""
if os.environ.get("VIRTUAL_ENV"):
    # Running in a virtual environment
    venv_root = [p for p in sys.path if p.endswith("site-packages")][-1]
sys.path.insert(0, venv_root + "/opt/graphite/lib")

# We're going to use carbon's libs directly to do things
try:
    from carbon import util
    from carbon.routers import ConsistentHashingRouter
except ImportError as e:
    raise SystemExit("No bueno. Can't import carbon! (" + str(e) + ")")


class Cluster():
    def __init__(self, config, cluster='main'):
        # Support multiple versions of carbon, the API changed in 0.10.
        args = inspect.getargspec(ConsistentHashingRouter.__init__).args
        if 'replication_factor' in args:
            ring = ConsistentHashingRouter(config.replication_factor(cluster))
        else:
            class Settings(object):
                REPLICATION_FACTOR = config.replication_factor(cluster)
                DIVERSE_REPLICAS = False
            ring = ConsistentHashingRouter(Settings())

        self.ring = ring

        try:
            dest_list = config.destinations(cluster)
            self.destinations = util.parseDestinations(dest_list)
        except ValueError as e:
            raise SystemExit("Unable to parse destinations!" + str(e))

        for d in self.destinations:
            self.ring.addDestination(d)

    def getDestinations(self, metric):
        return self.ring.getDestinations(metric)
