"""
Helper module for useful functions and tricks
"""
import logging
import json
import glob
import os
from logging.handlers import RotatingFileHandler


def dump(data, data_path):
    """
    Dumps data as a json at data_path

    Parameters
    ----------

    Returns
    -------

    Examples
    --------
    """
    data_dump = open(data_path, "w+")
    data_dump.write(json.dumps(data))
    data_dump.close()
    LOGGER.info("Output file at %s", data_path)

def set_dir(dir_path):
    """
    Creates directory if it does not exist

    Parameters
    ----------

    Returns
    -------

    Examples
    --------
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


# Log settings
LOGGER = logging.getLogger(__name__)
FMT = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s - %(message)s')
LOG_VERSION = len(glob.glob("build_*.log"))
FH = logging.FileHandler("build.log")
CH = logging.StreamHandler()
CH.setLevel(logging.DEBUG)
set_dir("logs/")
RFH = RotatingFileHandler("logs/build.log", maxBytes=10000, backupCount=5)
FH.setFormatter(FMT)
CH.setFormatter(FMT)
LOGGER.addHandler(FH)
LOGGER.addHandler(CH)
LOGGER.addHandler(RFH)
LOGGER.setLevel(logging.DEBUG)
