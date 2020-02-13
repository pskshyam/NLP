import os
import datetime
import tempfile

def get_temp_folder():
    """

    :return:
    """
    return tempfile.gettempdir()


def get_new_temp_folder(name=None):
    """

    :param name:
    :return:
    """
    folder_name = datetime.datetime.now().strftime('%Y_%m_%d.%H_%M_%S_%f') if name is None else name
    folder_path = os.path.join(get_temp_folder(), folder_name)
    create_folder(folder_path)
    return folder_path


def create_folder(path):
    """

    :param path:
    :return:
    """
    if not os.path.isdir(path):
        os.makedirs(path)


def get_temp_path(name):
    """

    :param name:
    :return:
    """
    return os.path.join(get_temp_folder(), name)


def remove_dir(path):
    """

    :param path:
    :return:
    """
    import shutil
    if os.path.exists(path):
        shutil.rmtree(path)

def create_temp_file(text):
    """

    :param uploaded_file:
    :return:
    """
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(text)
        f.flush()
        f.seek(0)
        f.close()
        file_path = tempfile.gettempdir()
        file_name = f.name
        path = os.path.join(file_path, file_name)
        return path