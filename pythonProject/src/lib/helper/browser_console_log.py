import re
from src.lib.helper.log_helper import Logging
from src.lib.helper.webdriver_logs_helper import LoggingLevel
from nested_lookup import nested_lookup


def _get_log_attribute_values(log, search_keyword, attribute):
    """
        To return a list of attribute values corresponding to presence of
        the search keyword in the message attribute.
        Attributes : Level, Source, Message, TimeStamp
    """
    try:
        attrib_values = [le[attribute] for le in log if
                         re.search(search_keyword, le['message'], re.IGNORECASE)]
    except Exception as ex:
        Logging.write_message_exception(ex)
        raise Exception("Error in processing messages attribute" + str(ex))
    return attrib_values


def get_levels(log, search_keyword):
    """
        Processes console logs to return 'level' attribute corresponding to the message attribute
        containing the search keyword.
        :param log: log obtained when web driver browser is enable in the decorator
        :param search_keyword: search keyword.
        Attributes : Level, Source, Message, TimeStamp
        :return: List of levels where search keyword is present in the message for that level.
        Ex: ['WARNING', 'SEVERE'] when search keyword is in each of this level record.
    """
    return _get_log_attribute_values(log, search_keyword, 'level')


def get_source(log, search_keyword):
    """
        Processes console logs to return 'source' attribute corresponding to the message attribute
        containing the search keyword.
        :param log: log obtained when web driver browser is enable in the decorator
        :param search_keyword: search keyword.
        :return: List of source where search keyword is present in the message for that source.
        Ex: ['console-api', 'console-api', 'console-api', 'console-api', 'console-api', 'security'].
    """
    return _get_log_attribute_values(log, search_keyword, 'source')


def get_timestamps(log, search_keyword):
    """
        Processes console logs to return 'timestamp' attribute corresponding to the message
        attribute containing the search keyword.
        :param log: log obtained when web driver browser is enable in the decorator
        :param search_keyword: search keyword.
        :return: List of timestamp where search keyword is present in the message for that
        timestamp.
        Ex:  [1594432382465, 1594432382784, 1594432382785, 1594432382785, 1594432382785,
        1594432382894].
        Attributes : Level, Source, Message, TimeStamp
        get(level) = INFO, DEBUG

    """
    return _get_log_attribute_values(log, search_keyword, 'timestamp')


def get_messages(log, search_keyword):
    """
        Processes console logs to return 'message' attribute corresponding to the message attribute
        containing the search keyword.
        :param log: log obtained when web driver browser is enable in the decorator
        :param search_keyword: search keyword.
        :return: List of messages where search keyword is present in that message.
    """
    return _get_log_attribute_values(log, search_keyword, 'message')


def _filter_log_on_keyword(log, search_keyword):
    """
        To return a list of records corresponding to the presence of search keyword
        in the message attribute.
        :param search_keyword: word for which the log is being searched for
        :param log: log obtained when web driver browser is enable in the decorator
        :param: search_keyword: search keyword.
        :return: records in which the search keyword is present
    """
    try:
        return [record for record in log if
                re.search(search_keyword, record['message'], re.IGNORECASE)]
    except Exception as ex:
        Logging.write_message_exception(ex)
        ex_msg = "Exception occurred while filtering browser console log on search keyword: {}. " \
                 "".format(search_keyword)
        raise Exception(ex_msg + str(ex))


def _filter_network_log_on_keyword(nw_logs, search_keyword):
    """
        Network logs are in dictionary or list of dictionaries format
        and this function will return a list with values
        for the corresponding search keyword.
        :param nw_logs : network logs obtained when web driver browser is enable in the decorator
        :param search_keyword: key for which value is being searched for
        :return: list of values found for the given keyword in all the logs
    """
    try:
        return_list = []
        for each_item in nw_logs:
            value = nested_lookup(search_keyword, each_item)
            if value:
                return_list.extend(value)
        return return_list
    except Exception as ex:
        Logging.write_message_exception(ex)
        ex_msg = "Exception occurred while filtering browser network log on search keyword: {}. " \
                 "".format(search_keyword)
        raise Exception(ex_msg + str(ex))


def _filter_log_on_level(log, log_level):
    """
        Processes console logs for warnings, severe and errors. Return logs for specified level
        and higher levels.
        :param log: log obtained when web driver browser is enable in the decorator.
        :param log_level: level info can be 'ALL', 'FINEST','FINER','FINE', 'CONFIG', 'INFO',
        'WARNING', 'SEVERE', 'OFF'.
        :return: List of records for that level. Level are returned with >= level argument to the
        script.
    """
    try:
        result = []
        # {'ALL': 10, 'FINEST': 20, 'FINER': 30, 'FINE': 40, 'CONFIG': 50, 'INFO': 60,
        #  'WARNING': 70, 'SEVERE': 80, 'OFF': 90}
        log_priorities = {level.name: (index + 1) * 10 for index, level in enumerate(LoggingLevel)}

        for log_line in log:
            if log_priorities.get(log_line['level']) >= log_priorities.get(log_level):
                result.append(log_line)
        return result
    except Exception as ex:
        Logging.write_message_exception(ex)
        ex_msg = "Exception occurred while filtering browser console log on level: {}. ".format(
            log_level)
        raise Exception(ex_msg + str(ex))


def filter_log(log, search_keyword=None, log_level=None):
    """
        Processes console logs to return records corresponding to the message attribute containing
        the specified search keyword for the specified level.
        :param log: log obtained when web driver browser is enable in the decorator
        :param search_keyword: search keyword.
        :param log_level: level info can be 'ALL', 'FINEST','FINER','FINE', 'CONFIG', 'INFO',
        'WARNING', 'SEVERE', 'OFF'.
        :return: List of records for that level where the given search keyword is present in that
        message.
    """
    try:
        if not (search_keyword or log_level):
            return log
        if search_keyword and log_level:
            return _filter_log_on_keyword(_filter_log_on_level(log, log_level), search_keyword)
        if log_level:
            return _filter_log_on_level(log, log_level)
        if search_keyword:
            return _filter_log_on_keyword(log, search_keyword)
    except Exception as ex:
        Logging.write_message_exception(ex)
        ex_msg = "Exception occurred while filtering browser console log on search keyword: {} " \
                 "and log level: {}. ".format(search_keyword, log_level)
        raise Exception(ex_msg + str(ex))
