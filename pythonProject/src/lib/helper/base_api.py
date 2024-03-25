import requests

from src.lib.helper.api_constants import TIMEOUT_M
from src.lib.helper.api_support import build_url, rest_response_handle, convert_to_json, files_to_upload, \
    validate_params
from src.lib.helper.log_helper import Logging


class APIResponse:
    """
    API response object.
    Args:
        status_code : http status code
        text : text from response of api call
        json_response : json from response of api call
        error_msg : error message will be given for 4XX or 5XX response codes
                    else None
    """

    def __init__(self, response, status_code, text, json_response, error_msg, json_error_msg):
        self.status_code = status_code
        self.text = text
        self.json_response = json_response
        self.http_error_msg = error_msg
        self.response = response
        self.json_error_msg = json_error_msg


class APIConfigurations:
    """
    API configuration object will be used to have a configurations that will be used for api calls.
    Attributes:
        base_url : base url
        end_point : relative url
        content_type : content type header in API call
        accept_type : accept type header in API call
        headers : headers for API calll
        auth : auth for HTTP calls
        params : params for API call
        allow_redirects : allow redirects on a HTTP call(default value is False).
        time_out : configurable timeout for API call
    """

    def __init__(self):
        self.base_url = None
        self.end_point = None
        self.content_type = None
        self.accept_type = None
        self.headers = {'Content-Type': 'application/json'}
        self.auth = None
        self.params = None
        self.allow_redirects = False
        self.time_out = TIMEOUT_M


class Rest:
    @staticmethod
    def request_get(config: APIConfigurations):
        """
        Makes a get HTTP GET call and returns APIResponse object.
        APIResponse object will be with data from GET call.
        :param config: APIConfigurations object
        :return: APIResponse response object with data from get call
        """

        url = build_url(config)

        try:
            response = requests.get(url=url,
                                    headers=config.headers,
                                    timeout=config.time_out,
                                    params=config.params,
                                    auth=config.auth
                                    )
            (response,
             status_code,
             text, json_response,
             http_err_msg,
             json_err_msg) = rest_response_handle(response)
            return APIResponse(response,
                               status_code,
                               text,
                               json_response,
                               http_err_msg,
                               json_err_msg)

        except requests.exceptions.RequestException as ex:

            Logging.write_message_exception("{err_name} on GET call for url: {url} \n {err_msg}"
                                            .format(err_name=ex.__class__.__name__, url=url,
                                                    err_msg=ex))
            raise ex

    @staticmethod
    def request_post(config: APIConfigurations, data=None, json_data=None, files=None,
                     file_upload_name='file'):
        """
        Makes a get HTTP POST call and returns APIResponse object.
        APIResponse object will be with data from POST call.
        :param config: APIConfigurations object
        :param data: message body
        :param json_data:
        :param files: file path
        :param file_upload_name: name of the file shown when uploaded
        :return: APIResponse response object with data from POST call
        """
        if data is None:
            data = {}
        url = build_url(config)
        if 'json' in config.headers.get('Content-Type', []):
            payload = convert_to_json(data)
        else:
            payload = data
        try:
            if data or files:
                if files:
                    file_list = files_to_upload(files, file_upload_name)
                else:
                    file_list = None
                response = requests.post(url=url, params=config.params,
                                         data=payload,
                                         headers=config.headers,
                                         files=file_list,
                                         timeout=config.time_out,
                                         auth=config.auth)
            elif json_data:
                response = requests.post(url=url, params=config.params,
                                         json=json_data,
                                         headers=config.headers,
                                         timeout=config.time_out,
                                         auth=config.auth)
            else:
                response = requests.post(url=url, params=config.params,
                                         data=payload,
                                         headers=config.headers,
                                         timeout=config.time_out,
                                         auth=config.auth)

            (response,
             status_code,
             text,
             json_response,
             http_err_msg,
             json_err_msg) = rest_response_handle(response)
            return APIResponse(response, status_code, text, json_response, http_err_msg,
                               json_err_msg)

        except requests.exceptions.RequestException as ex:
            Logging.write_message_exception("{err_name} on POST call for url: {url} \n {err_msg}"
                                            .format(err_name=ex.__class__.__name__, url=url,
                                                    err_msg=ex))
            raise ex

    @staticmethod
    def request_delete(config: APIConfigurations, data):
        """
        Makes a get HTTP DELETE call and returns APIResponse object.
        APIResponse object will be with data from DELETE call.
        :param config: APIConfigurations object
        :param data: data
        :return: APIResponse response object with data from DELETE call
        """
        url = build_url(config)
        try:
            response = requests.delete(url=url,
                                       headers=config.headers,
                                       params=config.params,
                                       data=convert_to_json(data),
                                       timeout=config.time_out,
                                       auth=config.auth)

            (response,
             status_code,
             text,
             json_response,
             http_err_msg,
             json_err_msg) = rest_response_handle(response)
            return APIResponse(response, status_code, text, json_response, http_err_msg,
                               json_err_msg)
        except requests.exceptions.RequestException as ex:
            Logging.write_message_exception("{err_name} on DELETE call for url: {url} \n {err_msg}"
                                            .format(err_name=ex.__class__.__name__, url=url,
                                                    err_msg=ex))
            raise ex

    @staticmethod
    def request_put(config: APIConfigurations, data=None, json_data=None, *files):
        """
        Makes a get HTTP PUT call and returns APIResponse object.
        APIResponse object will be with data from PUT call.
        :param config: APIConfigurations object
        :param data: message body
        :param json_data: json_data
        :param files: file path
        :return: APIResponse response object with data from PUT call
        """
        response = None
        is_redirect = True
        url = build_url(config)
        validate_params(data, json_data, files)
        try:
            while is_redirect:
                if data:
                    response = requests.put(url=url, params=config.params,
                                            data=convert_to_json(data),
                                            headers=config.headers,
                                            timeout=config.time_out,
                                            allow_redirects=config.allow_redirects,
                                            auth=config.auth)
                elif json_data:
                    response = requests.put(url=url, params=config.params,
                                            json=json_data,
                                            headers=config.headers,
                                            timeout=config.time_out,
                                            allow_redirects=config.allow_redirects,
                                            auth=config.auth)
                elif files:
                    file_list = files_to_upload(files)
                    response = requests.put(url=url, params=config.params,
                                            timeout=config.time_out,
                                            allow_redirects=config.allow_redirects,
                                            files=file_list,
                                            auth=config.auth)
                else:
                    raise ValueError("Provide either data or json or file/s")
                Logging.write_message_info(
                    'from response is_redirect value is : {} ; '
                    'status code is : {}'.format(response.is_redirect, response.status_code))
                is_redirect = response.is_redirect
                if is_redirect:
                    url = response.headers['Location']
                    Logging.write_message_info('redirect url is  : {}'.format(url))

            (response,
             status_code,
             text,
             json_response,
             http_err_msg,
             json_err_msg) = rest_response_handle(response)
            return APIResponse(response, status_code, text, json_response, http_err_msg,
                               json_err_msg)

        except requests.exceptions.RequestException as ex:
            Logging.write_message_exception("{err_name} on PUT call for url: {url} \n {err_msg}"
                                            .format(err_name=ex.__class__.__name__, url=url,
                                                    err_msg=ex))
            raise ex

    @staticmethod
    def request_patch(config: APIConfigurations, data=None):
        """
        Makes a get HTTP PATCH call and returns APIResponse object.
        APIResponse object will be with data from PATCH call.
        :param config: APIConfigurations object
        :param data : Message body
        :return: APIResponse response object with data from PATCH call
        """
        url = build_url(config)
        try:
            response = requests.patch(url=url, params=config.params,
                                      data=convert_to_json(data),
                                      headers=config.headers,
                                      timeout=config.time_out,
                                      auth=config.auth)
            (response,
             status_code,
             text,
             json_response,
             http_err_msg,
             json_err_msg) = rest_response_handle(response)
            return APIResponse(response, status_code, text, json_response, http_err_msg,
                               json_err_msg)

        except requests.exceptions.RequestException as ex:
            Logging.write_message_exception("{err_name} on PATCH call for url: {url} \n {err_msg}"
                                            .format(err_name=ex.__class__.__name__, url=url,
                                                    err_msg=ex))
            raise ex
