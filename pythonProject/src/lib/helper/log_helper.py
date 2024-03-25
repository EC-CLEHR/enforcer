"""
Initialize, Loads and writes the logging in a file
"""
import datetime
import inspect
import logging
import os
import sys

import pytest

from src.lib.helper import config_file
from src.lib.helper.custom_exceptions import LogDirNotFound
from src.lib.helper import path_helper


class Logging:
    """
    To bind Log_helper methods globally.
    """
    logger = None

    @staticmethod
    def write_message_info(message, start_time=None):
        pass

    @staticmethod
    def write_message_debug(message, start_time=None):
        pass

    @staticmethod
    def write_message_error(message, url=None, start_time=None):
        pass

    @staticmethod
    def write_message_exception(exception, message=None):
        pass

    @staticmethod
    def write_message_warning(exception, message=None):
        pass

    @staticmethod
    def disable_log():
        pass

    @staticmethod
    def enable_log():
        pass


class LogHelper:

    def __init__(self):
        # To check if the test is being run from platform
        if config_file.LOG_DIR == config_file.BASE_DIR_SOLUTION + "\\":
            # To assign default path to logs if the tests are being run from platform
            self.log_dir = config_file.LOG_DIR_DEFAULT
        else:
            self.log_dir = config_file.LOG_DIR

        log_file_name = get_log_file_name()

        self.logger = logging.getLogger(log_file_name)
        # By default, log all messages
        self.logger.setLevel(str(config_file.LOG_LEVEL).upper())

        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s",
                                      datefmt="%m/%d/%Y %I:%M:%S %p")

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(config_file.LOG_LEVEL)
        console_handler.setFormatter(formatter)
        pytest.log_full_paths = ''

        self.logger.addHandler(console_handler)

        if config_file.GENERATE_LOG:
            path_exists = path_helper.create_directory(self.log_dir)

            if path_exists:
                self.file_name = "{0}.log".format(self.log_dir + "/" + log_file_name)
                file_handler = logging.FileHandler(self.file_name, mode='w')
                file_handler.setLevel(config_file.LOG_LEVEL)
                pytest.log_full_paths = f"{self.log_dir}/{log_file_name}.log"
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            else:
                raise LogDirNotFound

    def write_message_info(self, message, start_time=None):
        """
        logging the message with info
        :param message: info message
        :param start_time: start time to capture the total sec
        :return: None
        """
        if start_time:
            total_time = (datetime.datetime.now() - start_time).total_seconds()
            self.logger.info("{message} total time in seconds:{total_time}"
                             .format(message=message, total_time=str(total_time)))
        else:
            self.logger.info("{message}".format(message=message))

    def write_message_debug(self, message, start_time=None):
        """
        logging the message with debug
        :param message: debug message
        :param start_time: start time to capture the total sec
        :return: None
        """
        if start_time:
            total_time = (datetime.datetime.now() - start_time).total_seconds()
            self.logger.debug("{message} total time in seconds:{total_time}"
                              .format(message=message, total_time=str(total_time)))
        else:
            self.logger.debug("{message}".format(message=message))

    def write_message_error(self, message, url=None, start_time=None):
        """
        logging the message  with error details
        :param message: log error message
        :param url: url of the application
        :param start_time: start time
        :return: None
        """
        if url and start_time:
            total_time = (datetime.datetime.now() - start_time).total_seconds()
            self.logger.error(
                "Error occurred \n page url: {url} \n method name : {method_name} \n message: {"
                "message}"
                "\n total time in seconds: {total_time}".format(url=url,
                                                                method_name=inspect.stack()[1][3],
                                                                message=message,
                                                                total_time=str(total_time)))
        else:
            self.logger.error("Error occurred  \n error :{message}".format(message=message))

    def write_message_exception(self, exception, message=None):
        """
        logging the message with exception details
        :param exception: exception
        :param message: log message
        :return: None
        """
        if message:
            self.logger.exception(
                "Exception occurred \n message : {message} \n exception :{exception}"
                .format(message=message, exception=exception))
        else:
            self.logger.exception(
                "Exception occurred  \n exception :{exception}".format(exception=exception))

    def write_message_warning(self, exception, message=None):
        """
        logging the message with warning details
        :param exception: exception
        :param message: warn message
        :return: None
        """
        if message:
            self.logger.warning("Warning  \n message : {message} \n exception :{exception}"
                                .format(message=message, exception=exception))
        else:
            self.logger.warning("Warning  \n exception :{exception}".format(exception=exception))

    def disable_log(self):
        """
        Disable logs
        :return: None
        """
        self.logger.info("****** REDACTED ******")
        self.logger.disabled = True

    def enable_log(self):
        """
        Enable logs
        :return: None
        """
        self.logger.disabled = False
        self.logger.info("****** LOGS ENABLED ******")


def get_log_file_name():
    """
    build a log file name
    :return: returns a string(log_file_name)
    """
    worker_name = os.environ.get('PYTEST_XDIST_WORKER')
    now = datetime.datetime.now()
    current_date = now.strftime("%Y-%m-%d-%H-%M-%S")

    if worker_name:
        log_file_name = config_file.LOG_FILE_NAME_PREFIX + "_" + worker_name + "_" + current_date
    else:
        log_file_name = config_file.LOG_FILE_NAME_PREFIX + "_" + current_date

    return log_file_name


def get_geckodriver_log_absolute_path():
    """
    Build a geckodriver(Firefox) log file absolute path
    :return: str
    """
    path_exists = path_helper.create_directory(config_file.LOG_DIR)
    if path_exists:
        return f'{config_file.LOG_DIR}/geckodriver-{get_log_file_name()}.log'
    else:
        raise LogDirNotFound
