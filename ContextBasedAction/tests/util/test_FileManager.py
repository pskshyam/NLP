import os
import util
import tempfile
from freezegun import freeze_time
import util.FileManager as fm
from falcon_multipart.parser import Parser


def test_create_folder_new(mocker):
    mocker.patch('os.makedirs')
    mocker.patch.object(os.path, 'isdir', return_value = False)
    fm.create_folder('test_path')
    os.path.isdir.assert_called_once_with('test_path')
    os.makedirs.assert_called_once_with('test_path')


def test_create_folder_existing(mocker):
    mocker.patch('os.makedirs')
    mocker.patch.object(os.path, 'isdir', return_value = True)
    fm.create_folder('test_path')
    os.path.isdir.assert_called_once_with('test_path')
    os.makedirs.assert_not_called()


def test_get_temp_path(mocker):
    mocker.patch.object(util.FileManager, 'get_temp_folder', return_value= '/temp')
    res = fm.get_temp_path("test")
    assert res == "/temp/test"


@freeze_time("2018-07-29 09:17:13.812189")
def test_get_new_temp_folder_with_no_name(mocker):
    mocker.patch.object(util.FileManager, 'get_temp_folder', return_value='/temp')
    mocker.patch('util.FileManager.create_folder')
    res = fm.get_new_temp_folder()
    assert res == "/temp/2018_07_29.09_17_13_812189"
    util.FileManager.create_folder.assert_called_once_with(res)


def test_get_new_temp_folder_with_name(mocker):
    mocker.patch.object(util.FileManager, 'get_temp_folder', return_value='/temp')
    mocker.patch('util.FileManager.create_folder')
    res = fm.get_new_temp_folder("test")
    assert res == "/temp/test"
    util.FileManager.create_folder.assert_called_once_with(res)


def test_get_tempfolder(mocker):
    mocker.patch('tempfile.gettempdir')
    fm.get_temp_folder()
    tempfile.gettempdir.assert_called_once_with()

def test_create_temp_file(mocker):
    uploaded_file = Parser()
    with open( os.path.join(os.getcwd(),"config.ini")) as f:
        uploaded_file.file = f
        mocker.patch.object(tempfile, 'gettempdir', return_value = '/temp')
        mocker.patch.object(tempfile, 'NamedTemporaryFile')
        mocker.patch.object(os.path, 'join', return_value = 'path')
        path_returned = util.FileManager.create_temp_file(uploaded_file)
        assert path_returned == 'path'