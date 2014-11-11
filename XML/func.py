
import xml.etree.ElementTree as ET
import subprocess

import app_map
import XML_config
import AXUI.logger as AXUI_logger

class _Step(object):
    _LOGGER = AXUI_logger.get_logger()
    def __init__(self, xml_element, app_map):
        self.xml_element = xml_element
        self.type = xml_element.attrib["type"]
        self.command = xml_element.attrib["cmd"]
        try:
            self.app_map_name = xml_element.attrib["app_map"]
        except KeyError:
            self.app_map_name = ""
        
        if self.app_map_name:
            self.app_map = app_map.get_include_app_map_by_name(self.app_map_name)
        else:
            self.app_map = app_map
        
    def run(self):
        if self.type == "GUI":
            self._LOGGER.debug("run app map command: %s" % self.command)
            self.app_map.execute(self.command)
        elif self.type == "CLI":
            self._LOGGER.debug("run system command: %s" % self.command)
            subprocess.Popen(self.command)
        else:
            raise AppMapException("step type must be GUI or CLI, get: %s" % self.type)

class Func(object):
    _LOGGER = AXUI_logger.get_logger()
    def __init__(self, xml_element, app_map):
        self.xml_element = xml_element
        self.app_map = app_map
        self.name = xml_element.attrib["name"]
        self.description = xml_element.attrib["description"]
        self.steps = []
        self.parse_steps()
    
    def __repr__(self):
        return "Func instance for %s" % self.name
    
    def parse_steps(self):
        for step_xml_element in self.xml_element.findall("AXUI:step", namespaces={"AXUI":"AXUI"}):
            self.steps.append(_Step(step_xml_element, self.app_map))
            
    def run(self):
        for step in self.steps:
            step.run()
            
        
