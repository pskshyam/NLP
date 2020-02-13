from engine.predict import IceDLPredict
from jobs.tasks import get_prediction, LogErrorsTask

def test_get_prediction(mocker):
    mocker.patch.object(IceDLPredict, "predict", return_value = True)
    service_id = "service_id"
    model_name = "model_name"
    data = "data"
    get_prediction(service_id = service_id, model_name=model_name, data=data, use_standard_names = True)
    IceDLPredict(service_id = service_id, model_name=model_name, data=data, use_standard_names = True).predict.assert_called_once_with()

def test_on_failure(mocker):

    mocker.patch.object(LogErrorsTask, "save_failed_task")

    log_error_task = LogErrorsTask()
    exc = ""
    task_id = ""
    args = ""
    kwargs = ""
    einfo = ""

    log_error_task.on_failure(exc=exc, task_id=task_id, args=args, kwargs=kwargs, einfo=einfo)

    log_error_task.save_failed_task.assert_called_once_with(exc, task_id, args, kwargs, einfo)

