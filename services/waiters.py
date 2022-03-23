# Standard/External modules
import logging
from enum import Enum
import botocore.waiter

logger = logging.getLogger(__name__)


class WaitState(Enum):
    SUCCESS = 'success'
    FAILURE = 'failure'


class BaseWaiter:
    """
    Base class for a custom waiter that leverages botocore's waiter code. Waiters
    poll an operation, with a specified delay between each polling attempt, until
    either an accepted result is returned or the number of maximum attempts is reached.
    """
    def __init__(self, waiter_name, api_operation, resp_dict_key, wait_over_acceptors,
                 boto_client, delay=10, max_tries=60, matcher='path'):

        self.waiter_name = waiter_name
        self.api_operation = api_operation
        self.resp_dict_key = resp_dict_key
        self.boto_client = boto_client
        self.waiter_model = botocore.waiter.WaiterModel({
            'version': 2,
            'waiters': {
                waiter_name: {
                    "delay": delay,
                    "operation": api_operation,
                    "maxAttempts": max_tries,
                    "acceptors": [{
                        "state": state.value,
                        "matcher": matcher,
                        "argument": resp_dict_key,
                        "expected": expected
                    } for expected, state in wait_over_acceptors.items()]
                }}})
        self.waiter = botocore.waiter.create_waiter_with_client(self.waiter_name, self.waiter_model, self.boto_client)

    def __call__(self, parsed, **kwargs):
        """
        Handles the after-call event by logging information about the operation.
        """
        logger.info("{} waiter called {}.".format(self.waiter_name, self.api_operation))
        logger.debug("{} waiter returned response: {}".format(self.waiter_name, parsed))

    def _wait(self, **kwargs):
        event_name = f'after-call.{self.boto_client.meta.service_model.service_name}'
        self.boto_client.meta.events.register(event_name, self)
        self.waiter.wait(**kwargs)
        self.boto_client.meta.events.unregister(event_name, self)


class HsmClusterCreateCompleteWaiter(BaseWaiter):
    def __init__(self, client):
        # note this waiter is forced to assess the first (zero index) cluster in a 'potential' list
        # since earlier checks are made to ensure no hsm clusters exist the list size should always be one
        super().__init__('HsmClusterCreateComplete', 'DescribeClusters', 'Clusters[0].State',
                         {'UNINITIALIZED': WaitState.SUCCESS}, client)

    def wait(self):
        self._wait()
