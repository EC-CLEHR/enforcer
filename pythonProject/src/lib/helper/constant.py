# Constants File for use by Orion Tests
# Do NOT check-in changes to this file.
# You should change the values in  this file to match your needs

from src.lib.helper.config_file import (BASE_DIR_PATH, LOG_DIR_DEFAULT, IMPLICIT_WAIT_TIME,
                                      EXPLICIT_WAIT_TIME,
                                      DATA_SOURCE_PATH, DATETIME_FORMAT, LOG_FILE_NAME_PREFIX,
                                      LOG_LEVEL,
                                      HTML_REPORT_TITLE, SCREENSHOT_BASE_DIR,
                                      SCREENSHOT_DIR_RELATIVE_PATH,
                                      TAKE_SCREENSHOT, SCREENSHOT_PIXEL_WIDTH, SCREENSHOT_AND_TITLE,
                                      SCREENSHOT_LIST, MIN_CHROME_VERSION, MIN_FIREFOX_VERSION,
                                      OUTPUT_DATA_FILE_EXTENSION, OUTPUT_DATA_FILE_PREFIX,
                                      OUTPUT_DATA_FILES_DIR_PATH, CLOSE_BROWSER, BASE_DIR_SOLUTION,
                                      LOG_DIR,
                                      ENVIRONMENT, ENVIRONMENT_LIST, APPIUM_SERVER,
                                      CONSUL_URL_ORION,
                                      SAUCELAB_APPIUM_URL, SAUCE_CONNECT_PATH, SAUCE_STORAGE_URL,
                                      AWSDEVICEFARM_APPIUM_URL, NATIVE_APP_LIST, WHITE_COLOR,
                                      TESTRAIL_BASE_URL,
                                      TESTRAIL_QUERY_PARAMS, TESTRAIL_USER_NAME, TESTRAIL_APIKEY,
                                      TESTRAIL_SUITE_ID,
                                      JIRA_BASE_URL, JIRA_USERNAME, JIRA_API_KEY,
                                      JIRA_ISSUE_SUMMARY,
                                      JIRA_ISSUE_LABEL, JIRA_BUG_IMPACT, JIRA_BUG_URGENCY,
                                      JIRA_BUG_AFFECTED_ENVIRONMENT, get_config_ini_file)


# wait_time
WAIT_TIME_XXS = 1
WAIT_TIME_XS = 5
WAIT_TIME_SMALL = 10
WAIT_TIME_MEDIUM = 15

# Appium constants
COMMAND_TIMEOUT_SMALL = 30
COMMAND_TIMEOUT_MEDIUM = 60
COMMAND_TIMEOUT_LARGE = 90
APPIUM_SESSION_TIME_OUT = 900
ANDROID_AUTOMATION_NAME = "UiAutomator2"
IOS_AUTOMATION_NAME = "XCUITest"
ANDROID_PLATFORM = "Android"
IOS_PLATFORM = "iOS"

# Appium - supported mobile operating systems
MAC_MOBILE_OS_LIST = ['ios', 'android']
WIN_MOBILE_OS_LIST = ['android']
AWS_DEVICE_OS_LIST = ['IOS', 'ANDROID']

# Supported Browsers list
SUPPORTED_BROWSERS = ['chrome', 'firefox', 'safari']

# Chrome Options for Android Web Capabilities
W3C_CHROME_OPTION = 'w3c'
W3C_CHROME_OPTION_VALUE = False

# Target Application Status - Appium
NOT_INSTALLED = 0
NOT_RUNNING = 1
RUNNING_IN_BACKGROUND_AND_SUSPENDED = 2
RUNNING_IN_BACKGROUND_AND_NOT_SUSPENDED = 3
RUNNING_IN_FOREGROUND = 4

# US Date Formats in Applications
DEFAULT_DATE_FORMAT = '%B %d, %Y'  # Ex: March 11, 2021

# Sharepoint
CSV_PATH = 'output'

# Mobile Device Commands
CMD_ADB_DEVICES = ['adb', 'devices']
CMD_IOS_SIMULATORS = ['xcrun', 'simctl', 'list', 'devices', 'booted']
CMD_IOS_DEVICES = ['xcrun', 'xctrace', 'list', 'devices']
CMD_IOS_REAL_DEVICES = ['idevice_id', '-l']
CMD_IOS_NATIVE_APPS = ['ideviceinstaller', '-l']
DEVICE_DETAILS_CSV_PATH = 'output'


# staff access token
staff_access_token = ''