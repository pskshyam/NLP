from engine.predict import IceDLPredict
import engine
import importlib

def test_predict(mocker, monkeypatch):

    modelinfomanger_mock = mocker.patch('engine.predict.ModelInfoManager')
    mocker.patch('engine.predict.ModelManager')
    load_model_mock = mocker.patch('engine.predict.IceDLPredict._load_model')
    mock_model = load_model_mock.return_value
    mock_model.predict.return_value = "mock_prediction"
    monkeypatch.setattr(modelinfomanger_mock, 'STATUS_PREDICTION_SUCCESS', 'prediction_success')
    kwargs = {"data": "test_data", 'use_standard_names': True}
    cut = IceDLPredict("service_id", "model_name", **kwargs)
    cut.query = "test_query"
    config = {
        '$set': {
            'prediction': 'mock_prediction',
            'prediction_status': 'prediction_success',
            'prediction_status_message': 'Prediction completed succesfully'}
    }

    cut.predict()
    mock_instance = modelinfomanger_mock.return_value
    mock_instance.update.assert_called_once_with("test_query", config)


def raise_exception():
    raise Exception("Exception")


def test_predict_exception(mocker, monkeypatch):
    modelinfomanger_mock = mocker.patch('engine.predict.ModelInfoManager')
    mocker.patch('engine.predict.ModelManager')
    load_model_mock = mocker.patch('engine.predict.IceDLPredict._load_model')
    mock_model = load_model_mock.return_value
    mock_model.predict.side_effect = Exception("Exception")
    monkeypatch.setattr(modelinfomanger_mock, 'STATUS_PREDICTION_FAILED', 'prediction_failure')

    kwargs = {"data": "test_data", 'use_standard_names': True}
    cut = IceDLPredict("service_id", "model_name", **kwargs)

    cut.query = "test_query"
    config = {
        '$set': {
            'prediction_status': 'prediction_failure',
            'prediction_status_message': 'Exception'}
    }

    cut.predict()

    mock_instance = modelinfomanger_mock.return_value
    mock_instance.update.assert_called_once_with("test_query", config)


def test_load_model(mocker):
    modelinfomanger_mock = mocker.patch('engine.predict.ModelInfoManager')
    modelmanager_mock = mocker.patch('engine.predict.ModelManager')
    ICEDLStore_mock = mocker.patch('engine.predict.ICEDLStore')
    mocker.patch.object(importlib, 'import_module', return_value="mock_module")
    mocker.patch('engine.predict.IceDLPredict.instantiate_class')

    modelmanager_mock.return_value.get_model.return_value = {"model_class":"testpackage.testclass"}
    ICEDLStore_mock.return_value.get_model_files.return_value = "mock_data"

    kwargs = {"data": "test_data", 'use_standard_names': True}
    cut = IceDLPredict("service_id", "model_name", **kwargs)
    cut._load_model()

    engine.predict.IceDLPredict.instantiate_class.assert_called_once_with('mock_module', 'testclass', "mock_data")