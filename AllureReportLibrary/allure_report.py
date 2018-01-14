from robot.libraries.BuiltIn import BuiltIn
from .allure_listener import AllureListener
from .version import VERSION


class AllureReportLibrary:
    """
    The Allure Adaptor for Robot Framework is a Library that can be included
    in the Robot scripts to generate Allure compatible XML files which can
    then be used to generate the Allure HTML reports.

    = Allure =
    This Library depends on the command line Allure client to perform the
    actual conversion from xml files to HTML page. For more information on
    the project Allure itself, please visit: http://allure.qatools.ru/.
    The Allure Command Line application can be downloaded from the Allure
    GitHub
    [https://github.com/allure-framework/allure1/releases/latest|release page]

    *NOTE: Allure 1.4.x and 1.5.x are supported.
    Allure 2 is currently not supported.*

    = Adaptor =

    The Adapter is split into two parts: Listener and Library. The Listener
    contains the logic for the Allure file creation. The Library assists the
    Listener by providing keywords to access the listener instance.

    *Listener*

    The Listener contains the core functionality. The listener makes use of the
    Robot Framework
    [http://robotframework.org/robotframework/latest/
    RobotFrameworkUserGuide.html#listener-interface|Listener interface]
    specification to capture the start and end of a suite, test case and
    keyword and output them into the Allure XML format. The files are generated
    when all the test cases and teardown keywords have been processed.

    The listener creates the following files:
    - XML file for each processed suite file.
    - allure.properties, one for each test run.
    - environment.xml, one for each test run.

    *Library*

    The Library is supplementary to the listener and serves to start the
    Listener when it wasn't specified when starting Robot Framework. The
    keywords that are part of this library interact with the active Listener
    instance. In the event that the listener was already started, only the
    library activation if performed.
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = VERSION

    def __init__(self, path=None):
        """
        The Allure Report Library requires the full path to the file containing
        the required properties for Allure to function. This is text file with
        the below properties and their example values. Please ensure to escape
        the : and \ with a \.
        """
        try:
            listener_active = BuiltIn().get_variable_value('${ALLURE}', False)
            if listener_active is False:
                self.ROBOT_LIBRARY_LISTENER = AllureListener(path, 'Library')
        except:
            pass

    def set_output_dir(self, path):
        """
        Set the XML Output Directory

        This keyword allows for the resetting of the allure.cli.logs.xml
        property. When a new folder is set, all the existing files will be
        moved to the new folder.
        """
        pass
