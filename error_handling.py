import logging

# Set up logging
def setup_logging(log_file='server.log'):
    logging.basicConfig(filename=log_file, level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info('Logging started')

# Log an error message
def log_error(error_message):
    logging.error(error_message)

# Log an info message
def log_info(info_message):
    logging.info(info_message)

# Log a warning message
def log_warning(warning_message):
    logging.warning(warning_message)

