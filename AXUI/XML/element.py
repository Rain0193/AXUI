
import os
import time
from AXUI.logger import LOGGER, logger_config
from AXUI.driver import get_driver
from AXUI.exceptions import DriverException, TimeOutError
from .XML_config import core_config

class FakeUIElement(object):
    '''used for Elements without identifier
    '''
    def __repr__(self):
        return "Fake element, Use when there is no identifier for this element"

    def verify(self):
        return self

class RootElement(object):
    '''wrapper for root element
    provide interface for enter point of UI automation API
    like desktop of windows UIA API, or browser for web driver API

    Interfaces exposed for use:
        verify:             function to verify if self still exist
        start:              function to init and start this element
        stop:               function to stop this element
        screenshot:         function to take a screenshot

        other driver special interfaces
    '''
    def __init__(self):
        #Need init by app map module
        self.name = ""
        self.children = {}
        self.parent = None
        self._time_out = None

        #get driver module
        driver_module = get_driver()
        #represent for root interface of driver module
        self.root = driver_module.Root()

    def __repr__(self):
        docstring = "root element instance"
        return docstring

    @property
    def timeout(self):
        if not self._time_out is None:
            return self._time_out
        else:
            return core_config.timeout

    @timeout.setter
    def timeout(self, input_value):
        self._time_out = input_value

    @property
    def screenshot_location(self):
        return core_config.screenshot_location

    @property
    def screenshot_on(self):
        if core_config.screenshot_option == "always_on":
            return True
        else:
            return False

    @property
    def screenshot_off(self):
        if core_config.screenshot_option == "always_off":
            return True
        else:
            return False

    @property
    def screenshot_on_failure(self):
        if core_config.screenshot_option == "on_failure":
            return True
        else:
            return False

    @property
    def details(self):
        '''return details of this element
        '''
        docstring = "Root element details for: %s\n" % self.name

        docstring += "#"*24
        docstring += "\n"
        docstring += "  Children:\n"
        for key in self.children:
            docstring += "    %s\n" % repr(self.children[key])

        docstring += "#"*24
        docstring += "\n"
        docstring += "  details:\n"
        docstring += self.root.__repr__()

        return docstring

    def verify(self):
        '''verify UIElement is valid or not
        return None if not valid
        '''
        return self.root.verify()

    def start(self, **kwargs):
        '''
        start method will do some initiation for root element
        for windows UIA, just bind UIA root element to driver root interface, no arguments required
        for webdriver API, could pass in some arguments, like browser type, URL, timeout, and start the browser
        '''
        if self.verify() is None:
            self.root.start(**kwargs)

    def stop(self):
        '''
        '''
        if not self.verify() is None:
            self.root.stop()

    def find_element(self, identifier):
        '''find element by identifier
        identifier should already be parsed
        '''
        self.start()
        return self.root.find_element(identifier)

    def find_elements(self, identifier):
        '''find all elements match identifier
        '''
        self.start()
        return self.root.find_elements(identifier)

    def screenshot(self, screenshot_location = ""):
        '''take a screen shot for this element
        '''
        if not os.path.isdir(screenshot_location):
            screenshot_location = self.screenshot_location

        self.start()

        filename = self.name+"_"+str(time.time())+".bmp"
        absfile = os.path.join(screenshot_location, filename)
        if os.path.isfile(absfile):
            os.remove(absfile)

        self.root.screenshot(absfile)
        LOGGER.info("Screenshot taken: %s" , absfile)
        return absfile

    def __getattr__(self, name):
        if name in self.children:
            return self.children[name]
        else:
            self.start()
            return getattr(self.root, name)

class Element(object):
    '''wrapper for UIElement
    hold informations from app map, and provide UIElement interface for app map

    Attributes used internal:
        name:               Element's name, from XML
        parent_string:      Element's parent string, from XML
        identifier_string:  Identifier string, from XML
        timeout:            Time out for this element, from XML
        children:           children elements
        parent:             parent element
        start_func:         function to start this element
        stop_func:          function to stop this element
        identifier:         parsed identifier

        UIElement:          driver interface for UIElement
        find:               function to find first match child element
        findall:            function to find all matched children elements

    Interfaces exposed for use:
        verify:             function to verify if self still exist
        start:              function to start this element
        stop:               function to stop this element
        screenshot:         function to take a screenshot

        other driver special interfaces

    '''
    #fake UI element is for elements without identifier
    fake_UI_element = FakeUIElement()

    def __init__(self):
        #Need init by app map
        self.name = ""
        self.parent_string = ""
        self.identifier_string = ""
        self._time_out = None
        self.children = {}
        self.parent = None
        self.start_func = None
        self.stop_func = None
        self.identifier = None

        #UIElement is assigned by verify method
        self.UIElement = None

    def __repr__(self):
        docstring = "element instance for: %s" % self.name
        return docstring

    @property
    def timeout(self):
        if not self._time_out is None:
            return self._time_out
        else:
            return core_config.time_out

    @timeout.setter
    def timeout(self, input_value):
        self._time_out = input_value

    @property
    def screenshot_location(self):
        return core_config.screenshot_location

    @property
    def screenshot_on(self):
        if core_config.screenshot_option == "always_on":
            return True
        else:
            return False

    @property
    def screenshot_off(self):
        if core_config.screenshot_option == "always_off":
            return True
        else:
            return False

    @property
    def screenshot_on_failure(self):
        if core_config.screenshot_option == "on_failure":
            return True
        else:
            return False

    @property
    def details(self):
        '''return details of this element
        '''
        docstring = "Element details for: %s\n" % self.name

        docstring += "#"*24
        docstring += "\n"
        docstring += "  Parent: %s\n" % repr(self.parent)

        docstring += "#"*24
        docstring += "\n"
        docstring += "  Children:\n"
        for key in self.children:
            docstring += "    %s\n" % repr(self.children[key])

        docstring += "#"*24
        docstring += "\n"
        docstring += "  UIElement details:\n"

        if self.verify() is None:
            docstring += "    UIElement not init or stopped for this Element\n"
        else:
            docstring += self.UIElement.__repr__()

        return docstring

    def verify(self):
        '''verify UIElement is valid or not
        return None if not valid
        '''
        #no identifier
        if self.identifier is None:
            self.UIElement = self.fake_UI_element
        #has identifier
        else:
            self.UIElement = self.parent.find_element(self.identifier)

        return self.UIElement

    def find_element(self, identifier):
        '''find element by identifier
        identifier should already be parsed
        '''
        try:
            if self.UIElement is self.fake_UI_element:
                return self.parent.find_element(identifier)
            else:
                return self.UIElement.find_element(identifier)
        except DriverException:
            #try to update self UIElement and find again
            try:
                self.verify()
                if self.UIElement is self.fake_UI_element:
                    return self.parent.find_element(identifier)
                else:
                    return self.UIElement.find_element(identifier)
            except DriverException:
                #still fail
                return None

    def find_elements(self, identifier):
        '''find all elements match identifier
        '''
        try:
            if self.UIElement is self.fake_UI_element:
                return self.parent.find_elements(identifier)
            else:
                return self.UIElement.find_elements(identifier)
        except DriverException:
            #try to update self UIElement and find again
            try:
                self.verify()
                if self.UIElement is self.fake_UI_element:
                    return self.parent.find_elements(identifier)
                else:
                    return self.UIElement.find_elements(identifier)
            except DriverException:
                #still fail
                return []

    def _wait_start(self):
        '''wait until UIElement is valid or timeout
        '''
        #keep finding the element by identifier, until found or timeout
        LOGGER.info("Waiting Element show up, timeout %s", self.timeout)
        start_time = time.time()
        while True:
            current_time = time.time()
            self.UIElement = self.verify()
            if not self.UIElement is None:
                LOGGER.info("Find element: %s after waiting %ss, continue", self.name, current_time - start_time)
                #do a desktop screenshot here as required
                if self.screenshot_on:
                    #get root
                    element = self
                    parent = element.parent
                    while not parent is None:
                        element = parent
                        parent = element.parent
                    #screenshot
                    element.screenshot()
                return

            time.sleep(0.1)
            if current_time - start_time > self.timeout:
                #do a desktop screenshot here as required
                if not self.screenshot_off:
                    #get root
                    element = self
                    parent = element.parent
                    while not parent is None:
                        element = parent
                        parent = element.parent
                    #screenshot
                    element.screenshot()
                raise TimeOutError("time out encounter, during start element:%s" % self.name)

    def start(self):
        '''start and find this UIElement
        '''
        #need to start parent element first
        self.parent.start()
        if self.verify() is None:
            LOGGER.info("Start function triggered, due to cannot find element: %s", self.name)
            #run start func
            if self.start_func:
                self.start_func.run()
            else:
                LOGGER.info("Element doesn't have start function")
            self._wait_start()
        else:
            LOGGER.info("Find element: %s, continue", self.name)

    def _wait_stop(self):
        '''wait until UIElement is not valid or timeout
        '''
        LOGGER.info("Waiting Element to stop, timeout %s" % self.timeout)
        if not self.identifier is None:
            #keep verify the element, until not found or timeout
            start_time = time.time()
            while True:
                self.UIElement = self.verify()
                if self.UIElement is None:
                    return

                time.sleep(0.1)
                current_time = time.time()
                if current_time - start_time > self.timeout:
                    raise TimeOutError("time out encounter, during stop element:%s" % self.name)

    def stop(self):
        '''stop and verify this UIElement
        Need to stop all children first
        '''
        if not self.verify() is None:
            #stop all children
            for name in self.children:
                self.children[name].stop()

            #stop self
            #only stop and check element which has stop_func attribute
            LOGGER.info("Find element %s, trigger stop function", self.name)
            if self.stop_func:
                self.stop_func.run()
            else:
                LOGGER.info("Element doesn't have stop function")
            self._wait_stop()
        else:
            LOGGER.info("Not find element %s, continue", self.name)

    def screenshot(self, screenshot_location = ""):
        '''take a screen shot for this element
        '''
        if not os.path.isdir(screenshot_location):
            screenshot_location = self.screenshot_location

        self.start()

        filename = self.name+"_"+str(time.time())+".bmp"
        absfile = os.path.join(screenshot_location, filename)
        if os.path.isfile(absfile):
            os.remove(absfile)

        self.UIElement.screenshot(absfile)
        LOGGER.info("Screenshot taken: %s" , absfile)
        return absfile

    def __getattr__(self, name):
        if name in self.children:
            return self.children[name]
        else:
            self.start()
            return getattr(self.UIElement, name)

class ElementGroup(object):
    '''
    '''
    def __init__(self):
        #Need init by app map
        self.name = ""
        self.parent_string = ""
        self.identifier_string = ""
        #move this to config later
        self.timedelay = 2
        self.parent = None
        self.start_func = None
        self.stop_func = None
        self.identifier = None

        #Elements is assigned dynamicly during runtime
        self.Elements = []

    def __repr__(self):
        docstring = "elementgroup instance for: %s" % self.name
        return docstring

    def start(self):
        '''start and findall UIElements, build Elements automatically
        '''
        #need to start parent element first
        self.parent.start()
        #run start func
        if self.start_func:
            self.start_func.run()
        #delay some time
        time.sleep(self.timedelay)
        #find and create all matched elements
        UIElements = self.parent.find_elements(self.identifier)

        for i, UIElement in enumerate(UIElements):
            element = Element()
            element.parent = self.parent
            if self.identifier is None:
                element.identifier = ["Index", i]
            else:
                element.identifier = ("AND", self.identifier, ("Index", i))
            element.UIElement = UIElement
            #Name property is not available for appium driver 
            #element.name = UIElement.Name

            self.Elements.append(element)

        return self.Elements

    def stop(self):
        '''stop this Element group
        '''
        #stop self
        #only stop element which has stop_func attribute
        if self.stop_func:
            self.stop_func.run()

    def __getitem__(self, index):
        self.start()
        return self.Elements[index]

    def __iter__(self):
        self.start()
        return iter(self.Elements)

    def __len__(self):
        self.start()
        return len(self.Elements)
