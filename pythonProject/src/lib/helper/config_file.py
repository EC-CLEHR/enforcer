""" Placeholder for Configuration variables """
import os
from collections import namedtuple

from src.lib.helper.path_helper import get_config_ini_file

config = get_config_ini_file("../config.ini")

GENERATE_LOG = config.getboolean('LOGGING', 'generate_log')
BASE_DIR_PATH = os.path.abspath('')

LOG_DIR_DEFAULT = os.path.join(BASE_DIR_PATH, config.get('LOGGING', 'log_dir_path'))
IMPLICIT_WAIT_TIME = config.getint('TIMEOUT', 'implicit_wait_time')
EXPLICIT_WAIT_TIME = config.getint('TIMEOUT', 'explicit_wait_time')

DATA_SOURCE_PATH = config.get('PATHS', 'data_source_path')

DATETIME_FORMAT = "%Y%m%dT%H%M%S"

LOG_FILE_NAME_PREFIX = config.get('LOGGING', 'log_file_name_prefix')
LOG_LEVEL = config.get('LOGGING', 'log_level')

HTML_REPORT_TITLE = config.get('RESULTS_REPORT', 'html_report_title')

SCREENSHOT_BASE_DIR = BASE_DIR_PATH
SCREENSHOT_DIR_RELATIVE_PATH = config.get('SCREENSHOT', 'screenshots_dir_path')
TAKE_SCREENSHOT = config.getboolean('SCREENSHOT', 'take_screenshot')
SCREENSHOT_PIXEL_WIDTH = "680"

SCREENSHOT_AND_TITLE = namedtuple('screenshot', 'file title')
SCREENSHOT_LIST = []

MIN_CHROME_VERSION = config.getint('BROWSER_VERSION', 'min_chrome_version')
MIN_FIREFOX_VERSION = config.getint('BROWSER_VERSION', 'min_firefox_version')

OUTPUT_DATA_FILE_EXTENSION = config.get('OUTPUT_DATA_FILE', 'output_data_file_extension')
OUTPUT_DATA_FILE_PREFIX = config.get('OUTPUT_DATA_FILE', 'output_data_file_name_prefix')
OUTPUT_DATA_FILES_DIR_PATH = config.get('OUTPUT_DATA_FILE', 'output_data_files_dir_path')

CLOSE_BROWSER = config.getboolean('DEBUGGING', 'close_browser')

# Path of project in which this framework is installed used as a plugin.
BASE_DIR_SOLUTION = os.path.abspath('')
log_ini_file = os.path.join(BASE_DIR_SOLUTION, 'config.ini')
if not os.path.isfile(log_ini_file):
    log_ini_file = config
    BASE_DIR_SOLUTION = BASE_DIR_PATH
config.read(log_ini_file)

LOG_DIR = os.path.join(
    BASE_DIR_SOLUTION, config.get('LOGGING', 'log_dir_path'))

# Environment
ENVIRONMENT = config.get('ENVIRONMENT', 'environment')
ENVIRONMENT_LIST = ['staging', 'qa']

# Appium constants
APPIUM_SERVER = 'http://localhost:4723/wd/hub'
CONSUL_URL_ORION = 'http://consul-{env}.smileco.cloud:8500/v1/kv/orion/orion?raw'  # NOSONAR
IOS_APP = config.get('APPIUM_APP_CAPABILITIES', 'ios_app')
ANDROID_APP = config.get('APPIUM_APP_CAPABILITIES', 'android_app')
ANDROID_APP_PACKAGE = config.get('APPIUM_APP_CAPABILITIES', 'android_app_package')
ANDROID_APP_ACTIVITY = config.get('APPIUM_APP_CAPABILITIES', 'android_app_activity')
PICKER_WHEEL_SWIPES = config.getint('APPIUM_PICKER_WHEEL_PARAMS', 'num_of_swipes')
PICKER_WHEEL_OFF_SET = config.get('APPIUM_PICKER_WHEEL_PARAMS', 'off_set')
PICKER_WHEEL_DAYS = config.getint('APPIUM_PICKER_WHEEL_PARAMS', 'num_of_days')
IOS_DEVICE_TYPE = config.get('APPIUM_IOS_DEVICE_TYPE', 'ios_device_type')

# Saucelab
SAUCELAB_APPIUM_URL: str = config.get('SAUCELABS', 'appium_url')
SAUCE_CONNECT_PATH: str = os.path.join(
    BASE_DIR_SOLUTION, config.get('SAUCELABS', 'sauce_connect_proxy_path'))
SAUCE_STORAGE_URL: str = 'https://api.us-west-1.saucelabs.com/v1/storage/upload'
AWSDEVICEFARM_APPIUM_URL: str = config.get('AWSDEVICEFARM', 'appium_url')
SAUCELAB_APPIUM_VERSION: str = config.get('SAUCELABS', 'sauce_appium_version')
SAUCELAB_USER_ID: str = config.get('SAUCELABS', 'saucelabs_userid')
SAUCELAB_ACCESS_KEY: str = config.get('SAUCELABS', 'saucelabs_accesskey')
SAUCELAB_TUNNEL: str = config.get('SAUCELABS', 'saucelabs_tunnel')

# Appium Native app
NATIVE_APP_LIST = [x for x in config.get('MOBILE_APPS', 'native_app_list').split(',')]

# Colors
WHITE_COLOR = 'rgba(255, 255, 255, 1)'

# Device details file path
DEVICE_DETAILS_CSV_PATH: str = config.get('DEVICE_DETAILS', 'device_details_csv_path')

# Test Rail
TESTRAIL_BASE_URL = config.get('TESTRAIL', 'testrail_base_url')
TESTRAIL_QUERY_PARAMS = config.get('TESTRAIL', 'testrail_query_params')
TESTRAIL_USER_NAME = config.get('TESTRAIL', 'user_name')
TESTRAIL_APIKEY = config.get('TESTRAIL', 'apikey')
TESTRAIL_SUITE_ID = config.get('TESTRAIL', 'suite_id')

# Jira
JIRA_BASE_URL = config.get('JIRA', 'jira_base_url')
JIRA_USERNAME = config.get('JIRA', 'jira_username')
JIRA_API_KEY = config.get('JIRA', 'jira_api_key')
JIRA_ISSUE_SUMMARY = config.get('JIRA', 'jira_issue_summary').strip()
JIRA_ISSUE_LABEL = config.get('JIRA', 'jira_issue_label').strip()
JIRA_BUG_IMPACT = config.get('JIRA', 'jira_bug_impact')
JIRA_BUG_URGENCY = config.get('JIRA', 'jira_bug_urgency')
JIRA_BUG_AFFECTED_ENVIRONMENT = config.get('JIRA', 'jira_bug_affected_environment')

# App Center
APPCENTER_OWNER = config.get('APPCENTER', 'appcenter_owner')
APPCENTER_ACCESS_KEY = config.get("APPCENTER", "appcenter_access_key")

# Sharepoint
SHAREPOINT_BASE_URL = config.get("SHAREPOINT", 'base_url')
SHAREPOINT_SITE_URL = config.get("SHAREPOINT", 'site_url')
SHAREPOINT_CLIENT_ID = config.get("SHAREPOINT", 'client_id')
SHAREPOINT_CLIENT_SECRET = config.get("SHAREPOINT", 'client_secret')
SHAREPOINT_TENANT_ID = config.get("SHAREPOINT", 'tenant_id')
SHAREPOINT_FILE_TO_READ = config.get("SHAREPOINT", 'file_to_read')
SHAREPOINT_WORKSHEET_NAME = config.get("SHAREPOINT", 'worksheet_name')

# Aws
AWS_REGION = config.get("AWS", 'region')
AWS_ROLE_ARN = config.get("AWS", 'aws_role_arn')
AWS_ROLE_SESSION_NAME = config.get("AWS", 'role_session_name')

# Appium Native app bundle Id
NATIVE_APP_BUNDLE_ID = config.get("APPIUM_NATIVE_APP_BUNDLE_ID", 'native_app_bundle_id')

# base documentation page for AWS service clients
AWS_DOCS_BASE = "https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/"
# service-specific doc page
# parametrize with lower-case service name, e.g. 'sqs'
AWS_SERVICE_DOCS_PAGE_TMPLT = f"{AWS_DOCS_BASE}" + "{}.html"
# method-specific doc section in service-specific doc page
# parametrize with service name twice (lower-case and all-caps)
# and method name, e.g. 'sqs', 'SQS', 'list_queues'
# -> <AWS_DOCS_BASE>/sqs.html#SQS.Client.list_queues
AWS_SERVICE_METHOD_DOCS_ANCHOR_TMPLT = f"{AWS_SERVICE_DOCS_PAGE_TMPLT}#" + "{}.Client.{}"
AWS_SERVICE = {'sns': {}, 'sqs': {}, 's3': {}}
