from models.context_extraction import context_extractor
from models.context_extraction.context_extractor import ContextExtractor
import pytest

def test_get_conversational_true():
    context_extractor_instance = ContextExtractor()

    kwargs = {"conversational": "true"}

    get_conversational_return = context_extractor_instance.get_conversational(**kwargs)
    assert get_conversational_return


def test_get_conversational_false():
    context_extractor_instance = ContextExtractor()

    kwargs = {"conversational": "false"}

    get_conversational_return = context_extractor_instance.get_conversational(**kwargs)
    assert not get_conversational_return


def test_get_conversational_error(mocker):
    with pytest.raises(Exception):
        context_extractor_instance = ContextExtractor()
        mocker.patch.object(ContextExtractor, 'raise_wrong_value')
        kwargs = {"conversational": "error_value"}

        context_extractor_instance.get_conversational(**kwargs)
        assert ContextExtractor.raise_wrong_value.call_count == 1


def test_raise_wrong_value():
    with pytest.raises(Exception):
        context_extractor_instance = ContextExtractor()
        context_extractor_instance.raise_wrong_value("test_parameter")


def test_predict(mocker):

    context_extractor_instance = ContextExtractor()
    mocker.patch.object(context_extractor, 'preprocess_text')
    mocker.patch.object(context_extractor, 'TextInformation')

    mocker.patch.object(ContextExtractor, 'get_conversational', return_value=True)
    mocker.patch.object(ContextExtractor, 'create_pipeline', return_value=[])
    mocker.patch.object(ContextExtractor, 'execute_pipeline')

    kwargs = {"conversational": "true"}
    context_extractor_instance.predict("text", **kwargs)

    context_extractor.preprocess_text.assert_called_once_with("text", True)
    assert context_extractor.TextInformation.call_count == 1

    assert ContextExtractor.create_pipeline.call_count == 1
    assert ContextExtractor.execute_pipeline.call_count == 1


def test_create_pipeline(mocker):

    context_extractor_instance = ContextExtractor()
    mocker.patch.object(context_extractor, 'VerbsExtractor')
    mocker.patch.object(context_extractor, 'AgentsExtractor')
    mocker.patch.object(context_extractor, 'IndirectObjectExtractor')
    mocker.patch.object(context_extractor, 'AdverbModExtractor')
    mocker.patch.object(context_extractor, 'DirectObjectExtractor')
    mocker.patch.object(context_extractor, 'SubjectExtractor')
    mocker.patch.object(context_extractor, 'ActionExtractor')

    context_extractor_instance.create_pipeline()

    assert context_extractor.VerbsExtractor.call_count == 1
    assert context_extractor.AgentsExtractor.call_count == 1
    assert context_extractor.IndirectObjectExtractor.call_count == 1
    assert context_extractor.AdverbModExtractor.call_count == 1
    assert context_extractor.DirectObjectExtractor.call_count == 1
    assert context_extractor.SubjectExtractor.call_count == 1
    assert context_extractor.ActionExtractor.call_count == 1


def test_execute_pipeline(mocker):

    context_extractor_instance = ContextExtractor()
    mocker.patch.object(context_extractor.VerbsExtractor, 'extract')
    verb = mocker.patch.object(context_extractor, 'VerbsExtractor')
    agents = mocker.patch.object(context_extractor, 'AgentsExtractor')
    indirect = mocker.patch.object(context_extractor, 'IndirectObjectExtractor')
    adverb = mocker.patch.object(context_extractor, 'AdverbModExtractor')
    direct = mocker.patch.object(context_extractor, 'DirectObjectExtractor')
    subject = mocker.patch.object(context_extractor, 'SubjectExtractor')
    action = mocker.patch.object(context_extractor, 'ActionExtractor')
    pipeline = [verb, agents, indirect, adverb, direct, subject, action]

    mocker.patch.object(ContextExtractor, 'create_pipeline', return_value=[])
    text_information = mocker.patch.object(context_extractor, 'TextInformation')
    context_extractor_instance.execute_pipeline(pipeline, text_information)

    assert context_extractor.VerbsExtractor.extract.call_count == 1
    assert context_extractor.AgentsExtractor.extract.call_count == 1
    assert context_extractor.IndirectObjectExtractor.extract.call_count == 1
    assert context_extractor.AdverbModExtractor.extract.call_count == 1
    assert context_extractor.DirectObjectExtractor.extract.call_count == 1
    assert context_extractor.SubjectExtractor.extract.call_count == 1
    assert context_extractor.ActionExtractor.extract.call_count == 1