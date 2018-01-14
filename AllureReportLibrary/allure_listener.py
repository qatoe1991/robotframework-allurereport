import os
import pprint
import re
import socket
import subprocess
import sys
import threading
import uuid
import webbrowser

from allure.common import AttachmentType
from allure.constants import Status, Label
from allure.structure import TestLabel, Failure, Attach, TestSuite, TestStep
from allure.utils import now
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from robot.version import get_version, get_full_version, get_interpreter

from .common import AllureImpl
from .constant import Robot, SEVERITIES, STATUSES
from .structure import AllureProperties, TestCase
from .util_funcs import clear_directory, copy_dir_contents
from .version import VERSION


class AllureListener(object):
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, allurePropPath=None, source='Listener'):
        self.stack = []
        self.testsuite = None
        self.callstack = []
        self.AllurePropPath = allurePropPath
        self.AllureIssueIdRegEx = ''
        self.testsuite is None
        self.isFirstSuite = True

        # Setting this variable prevents the loading of a Library added
        # Listener. I case the Listener is added via Command Line, the Robot
        # Context is not yet there and will cause an exceptions. Similar
        # section in start_suite.
        try:
            BuiltIn().get_variable_value('${ALLURE}', False)
            BuiltIn().set_global_variable('${ALLURE}', True)
        except:
            pass

    def start_suitesetup(self, name, attributes):
        start_test_attributes = {
            'critical': 'yes',
            'doc': 'Test Suite Setup section',
            'starttime': attributes['starttime'],
            'tags': [],
            'id': 's1-s1-t0',
            'longname': BuiltIn().get_variable_value('${SUITE_NAME}'),
            'template': ''
        }

        if len(str(start_test_attributes.get('doc'))) > 0:
            description = str(start_test_attributes.get('doc'))
        else:
            description = name

        test = TestCase(
            name=name,
            description=description,
            start=now(),
            attachments=[],
            labels=[],
            steps=[]
        )

        self.stack.append(test)
        return

    def end_suitesetup(self, name, attributes):
        end_test_attributes = {
            'critical': 'yes',
            'doc': 'Test Suite Setup section',
            'starttime': attributes['starttime'],
            'endtime': attributes['endtime'],
            'status': 'PASS',
            'tags': [],
            'id': 's1-s1-t0',
            'longname': BuiltIn().get_variable_value('${SUITE_NAME}'),
            'template': ''
        }

        test = self.stack.pop()
        BuiltIn().run_keyword(name)

        if end_test_attributes.get('status') == Robot.PASS:
            test.status = Status.PASSED
        elif end_test_attributes.get('status') == Robot.FAIL:
            test.status = Status.FAILED
            test.failure = Failure(
                message=end_test_attributes.get('message'), trace=''
            )
        elif end_test_attributes.get('doc') is not '':
            test.description = attributes.get('doc')

        if end_test_attributes['tags']:
            for tag in end_test_attributes['tags']:
                if re.search(self.AllureIssueIdRegEx, tag):
                    test.labels.append(TestLabel(
                        name=Label.ISSUE,
                        value=tag))
                if tag.startswith('feature'):
                    test.labels.append(TestLabel(
                        name='feature',
                        value=tag.split(':')[-1]))
                if tag.startswith('story'):
                    test.labels.append(TestLabel(
                        name='story',
                        value=tag.split(':')[-1]))
                elif tag in SEVERITIES:
                    test.labels.append(TestLabel(
                        name='severity',
                        value=tag))
                elif tag in STATUSES:
                    test.status = tag

        self.PabotPoolId = BuiltIn().get_variable_value(
            '${PABOTEXECUTIONPOOLID}'
        )

        if(self.PabotPoolId is not None):
            self.threadId = 'PabotPoolId-' + str(self.PabotPoolId)
        else:
            self.threadId = threading.get_ident()

        test.labels.append(TestLabel(
            name='thread',
            value=str(self.threadId)))

        self.testsuite.tests.append(test)
        test.stop = now()
        return test

    def start_test(self, name, attributes):

        if len(str(attributes.get('doc'))) > 0:
            description = str(attributes.get('doc'))
        else:
            description = name

        test = TestCase(
            name=name,
            description=description,
            start=now(),
            attachments=[],
            labels=[],
            steps=[],
            severity='normal'
        )

        self.stack.append(test)
        return

    def end_test(self, name, attributes):
        if not self.stack:
            return
        test = self.stack[-1]

        if attributes.get('status') == Robot.PASS:
            test.status = Status.PASSED
        elif attributes.get('status') == Robot.FAIL:
            test.status = Status.FAILED
            test.failure = Failure(message=attributes.get('message'), trace='')
        elif attributes.get('doc') is not '':
            test.description = attributes.get('doc')

        if attributes['tags']:
            for tag in attributes['tags']:
                if re.search(self.AllureIssueIdRegEx, tag):
                    test.labels.append(TestLabel(
                        name=Label.ISSUE,
                        value=tag))
                elif tag.startswith('feature'):
                    test.labels.append(TestLabel(
                        name='feature',
                        value=tag.split(':')[-1]))
                elif tag.startswith('story'):
                    test.labels.append(TestLabel(
                        name='story',
                        value=tag.split(':')[-1]))
                elif tag in SEVERITIES:
                    test.labels.append(TestLabel(
                        name='severity',
                        value=tag)
                    )
                    test.severity = tag
                elif tag in STATUSES:
                    test.status = tag
                else:
                    test.labels.append(TestLabel(
                        name='tag',
                        value=tag))

        self.PabotPoolId = BuiltIn().get_variable_value(
            '${PABOTEXECUTIONPOOLID}'
        )
        if(self.PabotPoolId is not None):
            self.threadId = 'PabotPoolId-' + str(self.PabotPoolId)
        else:
            self.threadId = threading.get_ident()

        test.labels.append(TestLabel(
            name='thread',
            value=str(self.threadId)))

        self.testsuite.tests.append(test)
        test.stop = now()
        return test

    def start_suite(self, name, attributes):
        self.SuitSrc = BuiltIn().get_variable_value('${SUITE_SOURCE}')
        self.ExecDir = BuiltIn().get_variable_value('${EXECDIR}')

        if(self.AllurePropPath is None):
            self.AllurePropPath = self.ExecDir + '\\allure.properties'

        if os.path.exists(self.AllurePropPath) is True:
            self.AllureProperties = AllureProperties(self.AllurePropPath)
            self.AllureIssueIdRegEx = self.AllureProperties.get_property(
                'allure.issues.id.pattern'
            )
        else:
            self.AllureProperties = AllureProperties(self.AllurePropPath)
            self.AllureIssueIdRegEx = self.AllureProperties.get_property(
                'allure.issues.id.pattern'
            )

        # Not using &{ALLURE} as this is throwing an error and ${ALLURE}
        # gives the desired dictionary in Allure as well.
        BuiltIn().set_global_variable(
            '${ALLURE}',
            self.AllureProperties.get_properties()
        )

        IsSuiteDirectory = os.path.isdir(self.SuitSrc)
        if not IsSuiteDirectory:
            if self.AllureProperties.get_property(
                    'allure.cli.logs.xml') is None:
                self.allurelogdir = BuiltIn().get_variable_value(
                    '${OUTPUT_DIR}') + '\Allure'
            else:
                self.allurelogdir = self.AllureProperties.get_property(
                    'allure.cli.logs.xml'
                )
            self.AllureImplc = AllureImpl(self.allurelogdir)

        PabotPoolId = BuiltIn().get_variable_value('${PABOTEXECUTIONPOOLID}')
        try:
            if(self.isFirstSuite is True
                and self.AllureProperties.get_property(
                    'allure.cli.logs.xml.clear') == 'True'
                    and PabotPoolId is None):
                clear_directory(
                    self.AllureProperties.get_property('allure.cli.logs.xml')
                )
        except Exception as e:
            logger.console(pprint.pformat(e))
        finally:
                self.isFirstSuite = False

        if attributes.get('doc') is not '':
            description = attributes.get('doc')
        else:
            description = name

        self.testsuite = TestSuite(
            name=name,
            title=name,
            description=description,
            tests=[],
            labels=[],
            start=now()
        )

        return

    def end_suite(self, name, attributes):

        self.testsuite.stop = now()
        logfilename = '%s-testsuite.xml' % uuid.uuid4()

        # When running a folder, the folder itself is also considered a Suite
        # The full check depends on the availability of all the vars which are
        # only available when a Robot file has started.
        IsSuiteDirectory = os.path.isdir(
            BuiltIn().get_variable_value("${SUITE_SOURCE}")
        )

        if(not(IsSuiteDirectory)):
            with self.AllureImplc._reportfile(logfilename) as f:
                self.AllureImplc._write_xml(f, self.testsuite)
        return

    def start_keyword(self, name, attributes):
        if (
            hasattr(self, attributes.get('kwname').replace(" ", "_"))
            and callable(getattr(
                self, attributes.get('kwname').replace(" ", "_")))):
            libraryMethodToCall = getattr(
                self,
                attributes.get('kwname').replace(" ", "_")
            )
            libraryMethodToCall(name, attributes)
            keyword = TestStep(
                name=name,
                title=attributes.get('kwname'),
                attachments=[],
                steps=[],
                start=now()
            )
            if self.stack:
                self.stack.append(keyword)
            return keyword

        if (
            attributes.get('type') == 'Keyword'
            or (
                attributes.get('type') == 'Teardown'
                and len(self.stack) is not 0)):
            keyword = TestStep(
                name=name,
                title=attributes.get('kwname'),
                attachments=[],
                steps=[],
                start=now()
            )
            if self.stack:
                self.stack.append(keyword)
            return keyword

        """
        Processing the Suite Setup.

        Although there is no test case yet, a virtual one is created to allow
        for the inclusion of the keyword.
        """
        if(attributes.get('type') == 'Setup' and len(self.stack) == 0):
            self.start_suitesetup(name, attributes)
            return

        if(attributes.get('type') == 'Teardown' and len(self.stack) == 0):
            self.start_suitesetup(name, attributes)
            return

    def end_keyword(self, name, attributes):
        if len(self.stack) > 0:
            if (
                attributes.get('type') == 'Keyword'
                or (
                    attributes.get('type') == 'Teardown'
                    and isinstance(self.stack[-1], TestStep) is True)):

                step = self.stack.pop()
                if(attributes.get('status') == 'FAIL'):
                    step.status = 'failed'
                elif(attributes.get('status') == 'PASS'):
                    step.status = 'passed'

                step.stop = now()

                self.stack[-1].steps.append(step)
                return

            if (attributes.get('type') == 'Setup'
                    and len(self.testsuite.tests) == 0):
                self.end_suitesetup(name, attributes)
                return

            if (attributes.get('type') == 'Teardown'
                    and isinstance(self.stack[-1], TestCase) is True):
                self.end_suitesetup(name, attributes)
                return
        return

    def message(self, msg):
        pass

    def log_message(self, msg):
        # Check to see if there are any items to add the log message to
        # this check is needed because otherwise Suite Setup may fail.
        if len(self.stack) > 0:
            if self.stack[-1].title == 'Capture Page Screenshot':
                screenshot = re.search(
                    '[a-z]+-[a-z]+-[0-9]+.png',
                    msg['message']
                )
                if screenshot is not None:
                    self.attach(
                        '{}'.format(screenshot.group(0)),
                        screenshot.group(0)
                    )
            else:
                kwname = msg['message']
            startKeywordArgs = {
                'args': [],
                'assign': [],
                'doc': '',
                'kwname': kwname,
                'libname': 'BuiltIn',
                'starttime': now(),
                'tags': [],
                'type': 'Keyword'
            }
            self.start_keyword('Log Message', startKeywordArgs)

            endKeywordArgs = {
                'args': [],
                'assign': [],
                'doc': '',
                'elapsedtime': 0,
                'endtime': now(),
                'kwname': kwname,
                'libname': 'BuiltIn',
                'starttime': now(),
                'status': 'PASS',
                'tags': [],
                'type': 'Keyword'
            }
            self.end_keyword('Log Message', endKeywordArgs)
        return

    def close(self):
        IsSuiteDirectory = os.path.isdir(self.SuitSrc)
        if not IsSuiteDirectory:
            self.save_environment()
            self.AllureProperties.save_properties()

            if (self.AllureProperties.get_property('allure.cli.outputfiles')
                    and self.PabotPoolId is None):
                self.allure(self.AllureProperties)

        return

    def save_environment(self):
        environment = {}
        environment['id'] = 'Robot Framework'
        environment['name'] = socket.getfqdn()
        environment['url'] = 'http://'+socket.getfqdn()+':8000'

        env_dict = (
            {'Robot Framework Full Version': get_full_version()},
            {'Robot Framework Version': get_version()},
            {'Interpreter': get_interpreter()},
            {'Python version': sys.version.split()[0]},
            {'Allure Adapter version': VERSION},
            {'Robot Framework CLI Arguments': sys.argv[1:]},
            {'Robot Framework Hostname': socket.getfqdn()},
            {'Robot Framework Platform': sys.platform}
        )

        for key in env_dict:
            self.AllureImplc.environment.update(key)

        self.AllureImplc.logdir = self.AllureProperties.get_property(
            'allure.cli.logs.xml'
        )
        self.AllureImplc.store_environment(environment)

    def allure(self, AllureProps):
        JAVA_PATH = AllureProps.get_property('allure.java.path')
        ALLURE_HOME = '-Dallure.home='+AllureProps.get_property('allure.home')
        JAVA_CLASSPATH = (
            '-cp "' + AllureProps.get_property('allure.java.classpath') + '"'
        )
        ALLURE_LOGFILE = AllureProps.get_property('allure.cli.logs.xml')
        ALLURE_OUTPUT = '-o ' + AllureProps.get_property(
            'allure.cli.logs.output')
        JAVA_CLASS = 'ru.yandex.qatools.allure.CommandLine'
        ALLURE_COMMAND = 'generate'
        ALLURE_URL = AllureProps.get_property('allure.results.url')

        allure_cmd = (
            JAVA_PATH + ' ' + ALLURE_HOME + ' ' + JAVA_CLASSPATH + ' ' +
            JAVA_CLASS + ' ' + ALLURE_COMMAND + ' ' + ALLURE_LOGFILE +
            ' ' + ALLURE_OUTPUT
        )

        if (AllureProps.get_property('allure.cli.outputfiles') == 'True'):
            open(os.devnull, 'w')
            subprocess.Popen(
                allure_cmd, stderr=subprocess.STDOUT, shell=True).wait()

            if (AllureProps.get_property(
                    'allure.results.browser.open') == 'True'):
                webbrowser.open(ALLURE_URL, new=0, autoraise=True)

    def attach(self, title, contents, attach_type=AttachmentType.PNG):
        """
        This functions created the attachments and append it to the test.
        """
        contents = os.path.join(
            BuiltIn().get_variable_value('${OUTPUT_DIR}'),
            contents
        )
        with open(contents, 'rb') as f:
            file_contents = f.read()

        attach = Attach(
            source=self.AllureImplc._save_attach(file_contents, attach_type),
            title=title,
            type=attach_type
        )

        self.stack[-1].attachments.append(attach)
        return

    def Set_Output_Dir(self, name, attributes):
        copy_dir_contents(
            self.AllureProperties.get_property('allure.cli.logs.xml'),
            attributes['args'][0]
        )
        self.AllureProperties.set_property(
            'allure.cli.logs.xml',
            attributes['args'][0]
        )
        self.AllureImplc.logdir = attributes['args'][0]
