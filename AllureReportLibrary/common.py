import allure
import os
from allure.structure import EnvParameter
from six import iteritems

from .structure import Environment


class AllureImpl(allure.common.AllureImpl):
    '''
    AllureImpl extends and overwrites allure.common.AllureImpl.

    All other Parent methods and attributes accessible.
    '''
    def __init__(self, logdir):
        self.logdir = os.path.normpath(
            os.path.abspath(
                os.path.expanduser(os.path.expandvars(logdir))
            )
        )

        if not os.path.exists(self.logdir):
            os.makedirs(self.logdir)

        # That's the state stack. It can contain TestCases or TestSteps.
        # Attaches and steps go to the object at top of the stack.
        self.stack = []

        self.testsuite = None
        self.environment = {}

    def store_environment(self, environmentlist):
        if not self.environment:
            return

        id = environmentlist['id']
        name = environmentlist['name']
        url = environmentlist['url']

        environment = Environment(id=id, name=name, url=url, parameters=[])
        for key, value in iteritems(self.environment):
            environment.parameters.append(
                EnvParameter(name=key, key=key, value=value)
            )

        with self._reportfile('environment.xml') as f:
            self._write_xml(f, environment)
