from models.context_extraction.impl.context_parts.direct_object_extractor import DirectObjectExtractor
from models.context_extraction.impl.context_parts import direct_object_extractor
from models.context_extraction import context_extractor


def test_extract(mocker):
    direct_object_extractor_instance = DirectObjectExtractor()

    mocker.patch.object(direct_object_extractor, "retokenize_object_final")
    mocker.patch.object(direct_object_extractor, "cut_objects")
    mocker.patch.object(direct_object_extractor, "remove_repeated_components")
    mocker.patch.object(direct_object_extractor, "replace_object")
    mocker.patch.object(direct_object_extractor, "remove_extra_index")
    text_information = mocker.patch.object(context_extractor, 'TextInformation')

    direct_object_extractor_instance.extract(text_information)

    assert direct_object_extractor.retokenize_object_final.call_count == 2
    assert direct_object_extractor.cut_objects.call_count == 2
    assert direct_object_extractor.remove_repeated_components.call_count == 2
    assert direct_object_extractor.replace_object.call_count == 2
    assert direct_object_extractor.remove_extra_index.call_count == 2
