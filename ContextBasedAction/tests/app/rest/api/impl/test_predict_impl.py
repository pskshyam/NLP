from store.manage_file import manage_temp_file
from falcon_multipart.parser import Parser


def test_manage_temp_file_exc(mocker):
    image = Parser()
    image.filename = "no_image"
    file_name = 'file_to_testing'
    msg = 'The file format is not supported'
    mocker.patch("app.rest.api.impl.predict_impl.create_temp_file", return_value = file_name)
    try:
        manage_temp_file(image)
    except ValueError as exc:
        assert str(exc)==msg
    store.predict_impl.create_temp_file.assert_not_called()