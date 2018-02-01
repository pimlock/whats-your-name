import logging

import sys


def setup_lambda_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)


def _setup_custom_handler():
    """
    Disabling this for now - if we log in different format than default format of Lambda than
    logs that are multiline are not parsed correctly by CloudWatch Logs.
    """
    # remove all the default handlers that AWSLambda is adding
    root_logger = logging.getLogger()
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    formatter = logging.Formatter('%(asctime)-15s [%(levelname)s] %(name)s - %(message)s')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    root_logger.addHandler(stdout_handler)
