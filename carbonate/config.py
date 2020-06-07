import os
import pwd
try:
    from ConfigParser import RawConfigParser, NoOptionError
except ImportError:
    from configparser import RawConfigParser, NoOptionError


class Config():

    """
    Load and access the carbonate configuration.
    """

    def __init__(self, config_file):
        self.config_file = config_file
        self.config = RawConfigParser()
        self.config.read(config_file)

    def clusters(self):
        """Return the clusters defined in the config file."""
        return self.config.sections()

    def destinations(self, cluster='main'):
        """Return a list of destinations for a cluster."""
        if not self.config.has_section(cluster):
            raise SystemExit("Cluster '%s' not defined in %s"
                             % (cluster, self.config_file))
        destinations = self.config.get(cluster, 'destinations')
        return destinations.replace(' ', '').split(',')

    def relay_method(self, cluster='main'):
        """Return the carbon relay method for a cluster."""
        if not self.config.has_section(cluster):
            raise SystemExit("Cluster '%s' not defined in %s"
                             % (cluster, self.config_file))
        if self.config.has_option(cluster, 'relay_method'):
            return self.config.get(cluster, 'relay_method')
        return 'consistent-hashing'

    def replication_factor(self, cluster='main'):
        """Return the replication factor for a cluster as an integer."""
        if not self.config.has_section(cluster):
            raise SystemExit("Cluster '%s' not defined in %s"
                             % (cluster, self.config_file))
        return int(self.config.get(cluster, 'replication_factor'))

    def ssh_user(self, cluster='main'):
        """Return the ssh user for a cluster or current user if undefined."""
        if not self.config.has_section(cluster):
            raise SystemExit("Cluster '%s' not defined in %s"
                             % (cluster, self.config_file))
        try:
            return self.config.get(cluster, 'ssh_user')
        except NoOptionError:
            return pwd.getpwuid(os.getuid()).pw_name

    def whisper_lock_writes(self, cluster='main'):
        """Lock whisper files during carbon-sync."""
        if not self.config.has_section(cluster):
            raise SystemExit("Cluster '%s' not defined in %s"
                             % (cluster, self.config_file))
        try:
            return bool(self.config.get(cluster, 'whisper_lock_writes'))
        except NoOptionError:
            return False

    def hashing_type(self, cluster='main'):
        """Hashing type of cluster."""
        if not self.config.has_section(cluster):
            raise SystemExit("Cluster '%s' not defined in %s"
                             % (cluster, self.config_file))
        hashing_type = 'carbon_ch'
        try:
            return self.config.get(cluster, 'hashing_type')
        except NoOptionError:
            return hashing_type

    def diverse_replicas(self, cluster='main'):
        """DIVERSE REPLICAS parameter of cluster."""
        if not self.config.has_section(cluster):
            raise SystemExit("Cluster '%s' not defined in %s"
                             % (cluster, self.config_file))
        diverse_replicas = True
        try:
            return self.config.get(cluster, 'diverse_replicas')
        except NoOptionError:
            return diverse_replicas
