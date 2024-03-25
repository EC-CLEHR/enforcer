import enum
import json

from src.lib.helper.support import (parameterize_fixture,
                                          get_network_log_filepath)


class LoggingLevel(enum.Enum):
    """
    Logging levels of LoggingPreferences JSON object
    """
    ALL = "ALL"
    FINEST = "FINEST"
    FINER = "FINER"
    FINE = "FINE"
    CONFIG = "CONFIG"
    INFO = "INFO"
    WARNING = "WARNING"
    SEVERE = "SEVERE"
    OFF = "OFF"


class WebDriverLogging:
    """
    This class is used for setting Logging Preferences values of the Web Driver
    from tests.
    """

    @staticmethod
    def log_events(browser: LoggingLevel = LoggingLevel.ALL,
                   performance: LoggingLevel = LoggingLevel.ALL):
        """
        Creates pytest.mark.parametrize decorator for passing params to
        get_driver_factory fixture in pytest-orion.
        Use this function if you need to log several types of events.
        :param browser: browser logging level (default: "OFF")
        :param performance: performance logging level (default: "OFF")
        :return: parametrize decorator
        """
        param = {"log": {"browser": browser.value, "performance": performance.value}}
        return parameterize_fixture("get_driver_factory", param)

    @classmethod
    def log_browser_events(cls, level: LoggingLevel = LoggingLevel.ALL):
        """
        Creates pytest.mark.parametrize decorator for passing params to
        get_driver_factory fixture in pytest-orion.
        :param level: browser logging level (default: LoggingLevel.ALL)
        :return: parametrize decorator
        """
        return cls.log_events(browser=level, performance=LoggingLevel.OFF)

    @classmethod
    def log_performance_events(cls, level: LoggingLevel = LoggingLevel.ALL):
        """
        Creates pytest.mark.parametrize decorator for passing params to
        get_driver_factory fixture in pytest-orion.
        :param level: performance logging level (default: LoggingLevel.ALL)
        :return: parametrize decorator
        """
        return cls.log_events(browser=LoggingLevel.OFF, performance=level)


def write_network_logs_to_file(filepath=None):
    """
    Writes network logs to file
    :param filepath: path of the file with filename (default: "{
    config_file.LOG_DIR}/...-network.log"")
    """
    from src.lib.helper.selenium_extension import SeleniumExtension

    if not filepath:
        filepath = get_network_log_filepath()
    network_logs = SeleniumExtension().get_browser_network_log()
    with open(filepath, 'a') as file:
        file.write(json.dumps(network_logs, separators=(",", ":"), indent=4))


def handle_network_logging(item, report):
    log_performance = item.config.getoption('--log-performance')
    if report.when in ('setup', 'call') and report.outcome == 'failed' and log_performance:
        write_network_logs_to_file()
