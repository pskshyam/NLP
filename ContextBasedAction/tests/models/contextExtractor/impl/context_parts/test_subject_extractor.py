from models.context_extraction.impl.context_parts.subject_extractor import SubjectExtractor
from models.context_extraction.impl.context_parts import subject_extractor
from models.context_extraction import context_extractor


def test_extract(mocker):
    subject_object_extractor_instance = SubjectExtractor()

    mocker.patch.object(subject_extractor, "retokenize_object_final")
    mocker.patch.object(SubjectExtractor, "cut_subject")
    mocker.patch.object(subject_extractor, "replace_object")
    mocker.patch.object(subject_extractor, "remove_extra_index")
    text_information = mocker.patch.object(context_extractor, 'TextInformation')

    subject_object_extractor_instance.extract(text_information)

    assert subject_extractor.retokenize_object_final.call_count == 1
    assert SubjectExtractor.cut_subject.call_count == 1
    assert subject_extractor.replace_object.call_count == 1
    assert subject_extractor.remove_extra_index.call_count == 1


def test_cut_subject_check_tuples_true(mocker):
    actions_structure = [{"doc": "doc_example", "context": {"action_subject": [{"subj1": "value1", "indexes": (1, 2)}],
                                                            "verbs": [{"verb1": "value1", "indexes": (1, 2)}]}
                          }]

    subject_object_extractor_instance = SubjectExtractor()

    mocker.patch.object(subject_extractor, "check_tuples", return_value=True)
    mocker.patch.object(subject_extractor, "cut_element")

    subject_object_extractor_instance.cut_subject(actions_structure)

    assert subject_extractor.check_tuples.call_count == 1
    assert subject_extractor.cut_element.call_count == 1


def test_cut_subject_check_tuples_false(mocker):

    actions_structure = [{"doc": "doc_example", "context": {"action_subject": [{"subj1": "value1", "indexes": (1, 2)}],
                                                            "verbs": [{"verb1": "value1", "indexes": (1, 2)}]}
                          }]

    subject_object_extractor_instance = SubjectExtractor()

    mocker.patch.object(subject_extractor, "check_tuples", return_value=False)
    mocker.patch.object(subject_extractor, "cut_element")

    subject_object_extractor_instance.cut_subject(actions_structure)

    assert subject_extractor.check_tuples.call_count == 1
    assert subject_extractor.cut_element.call_count == 0
