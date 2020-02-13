from models.context_extraction.impl.text_information import TextInformation
from models.context_extraction.impl import text_information


def test_text_information(mocker):

    mocker.patch.object(text_information, 'get_doc', return_value="test_return")
    mocker.patch.object(text_information, 'get_all_replacements')
    mocker.patch.object(text_information, 'get_actions_information_structure')

    test_text = "test text."

    TextInformation(test_text)

    text_information.get_doc.assert_called_with(test_text)
    text_information.get_all_replacements.assert_called_with("test_return")
    text_information.get_actions_information_structure.assert_called_with("test_return")
