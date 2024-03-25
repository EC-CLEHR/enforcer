"""
@package utilities

CheckPoint class implementation
It provides functionality to assert the result

Example:
    Assert.step(result, "Message")
    Assert.test(result, "Message")
"""

from selenium.common.exceptions import WebDriverException
from src.lib.helper import config_file
from src.lib.helper import log_helper
from src.lib.helper.config_file import SCREENSHOT_LIST, SCREENSHOT_AND_TITLE
from src.lib.helper.selenium_extension import SeleniumExtension
from src.lib.helper.support import get_current_test_name


def log_info_wrapper_for_verify_resp(expected, actual_data):
    log_helper.Logging.write_message_info(
        "Step Verify Pass: expected - {expected_data}, actual - {actual_data}"
        .format(expected_data=expected, actual_data=actual_data))


def log_err_wrapper_for_verify_resp(expected, actual_data):
    log_helper.Logging.write_message_error(
        "*******Step Verify Fail: expected - {expected_data}, actual - {actual_data}"
        .format(expected_data=expected, actual_data=actual_data))


# TODO move the API asserts into separate class or .py

def are_equal(expected, actual_data):
    """
    asserts actual data with expected data
    :param expected: expected data
    :param actual_data: actual data
    :return: Boolean
    """
    if expected == actual_data:
        log_info_wrapper_for_verify_resp(expected, actual_data)
        return True
    else:
        log_err_wrapper_for_verify_resp(expected, actual_data)
        return False


def are_not_equal(data1, data2):
    """
    asserts actual data with expected data
    :param data1: expected data
    :param data2: actual data
    :return: Boolean
    """
    if data1 != data2:
        log_info_wrapper_for_verify_resp(data1, data2)
        return True
    else:
        log_err_wrapper_for_verify_resp(data1, data2)
        return False


def item_in_collection(item, obj):
    """
    asserts actual data with expected data
    :param item: expected item in list data
    :param obj: str, tuple, list, dict
    :return: Boolean
    """
    try:
        if item in obj:
            log_helper.Logging.write_message_info(str(item) + " present in " + str(obj))
            return True
        else:
            log_helper.Logging.write_message_error(str(item) + " not present in " + str(obj))
            return False
    except Exception as e:
        log_helper.Logging.write_message_error(e)
        return False


def item_not_in_collection(item, obj):
    """
    asserts data not in collection
    :param item: expected item in list data
    :param obj: str, tuple, list, dict
    :return: Boolean
    """
    try:
        if item not in obj:
            log_helper.Logging.write_message_info(str(item) + " not present in " + str(obj))
            return True
        else:
            log_helper.Logging.write_message_error(str(item) + " present in " + str(obj))
            return False
    except Exception as e:
        log_helper.Logging.write_message_error(e)
        return False


def is_none(data_object):
    """
        asserts if data is None
        :param data_object : data object
        :return: None
        """
    return are_equal(data_object, None)


def is_not_none(data_object):
    """
        asserts if data is not None
        :param data_object: data object
        :return: None
        """
    return are_not_equal(data_object, None)


def has_header_response(response, header_dict: dict):
    """
    asserts dictionary present in headers.
    :param response: response object
    :param header_dict: dictionary to verify
    :return: None
    """
    header = list(response.response.headers.items())
    header_dict_to_check = list(header_dict.items())

    for value in header_dict_to_check:
        if value not in header:
            log_helper.Logging.write_message_error(
                "key, value: {key}, {value} are not present in headers".format(key=value[0],
                                                                               value=value[1]))
            return False
    log_helper.Logging.write_message_info("{} are present in headers".format(header_dict))
    return True


def has_header_key(response, key):
    """
    asserts key in headers
    :param response: response object
    :param key: header key
    :return: None
    """
    header = response.response.headers
    return item_in_collection(key, header)


def data_in_resp(resp, member, container):
    """Check whether response data member contain input member.

    :parm resp: response to validate.
    :parm member: value to check in response.
    :parm container: response key path in dot format
        which should starts with 'resp.'. example: resp.data.0.name
    """
    json_response = resp.json_response
    actual_val = _get_val_from_resp_by_path(json_response, container)
    return item_in_collection(member, actual_val)


def data_not_in_resp(resp, member, container):
    """Check whether response data member doesn't contain input member.

    :parm resp: response to validate.
    :parm member: value to check in response.
    :parm container: response key path in dot format
        which should starts with 'resp.'. example: resp.data.0.name
    """
    json_response = resp.json_response
    actual_val = _get_val_from_resp_by_path(json_response, container)
    return item_not_in_collection(member, actual_val)


def data_equal_resp(resp, member, container):
    """Check whether response data member is same as input member.

    :parm resp: response to validate.
    :parm member: value to check in response.
    :parm container: response key path in dot format
        which should starts with 'resp.'. example: resp.data.0.name
    """
    json_response = resp.json_response
    actual_val = _get_val_from_resp_by_path(json_response, container)
    return are_equal(member, actual_val)


def data_not_equal_resp(resp, member, container):
    """Check whether response data member is not same as input member.

    :parm resp: response to validate.
    :parm member: value to check in response.
    :parm container: response key path in dot format
        which should starts with 'resp.'. example: resp.data.0.name
    """
    json_response = resp.json_response
    actual_val = _get_val_from_resp_by_path(json_response, container)
    return are_not_equal(member, actual_val)


def _get_val_from_resp_by_path(resp, path):
    """
    Get value from response by dot format key path of response.
    :parm resp: response
    :parm path: key path in dot format which should starts with 'resp.'.
    example: resp.data.0.name
    """
    val = ''
    items = path.split('.')
    for index in range(len(items)):
        if index == 0:
            val = items[index]
        else:
            try:
                val += '[%s]' % int(items[index])
            except ValueError:
                val += "['%s']" % str(items[index])
    return eval(val)


class Assert:
    @staticmethod
    def step(result, result_message):
        pass

    @staticmethod
    def step_hard(result, result_message=''):
        pass

    @staticmethod
    def test(result, result_message):
        pass


class AssertTestStatus:

    def __init__(self, config):
        """
        Initiates CheckPoint class
        """
        self.result_list = []
        self.log = log_helper.Logging
        self.config = config

    def step(self, result, result_message):
        try:

            if result:
                self.result_list.append("PASS")
                self.log.write_message_info("### STEP VERIFICATION SUCCESSFUL : " + result_message)
            else:
                self.result_list.append("FAIL")
                self.log.write_message_error("### STEP VERIFICATION FAILED : " + result_message)
                if SeleniumExtension.driver and config_file.TAKE_SCREENSHOT:
                    normal_image_path, base_64_image_full_path = SeleniumExtension(

                    ).capture_screenshot(
                        self.config)
                    captured_screenshot = base_64_image_full_path or normal_image_path
                    SCREENSHOT_LIST.append(
                        SCREENSHOT_AND_TITLE(captured_screenshot, SeleniumExtension().get_title()))

        except WebDriverException as ex:
            self.log.write_message_exception(ex.msg)
        except Exception as ex:
            self.log.write_message_exception(ex)

    def step_hard(self, result, result_message=''):
        """
        assert the current step.
        """
        if result:
            self.log.write_message_info("### STEP ASSERT PASSED : " + result_message)
        else:
            self.log.write_message_info("### STEP ASSERT FAILED : " + result_message)
        assert result

    def test(self, result, result_message):
        """
        assert the entire test - final result of the verification point in a test case
        This needs to be called at least once in a test case
        This should be final test status of the test case
        """
        self.step(result, result_message)

        if "FAIL" in self.result_list:
            self.log.write_message_error(get_current_test_name() + " ### TEST FAILED")
            self.result_list.clear()
            assert False
        else:
            self.log.write_message_info(get_current_test_name() + " ### TEST PASSED")
            self.result_list.clear()
            assert True