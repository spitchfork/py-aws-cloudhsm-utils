class SsmParameterNotFoundError(Exception):
    pass


class HsmSubnetsNotFoundError(Exception):
    pass


class MultiSubnetsInAzError(Exception):
    pass


class ClusterPreExistsError(Exception):
    pass


class HsmClusterCreateError(Exception):
    pass


class HsmCreateError(Exception):
    pass


class HsmClustersNotFoundError(Exception):
    pass


class SecurityGroupNotFoundError(Exception):
    pass
