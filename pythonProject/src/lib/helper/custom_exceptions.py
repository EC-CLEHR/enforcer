class CommandLineException(Exception):
    """
    This exception is raised when there is an error while running cmd commands.
    """

    def __init__(self, *args, **kwargs):
        message = 'Unable to run given commands'

        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class DownloadDriverException(Exception):
    """
    This exception is raised when there is an error while saving driver zip file to disk.
    """

    def __init__(self, *args, **kwargs):
        message = 'Unable to download driver from given url.'

        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class BrowserNotFoundException(Exception):
    """
    This exception is raised when required browser is not found.
    """

    def __init__(self, *args, **kwargs):
        message = 'Browser is not found.'

        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class BrowserVersionSupportException(Exception):
    """
    This exception is raised when local browser version is not supported.
    """

    def __init__(self, *args, **kwargs):
        message = 'Local browser version is not supported.'

        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class BrowserVersionFetchException(Exception):
    """
    This exception is raised when there is an error while fetching version of browser installed.
    """

    def __init__(self, *args, **kwargs):
        message = 'Unable to fetch local Browser Version.'

        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class DriverInstanceCreationException(Exception):
    """
    This exception is raised when there is an error while creating driver instance.
    """

    def __init__(self, *args, **kwargs):
        message = 'Unable to create a Driver instance.'

        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class DriverZipUnpackException(Exception):
    """
    This exception is raised when downloaded zip fails to unpack.
    """

    def __init__(self, *args, **kwargs):
        message = 'Unable to open downloaded driver zip file.'

        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class LogDirNotFound(Exception):
    """
    This exception is raised when Logs path is not found in config.ini file.
    """

    def __init__(self, *args, **kwargs):
        message = 'Unable to find log directory from config file. Please check your config file.'

        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class WebdriverOptionMissingException(Exception):
    """
    This exception is raised when some required webdriver option is missing.
    """

    def __init__(self, *args, **kwargs):
        message = 'Webdriver option required for this action is missing.'

        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class BrowserNotSupportedException(Exception):
    """
    This exception is raised when the given browser is not supported.
    """

    def __init__(self, *args, **kwargs):
        message = 'Given browser is not supported'

        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class AWSAccessException(Exception):
    """
    This exception is raised when AWS access key, secret key or Token
    are not provided and not found in OS environment variables.
    """

    def __init__(self, *args, **kwargs):
        message = 'Unable to get access keys and tokens to communicate with AWS/Vault.'

        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class AWSSessionTimeoutException(Exception):
    """
    This exception is raised when current AWS session timesout.
    """

    def __init__(self, *args, **kwargs):
        message = 'AWS session has expired. Please get fresh session and try again.'

        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class AWSClientError(Exception):
    """
    This exception is raised when botocore.exceptions.ClientError exceptions are encountered
    """

    def __init__(self, *args, **kwargs):
        """
        :param response_object: botocore.exceptions.ClientError.response object (dict)
        """
        default_reason = 'unspecified'
        response_object = None
        delegate_to = {'ExpiredToken': AWSSessionTimeoutException}
        if kwargs:
            if 'response_object' in kwargs:
                response_object = kwargs['response_object']
            if 'message' in kwargs:
                msg_stub = kwargs['message']
                msg_found = True
        else:
            response_object = {}
            msg_stub = "AWS/boto3 client error encountered"
            msg_found = False
        error_code = response_object.get('Error', {}).get('Code', default_reason)
        error_msg = response_object.get('Error', {}).get('Message', default_reason)
        delegated_exception = delegate_to.get(error_code, None)
        if delegated_exception:
            raise delegated_exception(error_msg)
        message = "\n".join([msg_stub,
                             f"Error code:  {error_code}",
                             f"Error message:  {error_msg}"])
        args_found = any([args, kwargs])
        if msg_found or not args_found:
            super().__init__(message)
        elif args_found:
            super().__init__(*args, **kwargs)


class EnvironmentException(Exception):
    """
    This exception is raised when the provided environment is NOT supported.
    """

    def __init__(self, *args):

        if args:
            message = f"Please check environment provided. " \
                      f"Given environment \"{args[0]}\" is not supported."
        else:
            message = "Please check environment provided. Given environment is not supported."

        super().__init__(message)


class VaultTokenException(Exception):
    """
    This exception is raised when the provided token for vault is invalid.
    """

    def __init__(self, *args, **kwargs):
        message = 'Unable to authenticate provided Vault token.'

        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class AppiumException(Exception):
    """
    This exception is raised for mobile/appium specific errors
    """

    def __init__(self, *args, **kwargs):
        message = "Appium Exception"
        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class IllegalArgumentError(ValueError):
    """
    This exception is raised for Illegal Argument errors
    """

    def __init__(self, *args, **kwargs):
        message = "Invalid Value is provided as parameter"
        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class SauceLabsNoActiveTunnelsException(Exception):
    """
    This exception is raised when there are no active tunnels
    """

    def __init__(self, *args, **kwargs):
        message = "Saucelabs has no active tunnels"
        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class FilePathNotProvidedException(Exception):
    """
    This exception is raised when at least one filepath also not provided.
    """

    def __init__(self, *args, **kwargs):
        message = "Please provide something in filepaths to attach."
        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class EmailException(Exception):
    """
    This exception is raised for Email specific errors
    """

    def __init__(self, *args, **kwargs):
        message = "Error Occurred while searching the Email"
        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class FileUploadFailedException(Exception):
    """
    This exception is raised when uploading of file fails.
    """

    def __init__(self, *args, **kwargs):
        message = "Uploading of files failed."
        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class OSNotSupportedException(Exception):
    """
    This exception is raised OS is not supported in Platform
    """

    def __init__(self, *args, **kwargs):
        message = "OS not supported"
        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)


class InvalidParamsCountException(Exception):
    """
    This exception is raised when params count is invalid.
    """

    def __init__(self, *args, **kwargs):
        message = "Provide valid params count"
        if args or kwargs:
            super().__init__(*args, **kwargs)
        else:
            super().__init__(message)
