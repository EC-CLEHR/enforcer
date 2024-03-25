import json
from urllib.parse import urljoin

from src.lib.helper import log_helper


def files_to_upload(path, upload_name='file'):
    """
    build a list of tuples, each with file name and filereader object.
    :param path: list with paths of files to read.
    :param upload_name: upload name of the file
    :return: List
    """
    if not isinstance(path, (list, tuple)):
        path = [path]
    files = [(upload_name, (file.split('/')[-1], open(file, 'rb'))) for file in path]
    return files


def validate_params(*args):
    """
    This function checks args for none and returns True only if any one of the args is not None.
    In all other cases it returns False
    :param args: params to  be validated
    :return: boolean value/exception
    """
    valid_params_count = sum([1 if each_arg else 0 for each_arg in args])

    if valid_params_count > 1:
        raise Exception("Provide only one parameter data or json or file/s")
    elif valid_params_count == 0:
        raise Exception("Provide atleast one parameter data or json or file/s")
    else:
        return True


def build_pretty_json(response):
    """
    converts given response json to pretty json for logging.
    :param response: python response object to be converted to pretty json string
    :return: error message
    """
    pretty_json = None
    error_msg = ""
    try:
        pretty_json = json.dumps(response.json(), separators=(",", ":"), indent=4)
    except json.JSONDecodeError:
        error_msg = "Invalid JSON Format"
        log_helper.Logging.write_message_error("Invalid JSON Format json value" + response.json())
    except Exception as ex:
        error_msg = "Unknown error"
        log_helper.Logging.write_message_error("Unknown error " + str(ex))

    log_helper.Logging.write_message_info("Statuscode:{resp_code}\nresponse:{json_data}"
                                          .format(resp_code=response.status_code,
                                                  json_data=pretty_json))
    return error_msg


def convert_to_json(message_body):
    """
    converts given parameter to json.
    :param message_body: a dictionary of python object to be converted to json string
    :return: string
    """
    try:
        json_string = json.dumps(message_body)
    except json.JSONDecodeError:
        raise Exception("Invalid JSON Format , Please check message body")
    return json_string


def build_url(config):
    """
    Builds url from APIConfiguration object and returns url
    :param config: config object to build url from its parameters
    :return: string(url)
    """
    url = urljoin(config.base_url, config.end_point)
    return url


def handle_http_error(response):
    """
    Builds and returns http error message for 400 and 500 series errors.
    :param response: response object from request call
    :return: String
    """
    if 400 <= response.status_code < 500:
        http_error_msg = u'%s Client Error: %s for url: %s' % (response.status_code,
                                                               response.reason,
                                                               response.url)

    elif 500 <= response.status_code < 600:
        http_error_msg = u'%s Server Error: %s for url: %s' % (response.status_code,
                                                               response.reason,
                                                               response.url)

    else:
        http_error_msg = None

    return http_error_msg


def rest_response_handle(response):
    """
    Method handles http response by checking for status_code and building error message if necessary
    or response if status is OK.
    :param response: HTTP response object
    :return:
        response : HTTP response object
        status_code : HTTP status_code
        text : text f response
        json_response : json response from HTTP request
        error : error message if HTTP status code is in 400 or 500 series
    """
    log_helper.Logging.write_message_info("request url is : {}".format(response.url))
    json_response = None
    http_error_msg = handle_http_error(response)
    json_error_msg, json_response = check_json_response(response)

    return (response,
            response.status_code,
            response.text,
            json_response,
            http_error_msg,
            json_error_msg)


def check_json_response(response):
    """
    converts given response json to pretty json.
    :param response: python response object to be converted to pretty json string
    :return: error message
    """
    response_json = None
    pretty_json = None
    error_msg = None
    try:
        response_json = response.json()
        pretty_json = json.dumps(response.json(), separators=(",", ":"), indent=4)
    except json.JSONDecodeError:
        error_msg = "json decode error"
        log_helper.Logging.write_message_error("Invalid JSON Format json value: None")
    except Exception as ex:
        error_msg = "Unknown error"
        log_helper.Logging.write_message_error("Unknown error " + str(ex))

        log_helper.Logging.write_message_debug("Statuscode:{resp_code}\nresponse:{json_data}"
                                               .format(resp_code=response.status_code,
                                                       json_data=pretty_json))
    return error_msg, response_json
