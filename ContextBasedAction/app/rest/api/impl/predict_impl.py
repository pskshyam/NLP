import tempfile
import logging
import os
import base64
from util.FileManager import create_temp_file
logger = logging.getLogger(__name__)

def manage_file(uploaded_file):
    """

    :param uploaded_file:
    :return:
    """
    temp_file = manage_temp_file(uploaded_file)
    file_name = uploaded_file.filename
    if file_name.endswith('.txt'):
        with open(temp_file, "rb") as image_file:
            encoded_string = image_file.read().decode('utf-8')
    else:
        raise ValueError('The file format is not supported')
    os.remove(temp_file)
    return encoded_string


def manage_temp_file(uploaded_file):
    """

    :param uploaded_file:
    :return:
    """
    file_name = uploaded_file.filename
    if file_name.endswith('.txt'):
        temp_file = create_temp_file(uploaded_file.file.read())
        return temp_file
    else:
        raise ValueError('The file format is not supported')

