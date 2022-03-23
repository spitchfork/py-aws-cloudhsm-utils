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
