from AllureListener import AllureListener
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
from version import VERSION

class AllureReportLibrary:
    """
    The Allure Adaptor for Robot Framework is a Library that can be included
    in the Robot scripts to generate Allure compatible XML files which can 
    then be used to generate the Allure HTML reports. 
    
    = Allure =
    This Library depends on the command line Allure client to perform the actual 
    conversion from xml files to HTML page. For more information on the project 
    Allure itself, please visit: http://allure.qatools.ru/. The Allure Command 
    Line application can be downloaded from the Allure GitHub 
    [https://github.com/allure-framework/allure1/releases/latest|release page]
    
    *NOTE: Allure 1.4.x and 1.5.x are supported. Allure 2 is currently not supported.*
    
    
    = Adaptor = 

    The Adapter is split into two parts: Listener and Library. The Listener 
    contains the logic for the Allure file creation. The Library assists the
    Listener by providing keywords to access the listener instance.

    *Listener*

    The Listener contains the core functionality. The listener makes use of the 
    Robot Framework [http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-interface| 
    Listener interface] specification to capture the start and end of a suite,
    test case and keyword and output them into the Allure XML format. The files 
    are generated when all the test cases and teardown keywords have been processed.

    The listener creates the following files:
    - XML file for each processed suite file.
    - allure.properties, one for each test run.
    - environment.xml, one for each test run.

    *Library*

    The Library is supplementary to the listener and serves to start the Listener
    when it wasn't specified when starting Robot Framework. The keywords that are
    part of this library interact with the active Listener instance. In the event
    that the listener was already started, only the library activation if performed.

    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = VERSION

    def __init__(self, AllureOutputPath=None):
        """
        The Allure Report Library requires the full path to the file containing
        the required properties for Allure to function. This is a text file with 
        the below properties and their example values. Please ensure to escape 
        the : and \ with a \.
        
        | *Property*                   | *=Value*                                        | *Description* |
        | allure.cli.logs.xml          | C\:\\RobotScriptDir\\logs\\allure               | Directory where the Listener should store the xml log files. |
        | allure.cli.logs.xml.clear    | True                                            | Flag: True/False indicating if all the xml files in the directory should be removed. |
        | allure.cli.logs.output       | C\:\\RobotScriptDir\\logs\\allure\\report       | Directory where the html files should be stored. |
        | allure.cli.outputfiles       | True                                            | Flag: True/False indicating if the Allure CLI should be called after the test run was completed. |
        | allure.java.path             | C\:\\PROGRA~1\\Java\\JRE18~1.0_7\\bin\\java.exe | Path: Path to the Java executable for when it is not in the global system path. |
        | allure.home                  | C\:\\allure\                                    | Directory: folder where Allure Command Line application can be found. |
        | allure.java.classpath        | C\:\\allure\\lib\\*;C\:\\allure\\conf\\*        | Path: Class path for the Allure java libraries. |
        | allure.results.browser.open  | True                                            | Flag: True/False indicating if a browser should be opened after the test run was completed. |
        | allure.results.url           | http://localhost/allure/                        | URL: Address to where the browser will be opened to show the report. |
        """
        try:
            AllureListenerActive = BuiltIn().get_variable_value('${ALLURE}', False)
            if AllureListenerActive is False:
                self.ROBOT_LIBRARY_LISTENER = AllureListener(AllureOutputPath, 'Library')
        except:
            pass
        return None
        
    def set_output_dir(self, AllureOutputPath):
        """
        Set the XML Output Directory
         
        This keyword allows for the resetting of the allure.cli.logs.xml property. 
        When a new folder is set, all the existing files will be moved to the new
        folder.
        """
        pass

#     def set_log_level(self, log_level):
#         pass
#     
#     def stop_logging(self):
#         pass
#     
#     def set_test_case_severity(self, severity):
#         pass
#     
#     def set_test_case_status(self, status):
#         pass
#     
#     def set_keyword_status(self, status):
#         pass
#     
#     def set_thread_id(self, thread_id):
#         pass
#     
#     def set_label(self, labelname, value):
#         pass
#     
#     def skip_test_case_logging(self, test_case_name):
#         pass
# 
#     def skip_test_case_step_logging(self, test_case_name):
#         pass
#     
#     def hide_attachments(self):
#         pass
#     
#     def set_issue_management_id_pattern(self, pattern):
#         pass
#     
#     def set_issue_management_url(self, url):
#         pass
#     
#     def set_test_case_management_id_pattern(self, pattern):
#         pass
#     
#     def set_test_case_management_url(self, url):
    