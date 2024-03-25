"""
support for all file path ,directory related functions
"""
import os
from configparser import ConfigParser

import sys


def create_directory(dir_path):
    """
    Creates a log directory if it does not exist
    :param dir_path: directories to be created
    :return: a boolean value
                True on Success
                False on Failure/exception
    """
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except OSError:
            sys.stderr.write("Creation of the directory %s failed" % dir_path)
            return False
    return True


def get_config_ini_file(file_name: str):
    # TODO : ENG-23341
    """
    This method helps to return the config ini object
    :param file_name: file name whose config data we want
    :return: config ini
    """
    # Path of pytest_orion package which is exported as a plugin.
    base_dir_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    config_data = ConfigParser()
    ini_file = os.path.join(base_dir_path, file_name)
    config_data.read(ini_file)
    return config_data