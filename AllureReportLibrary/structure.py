import collections
import jprops
import os
from allure.constants import COMMON_NAMESPACE
from allure.rules import (
    Attribute, Element, WrappedMany, Nested, Many,
    Ignored, xmlfied
)
from allure.structure import IterAttachmentsMixin


class Environment(xmlfied('environment',
                          namespace=COMMON_NAMESPACE,
                          id=Element(),
                          name=Element(),
                          url=Element(),
                          parameters=Many(Nested()))):
    pass


class TestCase(IterAttachmentsMixin,
               xmlfied('test-case',
                       id=Ignored(),  # internal field, see AllureTestListener
                       name=Element(),
                       title=Element().if_(lambda x: x),
                       description=Element().if_(lambda x: x),
                       failure=Nested().if_(lambda x: x),
                       steps=WrappedMany(Nested()),
                       attachments=WrappedMany(Nested()),
                       labels=WrappedMany(Nested()),
                       status=Attribute(),
                       severity=Attribute(),
                       start=Attribute(),
                       stop=Attribute())):
    pass


class AllureProperties(object):
    def __init__(self, propertiesPath):
        self.path = propertiesPath
        if os.path.exists(self.path) is True:
            with open(self.path) as fp:
                self.properties = jprops.load_properties(
                    fp, collections.OrderedDict)
            fp.close()
        else:
            self.properties = {}
            self.set_property(
                "allure.issues.id.pattern",
                "\\b([A-Z]{1,3}[-][0-9]{1,4})\\b")
            self.set_property(
                "allure.issues.tracker.pattern",
                "http://jira.yourcompany.com/tests/%s")
            self.set_property(
                "allure.tests.management.pattern",
                "http://tms.yourcompany.com/tests/%s")
            self.set_property("allure.cli.logs.xml", "./allure-report")
            self.set_property("allure.cli.logs.xml.clear", "True")

    def save_properties(self, path=None):
        if(path is None):
            output_path = self.get_property(
                'allure.cli.logs.xml')+'\\allure.properties'
        else:
            output_path = path

        with open(output_path, 'w+') as fp:
            jprops.store_properties(fp, self.properties, timestamp=False)
        fp.close()

        return True

    def get_property(self, name):
        if name in self.properties.keys():
            return self.properties[name]
        else:
            return None

    def get_properties(self):
        return self.properties

    def set_property(self, name, value):
        self.properties[name] = value
        return True
