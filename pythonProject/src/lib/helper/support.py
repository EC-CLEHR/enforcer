"""
supports to read json file and all other common functionality's
"""
import csv
import importlib
import inspect
import json
import os
import re
import time

import subprocess
import sys

import psutil
from datetime import datetime, timezone, timedelta
from functools import wraps

import boto3
import pytest
import requests
import secrets
from requests.models import Response
from requests.exceptions import RequestException
from botocore.exceptions import ClientError

from src.lib.helper import constant, config_file
from src.lib.helper import log_helper
from src.lib.helper import path_helper
from src.lib.helper.csv_helper import CSVHelper
from src.lib.helper.custom_exceptions import LogDirNotFound, AppiumException
from src.lib.helper.config_file import IOS_DEVICE_TYPE


def kill_process_by_name(p_name: str):
    """
    Kill the process with given process id
    """
    try:
        log_helper.Logging.write_message_info(f"Killing process: {p_name}")
        if sys.platform == 'win32':
            os.system("taskkill /F /IM " + p_name)
        else:
            start_time = datetime.now()
            while find_process_id(p_name):
                pid = find_process_id(p_name)
                psutil.Process(pid).kill()
                time.sleep(1)
                if datetime.now() >= start_time + timedelta(0, 30):
                    break
    except psutil.NoSuchProcess:
        raise Exception(f"Process not found with given pid: {pid}")
    except Exception as ex:
        raise Exception(f"Exception during kill process using pid: {pid}", ex)


def get_current_datetime():
    """This method returns the date and time for today based on format in DATETIME_FORMAT
    constant"""
    return datetime.today().strftime(constant.DATETIME_FORMAT)


def random_with_n_digits(n):
    """
    Returns the random digit of length 'n'
    :param n: Length on the random digit
    :return: Random digit
    """
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return range_start + secrets.randbelow(range_end - range_start)


def read_data(file_path, key):
    """
    Reads the JSON data and returns dictionary
    :param file_path: file path of the JSON file
    :param key: Root object key to deserialize
    :return: string
    """
    with open(file_path, encoding='utf-8') as f:
        data_dictionary = json.load(f)
        data = json.dumps(data_dictionary[key])
    return data


def get_current_method_name():
    """
    Used to get the current calling method name
    :return: Calling method name
    """
    return inspect.stack()[1][3]


def get_locator(locator_info):
    """
    Used to returned tuple with locator type and its value
    :param locator_info: list of locator type and its value
    :return: locator and its value as a tuple
    """
    locator_type = None
    locator_value = None
    for key, value in locator_info.items():
        locator_type = key
        locator_value = value
    return locator_type, locator_value


def parse_html_to_text(html_source):
    """
    To parse text from html source
    :param html_source: html source
    :return: parsed text
    """
    style_tags_compile = re.compile('(?s)<style(.*?)</style>')  # regex for removing style tags
    text = style_tags_compile.sub("", html_source)
    html_tags_compile = re.compile('<[^<>]+>')  # regex for removing html tags
    text = html_tags_compile.sub("", text)
    text = "".join(
        [s for s in text.splitlines(True) if s.strip()])  # For removing extra spaces in content
    return text


def remove_item_from_list(list_of_items, item):
    """
    To remove an item from list
    :param list_of_items: any list
    :param item: item or value in the list
    """
    for each_item in list_of_items:
        if item in str(each_item):
            list_of_items.remove(each_item)


def add_config_metadata(config, meta_data):
    """
    To add new pytest config metadata
    :param config: config
    :param meta_data: pytest config metadata
    """
    for key, value in meta_data.items():
        config._metadata[key] = value


def remove_config_metadata(config, *args):
    """
    To remove list of keys from pytest config metadata
    :param config: config
    :param args: list of keys to remove from pytest config metadata
    """
    for key in args:
        if key in config._metadata:
            config._metadata.pop(key)


def format_metadata(config):
    """
    Used to format metadata into a tabular format
    :param config: config object
    """
    metadata_dict: dict = config._metadata
    formatted_data = ""
    for key in metadata_dict.keys():
        formatted_data = formatted_data + f"{key} : {metadata_dict[key]}\n"

    return formatted_data


def update_metadata(config):
    add_orion_ver_to_metadata(config)
    add_config_metadata(config,
                        {'Cmd Line Args': "pytest {0}".format(get_command_line_options(config))})
    add_config_metadata(config, {'Time Zone': str(datetime.now(timezone.utc).astimezone().tzinfo)})
    # Remove few metadata keys from HTML Report
    remove_config_metadata(config, 'JAVA_HOME', 'Packages', 'Plugins')


def get_command_line_options(config):
    """
    :param config: config
    :return: command line options passed
    """
    worker_count = os.environ.get('PYTEST_XDIST_WORKER_COUNT')

    options_str = ' '.join(config.workerinput["mainargv"][1:]) if worker_count else ' '.join(
        sys.argv[1:])
    log_helper.Logging.write_message_info("Given cmd options: " + options_str)
    return options_str


def add_orion_ver_to_metadata(config):
    """
    To add orion version to pytest config metadata
    :param config: config
    """
    if 'orion' in config._metadata['Plugins']:
        add_config_metadata(config, {'Orion': config._metadata['Plugins']['orion']})


def get_browser_details(request, driver):
    """
    To get browse details (name, version and headless mode)
    :param request: request
    :param driver: driver instance
    """
    browser_name = request.config.getoption('--browser').capitalize()
    headless_mode = "Headless" if request.config.getoption('--headless') else ""
    browser_ver = driver.capabilities[
        'browserVersion'] if 'browserVersion' in driver.capabilities else \
        driver.capabilities['version']
    return browser_name, browser_ver, headless_mode


def get_mobile_details(request):
    """
    To get mobile app details (app, mobile os)
    :param request: request
    """
    mobile_os = request.config.getoption('--mobile-os')
    mobile_app = request.config.getoption('--mobile-app')
    app = mobile_app if mobile_app else " - Web App"
    return mobile_os, app


def add_csv_details(header: list, filename=None):
    """
    This method is for providing headers and filename to csv generation.
    Will be used as a decorator over the test script
    :param header: header as list
    :param filename: optional filename
    :return: pytest parametrize command
    """
    param = {"header": header, "filename": filename}
    return pytest.mark.parametrize("write_csv_headers", [param],
                                   indirect=True)


def get_consul_data(key, *keys, url):
    """
    Makes a http call to consul and retrieves credentials.
    :param key: Atleast one parameter expected in the argument list
    :param url: consul url
    :param keys: list of keys to get data from consul
    :return: a dictionary with required credentials data.
    """

    try:
        consul_response = requests.request("GET", url, timeout=constant.WAIT_TIME_XS)
        consul_response_json = json.loads(consul_response.text)
        consul_data_dict = {key: consul_response_json.get(key)}
        consul_data_dict.update(
            {each_key: consul_response_json.get(each_key) for each_key in keys
             if each_key in consul_response_json})

    except KeyError as key_err:
        raise KeyError("Mismatch for key: {}. Exiting pytest...".format(key_err))
    except Exception:
        pytest.exit("Are you connected to VPN??")
    return consul_data_dict


def style_report():
    script = f"""
                 <script>
                 function debugBase64(base64URL, title){{
                     var win = window.open("url");
                     win.document.write('<img src="' + base64URL  + '" style="border:0; top:0px;
                     left:0px; bottom:0px; right:0px; width:100%; height:100%;" />');
                     win.document.title = title;
                 }}
                 </script>
             """  # noqa:F541

    styles = f""" <style>
                     .log {{
                         float: left;
                         width: 50vw;
                         height: 50vh;
                     }}
                     .screenshot {{
                         border: 2px solid grey;
                         margin-bottom: 2px;
                         margin-right: 5px;
                         max-width: -webkit-fill-available;
                         max-height: 45vh;
                     }}
                     .container {{
                         overflow: auto;
                         width: 45vw;
                         height: 50vh;
                         float: right;
                         display: flex;
                         flex-wrap: wrap;
                     }}
                 </style> """  # noqa:F541
    return script, styles


def get_links_from_html(html):
    """
    To get all links from html content
    :param html:
    :return: list of links in format: [{"title": "google", "href": "https://google.com"}]
    """

    from bs4 import BeautifulSoup

    links = []

    for a in BeautifulSoup(html, features="html.parser").find_all('a'):
        if a['href'] not in links:
            links.append(a['href'])

    for match in re.findall(
            'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', html):
        if match not in links:
            links.append(re.sub('<.*?>', '', match))

    return links


def get_current_test_name():
    """
    gets current test name
    :return: current_test_name, a str value :
    """
    current_test_name = None
    try:
        current_test_name = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]
        if not current_test_name:
            log_helper.Logging.write_message_error("Unable to get current test name")
    except Exception as ex:
        log_helper.Logging.write_message_exception(
            "Exception on trying to get current test name :\n " + str(ex))
    return current_test_name


def get_aws_secret(secret_name, region_name):
    """
    Get secret from AWS secret manager.
    :param secret_name: secret name to be pulled from AWS secret manager
    :param region_name: AWS region name
    :return: json data
    """
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        data = json.loads(get_secret_value_response['SecretString'])
        return data

    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            log_helper.Logging.write_message_exception("can't decrypt the protected secret text")
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            log_helper.Logging.write_message_exception("Internal ServiceError Exception")
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            log_helper.Logging.write_message_exception("Invalid Parameter Exception")
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the
            # resource.
            log_helper.Logging.write_message_exception("Invalid Request Exception")
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            log_helper.Logging.write_message_exception("Resource NotFound Exception")
            raise e


def get_test_case_id(test_case):
    """
    This method returns test case id.
    :return: str
    """
    return re.search(r'(\d{7})', test_case).group()


def check_parameter_for_none_blank(*keys):
    """
    Checks for a passed in parameters are blank or  None
    :param keys: parameters to be checked for None or blank value
    :return: a boolean Value
             or raises a ValueError exception
    """
    return_val = True
    err_items_list = []
    for each_item in keys:
        if each_item is None or each_item == "":
            err_items_list.append(each_item)
    if len(err_items_list) > 0:
        raise ValueError(f"Given parameters are None or blank : {err_items_list}")
    return return_val


def log_exception(test):
    @wraps(test)
    def wrapper(*args, **kwargs):
        try:
            test(*args, **kwargs)
        except Exception as ex:
            log_helper.Logging.write_message_exception(ex)
            assert False

    return wrapper


def get_network_log_filepath():
    """
    To get network log file path
    :return: string
    """
    path_exists = path_helper.create_directory(config_file.LOG_DIR)

    if path_exists:
        test_case_name = os.environ.get(
            'PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]
        return f"{config_file.LOG_DIR}/{test_case_name}-{get_current_datetime()}-network.log"
    else:
        raise LogDirNotFound


def parameterize_fixture(fixture, *args, indirect_value=True, ids=None):
    """
    pytest.mark.parametrize decorator for passing params to
    any fixture in pytest-orion.
    :param fixture: fixture to be parameterize
    :param args : params to be passed to the fixture
    :param indirect_value: True/False
    :param ids : Testid of the parameterized fixture
    :return: parametrize decorator
    """
    return pytest.mark.parametrize(fixture, [*args], indirect=indirect_value, ids=ids)


def set_driver_params(params, ids=None):
    """
    Creates pytest.mark.parametrize decorator for passing params to
    get_driver_factory fixture in pytest-orion.
    Use this function if you need to set browser viewport
    :param params: width and height e.g {"viewport:{pixels:"320,740"}}
    :param ids: Testid of the parameterized fixture
    :return: parametrize decorator
    """
    if isinstance(params, (list, tuple)):
        return parameterize_fixture("get_driver_factory", *params, ids=ids)
    return parameterize_fixture("get_driver_factory", params, ids=ids)


def get_driver_params(request):
    """
    To restrict request params
    :param request:
    :return: params
    """
    logging_prefs = None
    viewport = None
    browser_name = None
    if hasattr(request, 'param'):
        logging_prefs = request.param.get('log')
        viewport = request.param['viewport'].get('pixels') if 'viewport' in (
            request.param.keys()) else None
        browser_name = request.param.get('browser')
    return logging_prefs, viewport, browser_name


def get_geckodriver_console_logs(filepath):
    """
    To parse js errors and console logs from geckodriver.log file
    :param filepath: geckodriver.log filepath
    :return: console logs list
    """
    console_log = []
    with open(filepath, 'r') as file:
        for line in file.read().splitlines():
            js_error = line.startswith('JavaScript error')
            if line.startswith('console') or js_error:
                level, message = line.split(':', 1)
                message = message.strip() if js_error else message.strip(
                    '" ')
                console_log.append({'level': level, 'message': message})
    return console_log


def get_saucelabs_credentials() -> tuple:
    """
    Get the saucelabs credentials from Consul
    :param: str : environment
    :return: tuple : sauce_userid, sauce_accesskey, sauce_tunnel
    """
    sauce_userid = config_file.SAUCELAB_USER_ID
    sauce_accesskey = config_file.SAUCELAB_ACCESS_KEY
    sauce_tunnel = config_file.SAUCELAB_TUNNEL
    return sauce_userid, sauce_accesskey, sauce_tunnel


class CsvData:
    csv_row_data = []


def write_data_to_csv(data, file_path):
    """
    Writes data to the CSV
    :param data: data to write
    :param file_path: file path to write
    """
    with open(file_path, "a") as file:
        file.write(data)


def read_data_from_csv(file_path):
    """
    Reads data from the CSV and return in list format
    :param file_path: file path to read data
    :return: data in list format
    """
    data = []
    if os.path.exists(file_path):
        with open(file_path) as file:
            reader = csv.reader(file, delimiter=',')
            data = list(reader)
    return data


def find_process_id(process_name: str):
    """
    Get process name & pid from process object
    :params: None
    :returns: str: pid if process found else None
    """
    for proc in psutil.process_iter():
        try:
            if proc.name() == process_name:
                return proc.pid
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            log_helper.Logging.write_message_error("Sauce connect process not found")
    return None


def upload_app_to_sauce_storage(file_path: str, userid: str, accesskey: str) -> Response:
    """
    Uploading mobile app .apk .ipa .zip to saucelabs storage
    :param file_path is applications absolute path
    :param userid is saucelabs user name
    :param accesskey is saucelabs access key
    :return Response object
    """
    file_name: str = file_path.split('/')[-1]
    try:
        files = {'payload': (file_name, open(file_path, 'rb')), 'name': (None, file_name)}
        response = requests.post(config_file.SAUCE_STORAGE_URL, files=files,
                                 auth=(userid, accesskey))
        if response.status_code != 201:
            raise RequestException
        return response
    except FileNotFoundError:
        raise Exception("App not found at ", file_path)
    except Exception as ex:
        raise Exception("App uploading to saucelabs storage failed", ex)


def override_module(to_override: str, overriding: str):
    """
    This method is used to override orion config_file from any calling repo
    :param to_override: module to override name/path(pytest_orion.config_file)
    :param overriding: overriding module name/path(pytest_orion.config_file)
    :return: None
    """
    try:
        initial_module = importlib.import_module(to_override)
        overriding_module = importlib.import_module(overriding)
        all_common_fields = [value for value in dir(initial_module) if
                             value in dir(overriding_module)]
        req_fields = [f for f in all_common_fields if f.isupper()]
        for i in req_fields:
            setattr(initial_module, i, getattr(overriding_module, i))
    except Exception as e:
        raise e


def data_driven(test):
    """
    Decorator to make any test data driven
    :param test: test on which applied
    :return: func
    """

    @pytest.mark.usefixtures('update_test_data_for_ddt')
    def wrapper(*args, **kwargs):
        test(*args, **kwargs)

    return wrapper


# Appium support methods
# TODO Refine methods according to https://smiledirectclub.atlassian.net/browse/ENG-51184
# TODO create a method to read all the connected ios/android devices and simulator details :
#  https://smiledirectclub.atlassian.net/browse/ENG-51189
def get_android_device_name_os_version(device_id):
    """
    to get the details of connected real android device with the help of device name/device id
    to get the details of emulator with the help of device name/device id
    :param device_id: device id/device name passed by the user
    :return: device name, android version
    """
    os_version = subprocess.run(
        ['adb', '-s', device_id, 'shell', 'getprop', 'ro.build.version.release'],
        stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

    emu_cmd = ['adb', '-s', device_id, 'emu', 'avd', 'name']
    real_dev_cmd = ['adb', '-s', device_id, 'shell', 'getprop', 'ro.product.model']

    device_name_details = subprocess.run(emu_cmd if 'emulator' in device_id else real_dev_cmd,
                                         stdout=subprocess.PIPE).stdout.decode('utf-8').strip()

    if device_name_details.splitlines():
        device_name = device_name_details.splitlines()[0]
        return device_name, os_version

    raise AppiumException(f"Unable to find a device/emulator with the provided {device_id} "
                          f"name/id, please provide a valid device name/id")


def get_ios_device_details(device_id):
    """
    to get the details of the connected ios device or simulator with the help of udid
    to get the details of simulator with the help of udid
    :param device_id: udid passed by the user
    :return: device name & ios version
    """
    try:
        list_of_device_info = execute_command(constant.CMD_IOS_DEVICES).splitlines()
        matched_info = [x for x in list_of_device_info if device_id in x]
        if not matched_info:
            raise AppiumException(
                "Real ios device is not connected OR a simulator with provided {} is not "
                "found".format(device_id))
        ios_dev_info = matched_info[0].split("(" + device_id + ")")[0].strip()
        device_name = ios_dev_info.rsplit(' ', 1)[0].strip()
        os_version = re.findall(r'-?\d+\.?\d*\.?\d*', ios_dev_info)[-1]
        return device_name, os_version
    except AppiumException as device_exception:
        log_helper.Logging.write_message_exception(device_exception,
                                                   "Unable to find a device/simulator with the "
                                                   "provided {}, please "
                                                   "provide a correct udid".format(device_id))
        raise device_exception


def get_available_device_details(mobile_os):
    """
    to get the details of the connected ios/android device details
    :param mobile_os: operating system of connected mobile device
    :return: device name/device udid, os version
    """
    try:
        device_details = {}
        if mobile_os == "android":
            device_id = get_available_android_device_id()
            device_name, os_version = get_android_device_name_os_version(device_id)

        else:
            if check_real_ios_device_connected():
                device_id, device_name, os_version = get_ios_real_device_details()
            else:
                device_id, device_name, os_version = get_booted_ios_simulator_details()
            device_details["device_id"] = device_id

        device_details["device_name"] = device_name
        device_details["os_version"] = os_version
        return device_details
    except Exception as ex:
        log_helper.Logging.write_message_exception(
            f"Failed to get the {mobile_os} device/emulator details. Make sure you connect the "
            f"real device/emulator.")
        raise ex


def get_available_android_device_id():
    """
    To get the available android device id
    :return: device id
    """
    device_id = execute_command(constant.CMD_ADB_DEVICES).splitlines()[1].split("\t")[0]
    if device_id:
        return device_id
    else:
        raise AppiumException("Couldn't find the android device/emulator.."
                              "Make sure you connect one...")


def execute_command(command):
    """
    executes the provided command and returns the results
    return: out put
    """
    return subprocess.run(command, stdout=subprocess.PIPE).stdout.decode('utf-8')


def get_device_details_by_device_id(mobile_os, device_id):
    """
    to get the device details of the connected device or simulator/emulator with the help of
    device name/udid
    :param mobile_os: operating system of connected mobile device or running simulator/emulator
    :param device_id: device name/udid
    :return: device name(for ios device), os version
    """
    device_details = {}
    if mobile_os == 'android':
        device_details["device_name"], device_details["os_version"] = \
            get_android_device_name_os_version(
            device_id)

    elif mobile_os == 'ios':
        device_details["device_name"], device_details["os_version"] = get_ios_device_details(
            device_id)

    return device_details


def get_ios_real_device_details():
    """
    To get the device id, device name and os version of the connected ios real device
    :return: device id, device name and os version
    """

    devices = execute_command(constant.CMD_IOS_REAL_DEVICES).splitlines()

    if not devices:
        raise AppiumException("real ios device is not connected")

    device_id = devices[0].translate({ord(c): "" for c in "[]"})
    device_name, os_version = get_ios_device_details(device_id)
    return device_id, device_name, os_version


def get_booted_ios_simulator_details(device_type=IOS_DEVICE_TYPE):
    """
    To get the device id, device name and os version of the booted ios simulator
    :param device_type: ios device type : iPhone OR iPad
    :return: device id, device name and os version
    """
    booted_simulators_list = execute_command(constant.CMD_IOS_SIMULATORS).splitlines()

    for info in booted_simulators_list:
        if device_type in info:
            os_version = ""
            device_id = info.strip().split("(")[-2].replace(")", "").strip()
            device_name = info.strip().split("(")[0].strip()
            index_info = booted_simulators_list.index(info)
            reverse_list = list(reversed(booted_simulators_list[1:index_info]))
            for os_ver in reverse_list:
                if 'Booted' not in os_ver and 'iOS' in os_ver:
                    os_version = os_ver.translate({ord(c): "" for c in "--"}).strip().split(" ")[1]
                    break
            return device_id, device_name, os_version

    raise AppiumException(
        "couldn't find any booted simulators, ..make sure you have an iPad OR iPhone simulator "
        "booted!")


def check_real_ios_device_connected():
    """
    To check whether real ios device is connected or not
    :return: bool
    """
    device_info = execute_command(constant.CMD_IOS_REAL_DEVICES)

    if device_info:
        return True
    return False


def get_test_log_from_logfile(test_name: str, log_file_path: str):
    """
    Read the log messages based on the test name
    :param test_name: test script name
    :param log_file_path: file path of logs file
    """
    try:
        content = open(log_file_path, 'r+').readlines()
        filtered_content = ''
        for line_num, line_content in enumerate(content):
            if test_name in line_content:
                for line in content[line_num:]:
                    filtered_content += f"{line}"
        return filtered_content
    except FileNotFoundError:
        sys.stderr.write('No log_file_path provided')
        raise


def is_app_installed_on_real_device(app_id, mobile_os="ios"):
    """
    To verify installed native application on real device
    :param app_id: bundle id of native app
    :param mobile_os: operating system of connected mobile device
    :return: boolean
    """
    if mobile_os != "ios":
        raise AppiumException("We do not support this functionality other than on iOS")

    apps_info_list = execute_command(constant.CMD_IOS_NATIVE_APPS).splitlines()
    for info in apps_info_list:
        if app_id in info:
            return True
    return False


def write_mobile_device_details_to_csv():
    """
    To write available mobile (ios and android) device/simulator/emulator details to a csv file.
    """
    try:
        headers = ['platform', 'device_id', 'device_name', 'os_version']
        connected_devices = []
        time_stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        filename = os.path.join(constant.DEVICE_DETAILS_CSV_PATH, f"device_details{time_stamp}.csv")

        if sys.platform == "darwin":
            # ios simulators
            simulators = execute_command(constant.CMD_IOS_SIMULATORS).splitlines()
            for info in simulators:
                if "iPhone" in info or 'iPad' in info:
                    device_id = info.strip().split("(")[-2].replace(")", "").strip()
                    device_name, os_version = get_ios_device_details(device_id)
                    connected_devices.append(["ios simulator", device_id, device_name, os_version])

            # ios real devices
            devices = execute_command(constant.CMD_IOS_REAL_DEVICES).splitlines()
            for i in range(2, len(devices)):
                if devices[i] == "":
                    continue
                else:
                    device_id = devices[0].translate({ord(c): "" for c in "[]"})
                    device_name, os_version = get_ios_device_details(device_id)
                    connected_devices.append(
                        ["ios real device", device_id, device_name, os_version])

        # android devices
        devices_info = execute_command(constant.CMD_ADB_DEVICES).splitlines()
        for index in range(1, len(devices_info)):
            if devices_info[index] != "":
                device_id = devices_info[index].split("\t")[0]
                device_name, os_version = get_android_device_name_os_version(device_id)
                connected_devices.append(["android", device_id, device_name, os_version])

        # write data to csv
        if connected_devices:
            CSVHelper.create_csv(filename, [headers] + connected_devices)
        else:
            log_helper.Logging.write_message_info("Devices connected: 0, file creation skipped")
    except Exception as ex:
        log_helper.Logging.write_message_exception(ex, "failed to write the details to csv.")
        raise ex
