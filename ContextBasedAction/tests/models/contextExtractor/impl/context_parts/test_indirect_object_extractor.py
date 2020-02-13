from models.context_extraction.impl.context_parts.indirect_object_extractor import IndirectObjectExtractor
from models.context_extraction.impl.context_parts import indirect_object_extractor
from models.context_extraction import context_extractor


def test_extract(mocker):
    indirect_object_extractor_instance = IndirectObjectExtractor()

    mocker.patch.object(indirect_object_extractor, "retokenize_object_final")
    mocker.patch.object(indirect_object_extractor, "cut_objects")
    mocker.patch.object(indirect_object_extractor, "replace_object")
    mocker.patch.object(indirect_object_extractor, "remove_extra_index")
    text_information = mocker.patch.object(context_extractor, 'TextInformation')

    indirect_object_extractor_instance.extract(text_information)

    assert indirect_object_extractor.retokenize_object_final.call_count == 1
    assert indirect_object_extractor.cut_objects.call_count == 1
    assert indirect_object_extractor.replace_object.call_count == 1
    assert indirect_object_extractor.remove_extra_index.call_count == 1
