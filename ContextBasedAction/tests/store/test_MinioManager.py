from minio import Minio
from minio.definitions import Object
from unittest import mock
from store.MinioManager import ICEDLStore
from util.config.idl_config import idl_config
import os
import shutil
import diskcache

def test_get_buckets(mocker):
    mocker.patch.object(Minio, 'list_buckets')
    ice_dl_manager = ICEDLStore()
    bukets = ice_dl_manager._get_buckets()
    assert ice_dl_manager.connection.list_buckets.call_count ==2
    assert isinstance(bukets, list)

def test_get_cache(mocker):
    mocker.patch.object(Minio, 'list_buckets')
    ice_dl_manager = ICEDLStore()
    cache = ice_dl_manager._get_cache()
    assert isinstance(cache, diskcache.Cache)

def test_store_model_files_in_local(mocker):
    """

    :param mocker:
    :return:
    """
    model_name = "test_name"
    path = os.path.join(idl_config.local_model_config_store_path, model_name)
    mocker.patch.object(Minio, 'list_buckets')
    ice_dl_manager = ICEDLStore()
    mocker.patch.object(os.path, 'join', return_value=path)
    mocker.patch.object(ICEDLStore, "_write_response_in_file")
    mocker.patch.object(ICEDLStore, "_update_local_date")
    mocker.patch("os.path.exists")
    mocker.patch("os.path.isdir")
    mocker.patch("os.makedirs")
    mocker.patch("shutil.rmtree")
    dict_response = {}

    file_paths = ice_dl_manager._store_model_files_in_local(model_name, dict_response)

    os.path.join.assert_called_once_with(idl_config.local_model_config_store_path, model_name)
    assert os.path.exists.call_count == 1
    assert os.path.isdir.call_count == 1
    shutil.rmtree.assert_called_once_with(path)
    os.makedirs.assert_not_called()
    ice_dl_manager._update_local_date.assert_called_once_with(model_name)
    assert ice_dl_manager._write_response_in_file.call_count == len(dict_response.items())
    assert isinstance(file_paths, list)

def test_get_model_files_from_local(mocker):
    model_name = "test_name"
    path = os.path.join(idl_config.local_model_config_store_path)
    mocker.patch.object(Minio, 'list_buckets')
    ice_dl_manager = ICEDLStore()
    mocker.patch("os.listdir", return_value = [""])
    mocker.patch.object(os.path, 'join', return_value=path)

    ice_dl_manager._get_model_files_from_local(model_name)
    assert os.path.join.call_count == 2

def test_get_model_files_from_minio(mocker):
    """

    :param mocker:
    :return:
    """
    mocker.patch.object(Minio, 'list_buckets')
    ice_dl_manager = ICEDLStore()
    model_name = "model_name"
    mocker.patch.object(ICEDLStore, "_check_bucket")
    mocker.patch.object(Minio, 'list_objects')
    mocker.patch.object(Minio, 'get_object')
    mocker.patch.object(ICEDLStore, '_store_model_files_in_local', return_value = [])
    file_paths = ice_dl_manager._get_model_files_from_minio(model_name)
    ice_dl_manager._check_bucket.assert_called_once_with(model_name)
    assert isinstance(file_paths, list)



def test_get_model_files_outdated(mocker):
    mocker.patch.object(Minio, 'list_buckets')
    ice_dl_manager = ICEDLStore()
    model_config_dict = {
        "model_name": "invoice-extraction",
        "model_class": "models.invoice_extraction.InvoiceModel.InvoiceModel",
        "prediction_status": "prediction_failed",
        "prediction_status_message": "Incorrect padding",
        "updated_at": 1,
        "model_config_documents": {
            "data_file": "invoice.data",
            "conf_file": "invoice-yolov3.cfg",
            "weight_file": "pesos.weights",
            "names_file": "invoice.names"}
    }

    mocker.patch.object(ICEDLStore, "_is_local_date_updated", return_value = True)
    mocker.patch.object(ICEDLStore, "_check_local_model", return_value = True)
    mocker.patch.object(ICEDLStore, "_get_model_files_from_local")
    mocker.patch.object(ICEDLStore, "_get_model_files_from_minio")
    mocker.patch.object(ICEDLStore, "_create_config_files_dict", return_value = {})
    supporting_files = ice_dl_manager.get_model_files(model_config_dict)

    ice_dl_manager._get_model_files_from_local.assert_called_once_with(model_config_dict["model_name"])
    ice_dl_manager._get_model_files_from_minio.assert_not_called()
    assert ice_dl_manager._create_config_files_dict.call_count == 1
    assert isinstance(supporting_files, dict)

def test_get_model_files_updated(mocker):
    mocker.patch.object(Minio, 'list_buckets')
    ice_dl_manager = ICEDLStore()
    model_config_dict = {
    "model_name" : "invoice-extraction",
    "model_class" : "models.invoice_extraction.InvoiceModel.InvoiceModel",
    "prediction_status" : "prediction_failed",
    "prediction_status_message" : "Incorrect padding",
    "updated_at": 1,
    "model_config_documents" : {
        "data_file" : "invoice.data",
        "conf_file" : "invoice-yolov3.cfg",
        "weight_file" : "pesos.weights",
        "names_file" : "invoice.names"}
    }

    mocker.patch.object(ICEDLStore, "_is_local_date_updated", return_value = False)
    mocker.patch.object(ICEDLStore, "_check_local_model", return_value = False)
    mocker.patch.object(ICEDLStore, "_get_model_files_from_local")
    mocker.patch.object(ICEDLStore, "_get_model_files_from_minio")
    mocker.patch.object(ICEDLStore, "_check_model_config_files_names")
    mocker.patch.object(ICEDLStore, "_create_config_files_dict", return_value = {})
    supporting_files = ice_dl_manager.get_model_files(model_config_dict)

    ice_dl_manager._get_model_files_from_minio.assert_called_once_with(model_config_dict["model_name"])
    ice_dl_manager._get_model_files_from_local.assert_not_called()
    assert ice_dl_manager._create_config_files_dict.call_count == 1
    assert isinstance(supporting_files, dict)


def test_create_config_files_dict(mocker):
    mocker.MagicMock(Minio)
    mocker.patch.object(Minio, 'list_buckets')
    config_file_list = ['path/file1', 'path/file2', 'path/file3', 'path/file4']
    model_param_dict = {"model_config_documents": {
        "data_file": "file1",
        "conf_file": "file2",
        "conf_file": "file2",
        "weight_file": "file3",
        "names_file": "file4"
    }}
    ice_dl_manager = ICEDLStore()
    config_files_dict = ice_dl_manager._create_config_files_dict(config_file_list,model_param_dict)
    assert isinstance(config_files_dict, dict)


def test_check_model_config_files_name_same_files(mocker):
    mocker.MagicMock(Minio)
    mocker.patch.object(Minio, 'list_buckets')
    model_param_dict = {
        "model_name": "invoice-extraction",
        "model_class": "models.invoice_extraction.InvoiceModel.InvoiceModel",
        "prediction_status": "prediction_failed",
        "prediction_status_message": "Incorrect padding",
        "model_config_documents": {
            "data_file": "name1"
        }
    }
    object_minio = Object(bucket_name="", object_name="name1", last_modified="", etag="", size=0)

    mocker.patch.object(Minio, 'list_objects', return_value=[object_minio])
    ice_dl_manager = ICEDLStore()
    mocker.patch.object(ice_dl_manager, 'raise_exception')
    ice_dl_manager._check_model_config_files_names(model_param_dict)
    ice_dl_manager.raise_exception.assert_not_called()


def test_update_local_date(mocker):
    model_name = "model_name"
    mocker.patch.object(Minio, 'list_buckets')
    mocker.patch.object(ICEDLStore, "_get_cache")
    ice_dl_manager = ICEDLStore()
    ice_dl_manager._update_local_date(model_name)
    ice_dl_manager._get_cache.assert_called_once_with()


def test_get_connection_none(mocker):
    mocker.patch.object(Minio, 'list_buckets')
    ice_dl_manager = ICEDLStore()
    mocker.MagicMock(Minio)
    ice_dl_manager.connection = None
    connection = ice_dl_manager._get_connection()

    assert isinstance(connection, Minio)

def test_get_connection(mocker):
    mocker.patch.object(Minio, 'list_buckets')
    ice_dl_manager = ICEDLStore()
    minio_connection = mocker.MagicMock(Minio)
    ice_dl_manager.connection = minio_connection
    connection = ice_dl_manager._get_connection()
    assert isinstance(connection, Minio)

def test__check_local_model_true(mocker):
    model_name = "model_name"
    mocker.patch("os.path.exists", return_value = True)
    mocker.patch("os.listdir", return_value=[model_name])
    mocker.patch.object(Minio, 'list_buckets')
    ice_dl_manager = ICEDLStore()
    bool_value = ice_dl_manager._check_local_model(model_name)
    assert  bool_value == True

def test__check_local_model_false_extists(mocker):
    model_name = "model_name"
    mocker.patch("os.path.exists", return_value = False)
    mocker.patch("os.listdir", return_value=[model_name])
    mocker.patch.object(Minio, 'list_buckets')
    ice_dl_manager = ICEDLStore()
    bool_value = ice_dl_manager._check_local_model(model_name)
    assert bool_value == False

def test__check_local_model_false_any(mocker):
    model_name = "model_name"
    mocker.patch("os.path.exists", return_value = True)
    mocker.patch("os.listdir", return_value=[""])
    mocker.patch.object(Minio, 'list_buckets')
    ice_dl_manager = ICEDLStore()
    bool_value = ice_dl_manager._check_local_model(model_name)
    assert bool_value == False

def test__check_local_model_false_all(mocker):
    model_name = "model_name"
    mocker.patch("os.path.exists", return_value = False)
    mocker.patch("os.listdir", return_value=[""])
    mocker.patch.object(Minio, 'list_buckets')
    ice_dl_manager = ICEDLStore()
    bool_value = ice_dl_manager._check_local_model(model_name)
    assert bool_value == False

def test_is_local_date_updated_true(mocker):
    model_name = "model_name"
    model_date = "model_date"
    mocker.patch.object(Minio, 'list_buckets')
    mocker.patch.object(ICEDLStore, "_get_cache", return_value = {model_name:model_date})
    ice_dl_manager = ICEDLStore()
    bool_value = ice_dl_manager._is_local_date_updated(model_name, model_date)
    assert bool_value == True

def test_is_local_date_updated_false_cache(mocker):
    model_name = "model_name"
    model_date = "model_date"
    mocker.patch.object(Minio, 'list_buckets')
    mocker.patch.object(ICEDLStore, "_get_cache", return_value = {})
    ice_dl_manager = ICEDLStore()
    bool_value = ice_dl_manager._is_local_date_updated(model_name, model_date)
    assert bool_value == False

def test_is_local_date_updated_false_keys(mocker):
    model_name = "model_name"
    model_date = "model_date"
    mocker.patch.object(Minio, 'list_buckets')
    mocker.patch.object(ICEDLStore, "_get_cache", return_value = {model_name+" ":model_date})
    ice_dl_manager = ICEDLStore()
    bool_value = ice_dl_manager._is_local_date_updated(model_name, model_date)
    assert bool_value == False

def test_is_local_date_updated_false_all(mocker):
    model_name = "model_name"
    model_date = "model_date"
    mocker.patch.object(Minio, 'list_buckets')
    mocker.patch.object(ICEDLStore, "_get_cache", return_value = {model_name+" ":model_date+" "})
    ice_dl_manager = ICEDLStore()
    bool_value = ice_dl_manager._is_local_date_updated(model_name, model_date)
    assert bool_value == False
