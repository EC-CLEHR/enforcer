import enum
import json
import os
from datetime import datetime

from selenium.common.exceptions import (TimeoutException, NoSuchElementException,
                                        WebDriverException,
                                        NoSuchFrameException, StaleElementReferenceException,
                                        InvalidArgumentException, ElementNotSelectableException)
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select, WebDriverWait

from src.lib.helper import constant, config_file
from src.lib.helper import log_helper, browser_console_log
from src.lib.helper.custom_exceptions import WebdriverOptionMissingException
from src.lib.helper.support import get_locator, get_current_datetime, \
    get_geckodriver_console_logs

driver_type = WebDriver


class LocatorType(enum.Enum):
    id = 1
    name = 2
    class_name = 3
    link_text = 4
    tag_name = 5
    partial_link_text = 6
    css = 7
    xpath = 8


class SeleniumExtension:
    """
    Selenium wrapper class for all the built-in methods.
    """

    def __init__(self):
        self.log = log_helper.Logging
        self.take_screenshot = config_file.TAKE_SCREENSHOT

    wait_time = config_file.EXPLICIT_WAIT_TIME
    driver: driver_type = None

    def get_by_type(self, locator_type):
        """
        Gets the type from selenium By class.
        :param locator_type: type of locator.
        :return: By type of locator.
        """
        start_time = datetime.now()
        log_info = "Locator type " + \
                   str(locator_type) + " is not correct or supported"
        locator = {"id": By.ID,
                   "name": By.NAME,
                   "class_name": By.CLASS_NAME,
                   "link_text": By.LINK_TEXT,
                   "tag_name": By.TAG_NAME,
                   "partial_link_text": By.PARTIAL_LINK_TEXT,
                   "css": By.CSS_SELECTOR,
                   "xpath": By.XPATH
                   }

        if locator_type not in locator:
            self.log.write_message_error("Locator type exception occurred- " + log_info,
                                         self.driver.current_url, start_time)
            raise AttributeError
        return locator[locator_type]

    def get_title(self):
        """
        Used to get the current title of browser.
        :return: browser title.
        """
        return self.driver.title

    def wait_to_redirect(self, url_contains, timeout=wait_time):
        """
        Waits for a page to redirect.
        :type url_contains: string url contains
        :param timeout: time wait
        :return: none
        """
        start_time = datetime.now()
        try:
            current_url = self.driver.current_url
            wait = WebDriverWait(self.driver, timeout)
            if url_contains is not None:
                wait.until(expected_conditions.url_contains(url_contains))
            else:
                wait.until(lambda driver: driver.current_url != current_url)
        except TimeoutException as te:
            msg = "Exception occurred while navigating new page and validating url with :" + \
                  url_contains
            self.log.write_message_error(
                msg, url=self.driver.current_url, start_time=start_time)
            self.log.write_message_exception(te)
            raise te

    def wait_for_page_load(self, timeout=wait_time):
        """
        Waits for document state to be ready.
        :return: none
        """
        start_time = datetime.now()
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(lambda driver: self.driver.execute_script(
                'return document.readyState === "complete"'))
        except TimeoutException as te:
            msg = "Exception occurred while loading the page"
            self.log.write_message_error(
                msg, url=self.driver.current_url, start_time=start_time)
            self.log.write_message_exception(te)
            raise te

    def select_element(self, locator_info, timeout=wait_time):
        """
        To interact with Select type locators.
        :param locator_info: contains unique locator type and locator.
        :param timeout: wait time.
        :return: Select class object.
        """
        if not self.is_element_present(locator_info):
            raise NoSuchElementException
        element = self.get_element(locator_info, timeout)
        return Select(element)

    def get_elements(self, locator_info, timeout=wait_time):
        """
        To find the element in DOM to interact with.
        :param locator_info: unique locator and locator type.
        :param timeout: wait time.
        :return: identified web element.
        """
        elements = None
        start_time = datetime.now()
        self.wait_for_page_load()
        counter = 0
        attempts = 0
        if self.driver.name == "Safari":
            attempts = 1
        while counter <= attempts:
            elements = self.wait_for_elements_to_be_present(
                locator_info, timeout)
            if elements:
                break
            counter += 1
        if elements is None:
            raise NoSuchElementException
        self.log.write_message_info(
            "Elements found with " + str(locator_info), start_time=start_time)
        return elements

    def get_element(self, locator_info, timeout=wait_time):
        """
        To find the element in DOM to interact with.
        :param locator_info:  unique locator and locator type.
        :param timeout: wait time.
        :return: identified web element.
        """
        element = None
        start_time = datetime.now()
        self.wait_for_page_load()
        counter = 0
        attempts = 0
        if self.driver.name == "Safari":
            attempts = 1
        while counter <= attempts:
            element = self.wait_for_element_to_be_visible(
                locator_info, timeout, counter, attempts)
            if element:
                break
            counter += 1
        if element is None:
            raise NoSuchElementException
        self.log.write_message_info(
            "Element found with " + str(locator_info), start_time=start_time)
        return element

    def get_text_of_selected_option(self, locator_info, timeout=wait_time):
        """
        To capture the text of an option in a drop down.
        :param locator_info: unique locator and locator type.
        :param timeout: wait time.
        :return: text of option.
        """
        return self.select_element(locator_info, timeout).first_selected_option.text

    def element_click(self,
                      locator_info: dict = None,
                      timeout=wait_time,
                      element: WebElement = None
                      ):
        """
        To find the web element and clicking.
        :param locator_info: contains unique locator type and locator.
        :param timeout: wait time
        :param element: WebElement
        :return: none.
        """
        start_time = datetime.now()
        message = f"Clicked on element with text: {element.text if element else None}"
        if not element:
            element_exists = self.is_element_present(locator_info)
            if element_exists is False:
                raise NoSuchElementException
            element = self.get_element(locator_info, timeout)
            self.wait_for_element_to_be_clickable(locator_info, timeout)
            message = "Clicked on element with " + str(locator_info)
        self.scroll_element_to_view(element)
        element.click()
        self.log.write_message_info(message, start_time=start_time)

    def is_selected(self, locator_info, timeout=wait_time):
        """
        Checking if the checkbox is checked.
        :param locator_info: contains unique locator type and locator.
        :param timeout: wait time
        :return: bool
        """
        element = self.wait_for_element_to_be_present(locator_info, timeout)
        self.scroll_element_to_view(element)
        return element.is_selected()

    def select_checkbox(self, locator_info, timeout=wait_time):
        """
        To select an unchecked checkbox.
        :param locator_info: contains unique locator type and locator.
        :param timeout: wait time
        :return: none.
        """
        element = self.wait_for_element_to_be_present(locator_info, timeout)
        self.scroll_element_to_view(element)
        if not element.is_selected():
            self.js_click(locator_info)
            if not element.is_selected():
                raise ElementNotSelectableException('Checkbox is not checked')
        else:
            self.log.write_message_info('checkbox is already checked')

    def deselect_checkbox(self, locator_info, timeout=wait_time):
        """
        To deselect an already checked checkbox.
        :param locator_info: contains unique locator type and locator.
        :param timeout: wait time
        :return: none.
        """
        element = self.wait_for_element_to_be_present(locator_info, timeout)
        self.scroll_element_to_view(element)
        if element.is_selected():
            self.js_click(locator_info)
            if element.is_selected():
                raise ElementNotSelectableException('Checkbox is not checked')
        else:
            self.log.write_message_info('checkbox is already unchecked')

    def js_click(self, locator_info: dict = None, timeout=wait_time, element: WebElement = None):
        """
        To find the web element and clicking.
        :param locator_info: contains unique locator type and locator.
        :param timeout:  wait time
        :param element:  WebElement
        :return: none.
        """
        start_time = datetime.now()
        try:
            element = element if element else self.wait_for_element_to_be_present(
                locator_info, timeout)
            if element:
                self.driver.execute_script("arguments[0].click();", element)
                self.log.write_message_info(
                    "Clicked on element with " + str(locator_info), start_time=start_time)
            else:
                raise NoSuchElementException
        except Exception as ex:
            msg = "Unable to click on element using javascript click."
            if not element:
                msg = "Unable to click on element : '" + \
                      str(locator_info) + "' using javascript click."
            self.log.write_message_error(
                msg, url=self.driver.current_url, start_time=start_time)
            raise ex

    def send_text(self,
                  data,
                  locator_info: dict = None,
                  timeout=wait_time,
                  element: WebElement = None
                  ):
        """
        To find the element and sending data to that element.
        :param data: data to be sent to the element.
        :param locator_info: contains unique locator type and locator.
        :param element:  WebElement
        :param timeout:  wait time
        :return: none.
        """
        start_time = datetime.now()
        message = f"Entered '{data}' in element with text {element.text if element else None}"
        if not element:
            if not self.is_element_present(locator_info):
                raise NoSuchElementException
            element = self.get_element(locator_info, timeout)
            message = "Entered '" + data + "' in element " + str(locator_info)
        self.scroll_element_to_view(element)
        element.clear()
        element.send_keys(data)
        self.log.write_message_info(message, start_time=start_time)

    def send_sensitive_text(self, data, locator_info, timeout=wait_time):
        """
        To find the element and sending data to an sensitive element such as password.
        :param data: data to be sent to the element.
        :param locator_info: contains unique locator type and locator.
        :param timeout:  wait time
        :return: none.
        """
        try:
            start_time = datetime.now()
            if not self.is_element_present(locator_info):
                raise NoSuchElementException
            element = self.get_element(locator_info, timeout)
            self.scroll_element_to_view(element)
            element.clear()
            log_helper.Logging.disable_log()
            element.send_keys(data)
        except Exception:
            msg = "Element is not present with " + str(locator_info)
            self.log.write_message_error(
                msg, url=self.driver.current_url, start_time=start_time)
        finally:
            log_helper.Logging.enable_log()

    def is_element_present(self, locator_info, timeout=wait_time):
        """
        To verify whether the element is present on DOM.
        :param locator_info: contains unique locator type and locator.
        :param timeout: wait time.
        :return: bool
        """
        start_time = datetime.now()
        result = False
        try:
            element = self.get_element(locator_info, timeout)
            if element:
                self.log.write_message_info("Element is present with " + str(locator_info),
                                            start_time=start_time)
                result = True
        except Exception:
            msg = "Element is not present with " + str(locator_info)
            self.log.write_message_error(
                msg, url=self.driver.current_url, start_time=start_time)
        return result

    def wait_for_element_to_be_visible(self, locator_info, timeout=wait_time, limit=0, max_limit=0):
        """
        To wait for an element is present on the DOM of a page and visible.
        :param locator_info: contains unique locator type and locator.
        :param timeout: time to wait.
        :param limit: counter
        :param max_limit: max limit counter
        :return: web element
        """
        start_time = datetime.now()
        locator_type, locator_value = get_locator(locator_info)
        try:
            by_type = self.get_by_type(locator_type)
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(
                expected_conditions.visibility_of_element_located((by_type, locator_value)))
        except TimeoutException as te:
            msg = f"element is not displayed due to time-out exception with {str(locator_info)}"
            self.log.write_message_error(
                msg, url=self.driver.current_url, start_time=start_time)
            self.log.write_message_exception(te)
            # if limit and max_limit are same then exception will throw
            if limit == max_limit:
                raise te
        except WebDriverException as de:
            msg = "element is not displayed with " + str(locator_info)
            self.log.write_message_error(
                msg, url=self.driver.current_url, start_time=start_time)
            self.log.write_message_exception(de)
            if limit == max_limit:
                raise de

    def wait_for_elements_to_be_present(self,
                                        locator_info,
                                        timeout=wait_time,
                                        limit=0,
                                        max_limit=0):
        """
        To wait for elements is present on the DOM of a page
        :param locator_info: contains unique locator type and locator.
        :param timeout: time to wait.
        :param limit: counter
        :param max_limit: max limit counter
        :return: web element
        """
        locator_type, locator_value = get_locator(locator_info)
        start_time = datetime.now()
        try:
            by_type = self.get_by_type(locator_type)
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(
                expected_conditions.presence_of_all_elements_located((by_type, locator_value)))
        except TimeoutException as te:
            msg = "element is not displayed due to time-out exception with " + \
                  str(locator_info)
            self.log.write_message_error(msg, url=self.driver.current_url, start_time=start_time)
            self.log.write_message_exception(te)
            if limit == max_limit:
                raise te
        except WebDriverException as de:
            msg = "element is not displayed with " + str(locator_info)
            self.log.write_message_error(
                msg, url=self.driver.current_url, start_time=start_time)
            self.log.write_message_exception(de)
            if limit == max_limit:
                raise de

    def wait_for_element_to_be_clickable(self, locator_info, timeout=wait_time):
        """
        To wait for an element to click  explicitly.
        :param locator_info:  contains unique locator type and locator.
        :param timeout: time to wait.
        :return: Web element
        """
        locator_type, locator_value = get_locator(locator_info)
        start_time = datetime.now()
        try:
            by_type = self.get_by_type(locator_type)
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(
                expected_conditions.element_to_be_clickable((by_type, locator_value)))
        except TimeoutException as te:
            msg = "element is not clickable with " + str(locator_info)
            self.log.write_message_error(
                msg, url=self.driver.current_url, start_time=start_time)
            self.log.write_message_exception(te)
            raise te
        return element

    def switch_to_frame(self, locator_info, timeout=wait_time):
        """
        To find the Frame and Switch.
        :param locator_info : contains unique locator type and locator.
        :param timeout: wait time
        :return: none.
        """
        start_time = datetime.now()
        locator_type, locator_value = get_locator(locator_info)
        try:
            by_type = self.get_by_type(locator_type)
            wait = WebDriverWait(self.driver, timeout)
            self.driver.switch_to.default_content()
            wait.until(
                expected_conditions.frame_to_be_available_and_switch_to_it(
                    (by_type, locator_value)))
            self.log.write_message_info(
                "Switched to frame  with " + str(locator_info), start_time=start_time)
        except NoSuchFrameException as ex:
            msg = "cannot switched to frame  with " + str(locator_info)
            self.log.write_message_error(
                msg, url=self.driver.current_url, start_time=start_time)
            self.log.write_message_exception(ex)
            raise ex

    def get_attribute_value(self, attribute, locator_info, timeout=wait_time):
        """
        To find the element and get attribute value of that element.
        :param attribute: attribute from which value to be needed.
        :param locator_info : contains unique locator type and locator.
        :param timeout: wait time
        :return: none.
        """
        start_time = datetime.now()
        try:
            element = self.get_element(locator_info, timeout)
            attribute_value = element.get_attribute(attribute)
            message = "Attribute value {attribute_value} on element with {log_info} is retrieved". \
                format(attribute_value=attribute_value,
                       log_info=str(locator_info))
            self.log.write_message_info(message, start_time=start_time)
            return attribute_value
        except WebDriverException as ex:
            self.log.write_message_error(
                "cannot get attribute value on the element with " + str(locator_info),
                url=self.driver.current_url,
                start_time=start_time)
            self.log.write_message_exception(ex)
            raise ex

    def get_value_of_css_property(self, prop, locator_info, timeout=wait_time):
        """
        To find the element and get value of css property.
        :param prop: property from which value to be needed.
        :param locator_info : contains unique locator type and locator.
        :param timeout: wait time
        :return: none.
        """
        start_time = datetime.now()
        try:
            element = self.get_element(locator_info, timeout)
            prop_value = element.value_of_css_property(prop)
            message = "Property value {prop_value} on element with {locator_info} is " \
                      "retrieved".format(prop_value=prop_value, locator_info=str(locator_info))
            self.log.write_message_info(message, start_time=start_time)
            return prop_value
        except WebDriverException as ex:
            self.log.write_message_error(
                "cannot get property value on the element with {locator_info}".format(
                    locator_info=str(locator_info)),
                url=self.driver.current_url,
                start_time=start_time)
            self.log.write_message_exception(ex)
            raise ex

    def scroll_element_to_view(self, element):
        """
        Scrolls web-element to middle of screen.
        :param self:
        :param element: web-element
        :return: none
        """
        start_time = datetime.now()
        try:
            scroll_element_to_middle = """var viewPortHeight = Math.max(
            document.documentElement.clientHeight,
            window.innerHeight || 0);
                                       var elementTop = arguments[0].getBoundingClientRect().top;
                                       window.scrollBy(0, elementTop-(viewPortHeight/2));
                                       """
            self.driver.execute_script(scroll_element_to_middle, element)
        except WebDriverException as ex:
            self.log.write_message_error("issue with scroll element to view",
                                         url=self.driver.current_url,
                                         start_time=start_time)
            self.log.write_message_exception(ex)
            raise ex

    def wait_until_text_to_be_present_in_element(self, locator_info, text, timeout=wait_time):
        """
        To wait until the text to be present in element .
        :param locator_info:  contains unique locator type and locator.
        :param text: string to be searched for in text of element found by locator_info
        :param timeout: maximum time to wait for text to appear
        :return: Web element
        """
        locator_type, locator_value = get_locator(locator_info)
        start_time = datetime.now()
        try:
            by_type = self.get_by_type(locator_type)
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(expected_conditions.
                                 text_to_be_present_in_element((by_type, locator_value), text))
        except TimeoutException as te:
            msg = f"{text} is not present in the element {locator_info}"
            self.log.write_message_error(msg, url=self.driver.current_url, start_time=start_time)
            self.log.write_message_exception(te)
            raise te
        return element

    def wait_for_element_to_be_present(self, locator_info, timeout=wait_time):
        """
        To wait for an element is present on the DOM of a page.
        :param locator_info: contains unique locator type and locator..
        :param timeout: wait time.
        :return: Web element
        """
        start_time = datetime.now()
        locator_type, locator_value = get_locator(locator_info)
        try:
            by_type = self.get_by_type(locator_type)
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(expected_conditions.presence_of_element_located((by_type,
                                                                                  locator_value)))
        except TimeoutException as te:
            msg = "element is not present with " + str(locator_info)
            self.log.write_message_error(
                msg, url=self.driver.current_url, start_time=start_time)
            self.log.write_message_exception(te)
            raise te
        return element

    def switch_to_default_content(self):
        """
        Switch to default frame.
        :return: none.
        """
        start_time = datetime.now()
        try:
            self.driver.switch_to.default_content()
            self.log.write_message_info(
                "Switched to  default frame/content ", start_time=start_time)
        except Exception as ex:
            msg = "Failed switching to default frame/content "
            self.log.write_message_error(
                msg, url=self.driver.current_url, start_time=start_time)
            self.log.write_message_exception(ex)
            raise ex

    def double_click(self,
                     locator_info: dict = None,
                     timeout=wait_time,
                     element: WebElement = None):
        """
        To perform double click action
        :param locator_info: contains unique locator type and locator.
        :param element: WebElement
        :param timeout: wait time
        :return: none
        """
        start_time = datetime.now()
        self.wait_for_page_load()
        try:
            message = f"Double click on element with text {element.text if element else None}"
            actions = ActionChains(self.driver)
            if not element:
                element = self.get_element(locator_info, timeout)
                message = "Double click with " + str(locator_info)
            actions.double_click(element).perform()
            self.log.write_message_info(message, start_time=start_time)
        except WebDriverException as ex:
            msg = f"Cannot double click on the element with text " \
                  f"{element.text if element else None}"
            if not element:
                msg = f"Cannot double click on the element with locator {locator_info}"
            self.log.write_message_error(
                msg, url=self.driver.current_url, start_time=start_time)
            self.log.write_message_exception(ex)
            raise ex

    def wait_for_element_to_be_staleness(self, locator_info, timeout=wait_time):
        """
        To wait until an element is no longer stale to the DOM
        :param locator_info:  contains unique locator type and locator.
        :param timeout: time to wait.
        :return: Web element
        """

        start_time = datetime.now()
        try:
            element = self.get_element(locator_info, timeout)
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(expected_conditions.staleness_of(element))
            self.log.write_message_info(
                "element refreshed with " + str(locator_info), start_time=start_time)
        except TimeoutException as te:
            msg = "element is not longer valid " + str(locator_info)
            self.log.write_message_error(
                msg, url=self.driver.current_url, start_time=start_time)
            self.log.write_message_exception(te)
            raise te
        return element

    def drag_and_drop_single_object(self,
                                    source_path,
                                    target_element,
                                    offset_x=0,
                                    offset_y=0,
                                    timeout=wait_time):
        """
        Executes drag and drop on the Browser for single object
        :param source_path: source path of obj file
        :param target_element: element or locator where files are dropped
        :param offset_x: x axis location
        :param offset_y: y axis location
        :param timeout: wait time for the document to load
        :return: None
        """
        js_image_object = """
                   var target = arguments[0],
                       offsetX = arguments[1],
                       offsetY = arguments[2],
                       document = target.ownerDocument || document,
                       window = document.defaultView || window;

                   var input = document.createElement('INPUT');
                   input.type = 'file';
                   input.onchange = function () {
                     var rect = target.getBoundingClientRect(),
                         x = rect.left + (offsetX || (rect.width >> 1)),
                         y = rect.top + (offsetY || (rect.height >> 1)),
                         dataTransfer = { files: this.files };

                     ['dragenter', 'dragover', 'drop'].forEach(function (name) {
                       var evt = document.createEvent('MouseEvent');
                       evt.initMouseEvent(name, !0, !0, window, 0, 0, 0, x, y, !1, !1, !1, !1, 0,
                       null);
                       evt.dataTransfer = dataTransfer;
                       target.dispatchEvent(evt);
                     });

                     setTimeout(function () { document.body.removeChild(input); }, arguments[3]);
                   };
                   document.body.appendChild(input);
                   return input;
                   """
        input_element = self.driver.execute_script(
            js_image_object, target_element, offset_x, offset_y)
        input_element.send_keys(source_path)
        wait = WebDriverWait(self.driver, timeout)
        wait.until(expected_conditions.staleness_of(input_element))

    def drag_and_drop_multiple_objects(self, source_path, target_element, objects_count,
                                       relative_offset_x=10,
                                       relative_offset_y=10, timeout=wait_time):
        """
        Executes drag and drop on the Browser for multiple objects
        :param source_path: source path of files
        :param target_element: element or locator where files are dropped
        :param objects_count: number of objects/files to upload
        :param relative_offset_x: x axis relative location offset per object
        :param relative_offset_y: y axis relative location offset per object
        :param timeout: wait time for the document to load
        :return: None
        """
        for i in objects_count:
            self.drag_and_drop_single_object(source_path, target_element,
                                             (i - 1) * relative_offset_x,
                                             (i - 1) * relative_offset_y,
                                             timeout)

    def wait_for_element_to_disappear(self, locator_info, timeout=wait_time):
        """
        To wait for an element to disappear on the DOM of a page.
        :param locator_info: contains unique locator type and locator.
        :param timeout: wait time.
        :return: boolean
        """
        start_time = datetime.now()
        locator_type, locator_value = get_locator(locator_info)
        try:
            by_type = self.get_by_type(locator_type)
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(
                expected_conditions.invisibility_of_element_located((by_type, locator_value)))
        except TimeoutException as te:
            msg = "element {locator} didn't disappear".format(
                locator=locator_value)
            self.log.write_message_error(
                msg, self.driver.current_url, start_time)
            self.log.write_message_exception(te)
            raise te

    # TO DO: ENG-23805 - Create hook wrapper for capture screenshot method

    @classmethod
    def enable_screenshot(cls):
        """To enable screenshot capture before a particular step"""
        cls.take_screenshot = True

    @classmethod
    def disable_screenshot(cls):
        """To disable screenshot capture at any step"""
        cls.take_screenshot = False

    def capture_screenshot(self, config):
        """
        Takes a screen shot.
        :param config: pytest config
        :return: image_relative_path returns  the relative path to attach in the report

        Args:
            config: pytest config
        """
        try:
            # file format: test_smile_assessment-smileshops-20200219201531.png
            # TO DO: ENG-23804 - Explore screenshot formats other than PNG

            # trying get the page where failure occurred and appending in image title
            # ex : https://staging.smiledirectclub.com/smileshops/
            # We will get the 'smileshops' from the url and append to the image title

            if not config_file.TAKE_SCREENSHOT:
                self.log.write_message_info("########Screenshot skipped########")
                return None

            test_case_name = os.environ.get(
                'PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]
            url = self.driver.current_url.split('/')
            if len(url) > 3:
                test_case_name = test_case_name + "-" + url[3]

            file_name = test_case_name + "-" + get_current_datetime() + ".png"
            screenshot_dir_absolutepath = os.path.join(
                config_file.SCREENSHOT_BASE_DIR, config_file.SCREENSHOT_DIR_RELATIVE_PATH)

            # Capture & save Image file
            image_full_path = os.path.join(
                screenshot_dir_absolutepath, file_name)
            normal_image_path = self.create_dir_and_save_screenshot(screenshot_dir_absolutepath,
                                                                    image_full_path)
            base_64_image_full_path = None
            if config.getoption('--base64'):
                base_64_image_full_path = "data:image/jpeg;base64," \
                                                       "" + self.driver.get_screenshot_as_base64()
            return normal_image_path, base_64_image_full_path
        except Exception as ex:
            self.log.write_message_exception(
                ex, message="Exception occurred while taking screen shot:")

    def create_dir_and_save_screenshot(self, screenshot_dir_absolutepath, image_full_path):
        # Creates a dir if not exists
        if not os.path.exists(screenshot_dir_absolutepath):
            os.makedirs(screenshot_dir_absolutepath)
        screenshot_taken = self.driver.get_screenshot_as_file(image_full_path)
        if not screenshot_taken:
            self.log.write_message_error("*** Screenshot capture failed. ***")
            return None
        self.log.write_message_info("*** Screenshot taken ***")
        screenshot_size = round(os.stat(image_full_path).st_size / 1024)
        if screenshot_size > 0:
            self.log.write_message_info("*** Screens size:" + str(
                screenshot_size) + "kbs. \n Screenshot absolute path: " +
                                        image_full_path)
            return image_full_path
        self.log.write_message_error(
            "*** Problem with taken screenshot. Its size is not > 0. ***")
        return None

    def send_keys_enter(self):
        """
        Clicks keyboard ENTER key
        :return: None
        """
        start_time = datetime.now()
        self.wait_for_page_load()
        try:
            actions = ActionChains(self.driver)
            actions.send_keys(Keys.ENTER)
            actions.perform()
            self.log.write_message_info(
                "Clicked Enter key", start_time=start_time)
        except WebDriverException as ex:
            msg = "Cannot click Enter key from keyboard"
            self.log.write_message_error(msg, start_time=start_time)
            self.log.write_message_exception(ex)
            raise ex

    def wait_for_all_images_to_load(self, timeout=wait_time):
        """
        To wait for all images in the page to load
        :param timeout: wait time
        """
        start_time = datetime.now()
        scroll_element_to_middle = """var viewPortHeight = Math.max(
        document.documentElement.clientHeight,
                                   window.innerHeight || 0);
                                                              var elementTop = arguments[
                                                              0].getBoundingClientRect().top;
                                                              window.scrollBy(0, elementTop-(
                                                              viewPortHeight/2));"""
        all_images = self.driver.find_elements_by_tag_name('img')
        for each_ele in all_images:
            try:
                self.driver.execute_script(scroll_element_to_middle, each_ele)
                wait = WebDriverWait(self.driver, timeout=timeout)
                if 'visibility: hidden' not in each_ele.get_attribute('style'):
                    wait.until(lambda driver: driver.execute_script(
                        "return arguments[0].complete && typeof arguments[0].naturalWidth != "
                        "\"undefined\"\n"
                        " && arguments[0].naturalWidth > 0", each_ele))
            except StaleElementReferenceException:
                continue
            except WebDriverException as ex:
                self.log.write_message_error(
                    "Issue while waiting for images load " + str(ex), start_time=start_time)
                continue
        self.driver.execute_script("window.scrollTo(0, 0);")

    def send_number(self, number, locator_info, timeout=wait_time):
        """
        To enter number
        :param number: number to enter
        :param locator_info: locator
        :param timeout: wait time out
        """
        start_time = datetime.now()
        try:
            element = self.get_element(locator_info, timeout)
            self.scroll_element_to_view(element)
            element.send_keys(Keys.CONTROL + 'a')
            element.send_keys(Keys.BACKSPACE)
            number = number.replace('', ' ').strip().split()
            for each_digit in number:
                element.send_keys(each_digit)
            self.log.write_message_info(
                "Entered '" + str(number) + "' in element " + str(locator_info),
                start_time=start_time)
        except WebDriverException as ex:
            msg = "Cannot send number into field "
            self.log.write_message_error(
                msg + str(locator_info), start_time=start_time)
            self.log.write_message_exception(ex)
            raise ex

    def activate_window(self, window_title=None, window_url=None, window_handle=None):
        """
        Used to activate a specific window based on either window title or url or handle
        :param window_title: Title of window to activate
        :param window_url: URL of window to activate
        :param window_handle: Window handle to activate
        :return: None
        """
        start_time = datetime.now()
        try:
            if not (window_title or window_url or window_handle):
                return self.log.write_message_info(
                    "Neither window title nor url nor handle is provided. So default "
                    "window is active", start_time=start_time)
            handles = self.driver.window_handles
            for handle in handles:
                self.driver.switch_to.window(handle)
                title, url = self.get_title(), self.driver.current_url
                if (title == window_title) or (url == window_url) or (handle == window_handle):
                    return self.log.write_message_info(
                        f"Activated window with title: {title}, URL: {url}",
                        start_time=start_time)

        except WebDriverException as ex:
            msg = "Unable to activate window"
            self.log.write_message_error(msg, start_time=start_time)
            self.log.write_message_exception(ex)
            raise ex

    def get_active_window_handle(self):
        """
        Used to get the active window handle
        :return: Current window handle
        """
        start_time = datetime.now()
        try:
            self.log.write_message_debug(
                "Returning active window handle", start_time=start_time)
            return self.driver.current_window_handle
        except WebDriverException as ex:
            msg = "Unable to get active window handle"
            self.log.write_message_error(msg, start_time=start_time)
            self.log.write_message_exception(ex)
            raise ex

    def close_window(self, window_title=None, window_url=None, window_handle=None):
        """
        Used to close a window when multiple windows are opened
        :param window_title: Title of window to close
        :param window_url: URL of window to close
        :param window_handle: Window handle to close
        :return: log message / None
        """
        start_time = datetime.now()
        try:
            if not (window_title or window_url or window_handle):
                return self.log.write_message_info(
                    "Please provide either title or url or handle to close window",
                    start_time=start_time)
            handles = self.driver.window_handles
            size = len(handles)
            if not (size > 1):
                return self.log.write_message_info("Can not close default/only-available window",
                                                   start_time=start_time)
            """Close the window if there is more that one window,
            and matches with title, url or handle"""
            for handle in handles:
                self.driver.switch_to.window(handle)
                title, url = self.get_title(), self.driver.current_url
                if (title == window_title) or (url == window_url) or (handle == window_handle):
                    self.driver.close()
                    self.log.write_message_info(f"Window with title: {title}, URL: {url} is closed",
                                                start_time=start_time)
                    break
            'After closing the window, activate the last window'
            handles = self.driver.window_handles
            if len(handles) < size:
                for handle in handles:
                    last_window_handle = handle
                self.driver.switch_to.window(last_window_handle)
                title, url = self.get_title(), self.driver.current_url
                self.log.write_message_info(f"Switched to Window with title: {title}, URL: {url}",
                                            start_time=start_time)
        except WebDriverException as ex:
            msg = "Unable to close window"
            self.log.write_message_error(msg, start_time=start_time)
            self.log.write_message_exception(ex)
            raise ex

    def get_driver_log(self, log_type):
        """
        To get performance events.
        In order to use this method, `performance` item should be present in
        logging_prefs dict of WebDriverFactory.
        :return: dict of performance events
        """
        try:
            if log_type not in ('browser', 'performance'):
                raise ValueError(
                    'Given param {} is not supported. Please pass either "browser" or '
                    '"performance"') \
                    .__format__(log_type)
            if self.driver.name == 'chrome':
                browser_log = self.driver.get_log(log_type)
            elif log_type == 'browser' and self.driver.name == 'firefox':
                browser_log = get_geckodriver_console_logs(
                    self.driver.service.log_file.name)
            else:
                return None
        except InvalidArgumentException as invalid_argument_exception:
            message = "Cannot get {0} log. Check if the {0} item exists in logging_prefs dict of " \
                      "WebDriverFactory." \
                .format(log_type)
            self.log.write_message_error(message)
            self.log.write_message_exception(invalid_argument_exception)
            raise WebdriverOptionMissingException(message)

        if log_type == 'browser':
            return browser_log
        elif log_type == 'performance':
            return [json.loads(entry['message'])['message']
                    for entry in browser_log]

    def get_browser_network_log(self):
        """
        To get network events.
        In order to use this method, `performance` item should be present in
        logging_prefs dict of WebDriverFactory.
        :return: dict of network events
        """
        performance_log = self.get_driver_log('performance')

        return [entry for entry in performance_log
                if entry['method'].startswith('Network')]

    def filter_browser_log(self, keyword=None, level=None):
        """
            To get console log for log level.
            In order to use this method, the value of `browser` should be True
            in logging_prefs dict of WebDriverFactory and @WebDriverLogging.log_browser_events()
            should be used for the script.
            * Filtering by level is only available for Chrome webdriver
            :return: dict of events containing the keyword in the message attribute for the level
            specified
        """
        console_log = self.get_driver_log('browser')
        if self.driver.name == 'chrome':
            return browser_console_log.filter_log(console_log, keyword, level)
        else:
            return browser_console_log.filter_log(console_log, keyword)

    def filter_browser_log_timestamps_for_keyword(self, keyword):
        """
            To get console log for log level.
            In order to use this method, the value of `browser` should be True
            in logging_prefs dict of WebDriverFactory and @WebDriverLogging.log_browser_events()
            should be used for the script.
            * For Chrome webdriver only.
            :return: list of timestamps corresponding to the keyword present in the message
            attribute
        """
        console_log = self.get_driver_log('browser')
        return browser_console_log.get_timestamps(console_log, keyword)

    def filter_browser_log_levels_for_keyword(self, keyword):
        """
            To get console log for log level.
            In order to use this method, the value of `browser` should be True
            in logging_prefs dict of WebDriverFactory and @WebDriverLogging.log_browser_events()
            should be used for the script.
            :return: list of levels corresponding to the keyword present in the message attribute
        """
        console_log = self.get_driver_log('browser')
        return browser_console_log.get_levels(console_log, keyword)

    def switch_to_alert(self):
        """
        Used to switch to alert
        :return: alert reference
        """
        wait = WebDriverWait(self.driver, constant.WAIT_TIME_SMALL)
        wait.until(expected_conditions.alert_is_present())
        return self.driver.switch_to.alert

    def get_text_from_alert(self):
        """
        User to get text from alert
        :return: alert text
        """
        return self.switch_to_alert().text

    def accept_alert(self):
        """
        Used to accept the pop up alert
        :return: None
        """
        self.switch_to_alert().accept()

    def reload_iframe(self, locator_info, timeout=wait_time):
        """
        Javascript code to reload iframe.
        :param locator_info: contains unique locator type and locator.
        :param timeout: time to wait.
        :return: none
        """
        start_time = datetime.now()
        try:
            self.driver.switch_to.default_content()
            element = self.get_element(locator_info, timeout)
            self.driver.execute_script("arguments[0].contentWindow.location.reload(true);", element)
        except WebDriverException as ex:
            self.log.write_message_error("Unable to reload the iframe",
                                         start_time=start_time)
            self.log.write_message_exception(ex)
            raise ex

    def enter_tab(self, n=1):
        """
        Enters tab on the current active element
        :param: n - no of times tab
        :return: None
        """
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.TAB * n)
        actions.perform()
