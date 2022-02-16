import logging

# Global formatter for logging
c_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Mutable global with logging level
m_level = 'INFO'

# Used to set the custom path for log file
def set_log_path(log_path):
    file_handler = logging.FileHandler(filename=log_path)
    file_handler.setFormatter(c_formatter)
    logging.getLogger().setLevel(m_level)
    logging.getLogger().addHandler(file_handler)

# Includes debugging in log file
def set_debug_level():
    global m_level
    m_level = 'DEBUG'
    logging.getLogger().setLevel('DEBUG')

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
