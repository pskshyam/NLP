from models.context_extraction.impl.context_parts.agents_extractor import AgentsExtractor
from models.context_extraction.impl.context_parts import agents_extractor
from models.context_extraction import context_extractor


def test_extract(mocker):
    agents_extractor_instance = AgentsExtractor()
    mocker.patch.object(agents_extractor, "retokenize_object_final")
    mocker.patch.object(agents_extractor, "remove_extra_index")
    mocker.patch.object(agents_extractor, "replace_object")
    text_information = mocker.patch.object(context_extractor, 'TextInformation')

    agents_extractor_instance.extract(text_information)

    assert agents_extractor.retokenize_object_final.call_count == 1
    assert agents_extractor.remove_extra_index.call_count == 1
    assert agents_extractor.replace_object.call_count == 1
