import logging

db_logger = logging.getLogger('db')


def log_exception(error, custom_err_msg=''):
    db_logger.exception(custom_err_msg + '\n' + str(error))


def log_message(message=''):
    db_logger.info(message)
