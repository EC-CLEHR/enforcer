from src.lib.helper.path_helper import get_config_ini_file
import os

config = get_config_ini_file('../api_config.ini')
TIMEOUT_M = config.getint('TIMEOUT', 'timeout_m')
