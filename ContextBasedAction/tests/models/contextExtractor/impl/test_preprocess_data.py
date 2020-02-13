from models.context_extraction.impl import preprocess_data
import spacy
import pytest
import re


def get_doc_example(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return doc


def test_preprocess_text_conversational(mocker):

    mocker.patch.object(preprocess_data, 'transform_conversation', return_value="test_return")
    mocker.patch.object(preprocess_data, 'replace_marks', return_value="test_return")

    test_text = "test_return"
    preprocess_data.preprocess_text(test_text, True)

    preprocess_data.transform_conversation.assert_called_with([test_text])
    preprocess_data.replace_marks.call_count == 1


def test_preprocess_text_non_conversational(mocker):

    mocker.patch.object(preprocess_data, 'transform_conversation', return_value="test_return")
    mocker.patch.object(preprocess_data, 'replace_marks', return_value="test_return_text")
    mocker.patch.object(preprocess_data, 'get_doc', return_value="test_return_doc")
    mocker.patch.object(preprocess_data, 'clean_data', return_value="test_return_text")

    test_text = "test text."
    preprocess_data.preprocess_text(test_text, False)

    preprocess_data.transform_conversation.assert_not_called()
    preprocess_data.replace_marks.assert_called_with(test_text)
    preprocess_data.get_doc.assert_called_with("test_return_text")
    preprocess_data.clean_data.assert_called_with("test_return_doc")


def test_transform_conversation(mocker):

    mocker.patch.object(preprocess_data, 'transform_sentence', return_value="transformed_sentence")

    test_texts_list = ["first text.", "second text."]
    preprocess_data.transform_conversation(test_texts_list)

    assert preprocess_data.transform_sentence.call_count == len(test_texts_list)


def test_get_colons_index(mocker):

    mocker.patch.object(preprocess_data, 'transform_sentence', return_value="transformed_sentence")

    doc = get_doc_example("Person name: example text.")
    colon_index = preprocess_data.get_colons_index(doc)

    assert colon_index == 2


def test_get_colons_index_no_colons(mocker):

    mocker.patch.object(preprocess_data, 'transform_sentence', return_value="transformed_sentence")

    doc = get_doc_example("Person name example text.")

    with pytest.raises(Exception) as ex:
        preprocess_data.get_colons_index(doc)

    assert "Text has not a valid conversational format" in str(ex.value)


def test_transform_sentence(mocker):

    test_text = "Person name: example text."
    doc = get_doc_example(test_text)

    mocker.patch.object(preprocess_data, 'get_doc', return_value=doc)
    mocker.patch.object(preprocess_data, 'get_colons_index', return_value=2)

    preprocess_data.transform_sentence(test_text)

    preprocess_data.get_doc.assert_called_with(test_text)
    preprocess_data.get_colons_index.assert_called_with(doc)


def test_replace_marks(mocker):

    mocker.patch("re.sub")
    preprocess_data.replace_marks("")

    assert re.sub.call_count == 5


def test_replace_text(mocker):
    test_text = "Person name?? example text."
    mocker.patch.object(preprocess_data, 'replace_str', return_value=test_text)
    text_out = preprocess_data.replace_text(test_text)
    assert preprocess_data.replace_str.call_count == 2
    assert isinstance(text_out, str)


def test_replace_str():
    test_text = "Person name?? example text."
    str_to_rep = "a"
    str_rep = "a"
    text_out = preprocess_data.replace_str(test_text, str_to_rep, str_rep)
    assert isinstance(text_out, str)


def test_get_nearest_token_index_true():
    doc = get_doc_example("Sam'd cut the paper.")
    index = 1
    nearest_token = preprocess_data.get_nearest_token_index(doc, index)
    assert nearest_token == 2


def test_get_nearest_token_index_true_adv():
    doc = get_doc_example("He'd probably be there to visit her.")
    index = 1
    nearest_token = preprocess_data.get_nearest_token_index(doc, index)
    assert nearest_token == 3


def test_get_nearest_token_index_false():
    doc = get_doc_example("He would.")
    index = 1
    nearest_token = preprocess_data.get_nearest_token_index(doc, index)
    assert nearest_token == -1


def test_expand_contracted_auxiliar_nearest_token_call(mocker):
    doc = get_doc_example("He'd probably be there to visit her.")
    i = 0
    token = doc[0]
    mocker.patch.object(preprocess_data, 'get_nearest_token_index', return_value=-1)

    preprocess_data.expand_contracted_auxiliar(doc, i, token)

    assert preprocess_data.get_nearest_token_index.call_count == 1


def test_expand_contracted_auxiliar_nearest_token_not_call(mocker):
    doc = get_doc_example("He'll probably be there to visit her.")
    i = 0
    token = doc[0]
    mocker.patch.object(preprocess_data, 'get_nearest_token_index', return_value=-1)

    preprocess_data.expand_contracted_auxiliar(doc, i, token)

    assert preprocess_data.get_nearest_token_index.call_count == 0


def test_clean_data():

    test_text = "Person  name   example  text . "
    doc = get_doc_example(test_text)

    clean_text = preprocess_data.clean_data(doc)

    assert isinstance(clean_text, str)


