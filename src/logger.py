import logging

# Set debug level and path for log file.
def setup_logger(level, log_path):
    c_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(filename=log_path)
    file_handler.setFormatter(c_formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(c_formatter)
    logging.getLogger().setLevel(level)
    logging.getLogger().addHandler(file_handler)
    logging.getLogger().addHandler(stream_handler)

# Function for debug messages print. Acts like `print()` function, but prints
# the output to the specified log file.
# Use it as normal `print()` when expecting some errors to occur.
def debug(format, *args, **kwargs):
    logging.debug(format, *args, **kwargs)

# Function for info messages print. Acts like `print()` function, but prints
# the output to the specified log file.
# Used to define current program states, mainly in the core.
def info(format, *args, **kwargs):
    logging.info(format, *args, **kwargs)

# Function for warning messages print. Acts like `print()` function, but prints
# the output to the specified log file.
# Used on errors.
def warn(format, *args, **kwargs):
    logging.warning(format, *args, **kwargs)
