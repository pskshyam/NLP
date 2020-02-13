from models.context_extraction.impl.context_parts.verbs_extractor import VerbsExtractor
from models.context_extraction import context_extractor
import textacy
import spacy


def get_doc_example(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return doc


def test_extract(mocker):
    verbs_extractor_instance = VerbsExtractor()

    mocker.patch.object(VerbsExtractor, "verb_extraction")
    text_information = mocker.patch.object(context_extractor, 'TextInformation')

    verbs_extractor_instance.extract(text_information)

    assert VerbsExtractor.verb_extraction.call_count == 1


def test_verb_extraction_active(mocker):

    verb_dict = {'pos_': ['VERB'], 'initial_value': 'is', 'aux': False,
                'replacement_value': 'is', 'indexes': (1, 2),
                'dep_': ['ROOT'], 'active': True}

    verbs_extractor_instance = VerbsExtractor()

    mocker.patch.object(textacy.extract, "pos_regex_matches", return_value=["test_element"])
    mocker.patch.object(VerbsExtractor, "filtering_verbs")
    mocker.patch.object(VerbsExtractor, "clean_init_verb", return_value=["", verb_dict])
    mocker.patch.object(VerbsExtractor, "clean_aux_passive")

    verbs_extractor_instance.verb_extraction([{"doc": "doc_example",
                                                   "context": {"obj_type": ""}}])

    assert VerbsExtractor.filtering_verbs.call_count == 1
    assert VerbsExtractor.clean_init_verb.call_count == 1
    assert VerbsExtractor.clean_aux_passive.call_count == 0


def test_verb_extraction_passive(mocker):

    verb_dict = {'pos_': ['VERB', 'VERB'], 'initial_value': 'was eaten', 'aux': False,
                 'replacement_value': 'was eaten', 'indexes': (2, 4),
                 'dep_': ['auxpass', 'ROOT'], 'active': True}

    verbs_extractor_instance = VerbsExtractor()

    mocker.patch.object(textacy.extract, "pos_regex_matches", return_value=["test_element"])
    mocker.patch.object(VerbsExtractor, "filtering_verbs")
    mocker.patch.object(VerbsExtractor, "clean_init_verb", return_value=["", verb_dict])
    mocker.patch.object(VerbsExtractor, "clean_aux_passive")

    verbs_extractor_instance.verb_extraction([{"doc": "doc_example",
                                                   "context": {"obj_type": ""}}])

    assert VerbsExtractor.filtering_verbs.call_count == 1
    assert VerbsExtractor.clean_init_verb.call_count == 1
    assert VerbsExtractor.clean_aux_passive.call_count == 1


def test_filtering_verbs_cut_verbs(mocker):

    verb_dict = {'replacement_value': 'well trained', 'pos_': ['ADV', 'VERB'],
                 'aux': False, 'indexes': (3, 5), 'dep_': ['advmod', 'amod'],
                 'initial_value': 'well trained', 'active': True}

    verbs_extractor_instance = VerbsExtractor()

    mocker.patch.object(VerbsExtractor, "cut_verbs", return_value={})

    filtering_verbs_result = verbs_extractor_instance.filtering_verbs(verb_dict, [1, 2], "")

    assert VerbsExtractor.cut_verbs.call_count == 1
    assert isinstance(filtering_verbs_result, dict)


def test_filtering_verbs_not_cut_verbs(mocker):
    verb_dict = {'replacement_value': 'well trained', 'pos_': ['ADV', 'VERB'],
                 'aux': False, 'indexes': (3, 5), 'dep_': ['advmod', 'amod'],
                 'initial_value': 'well trained', 'active': True}

    verbs_extractor_instance = VerbsExtractor()

    mocker.patch.object(VerbsExtractor, "cut_verbs")

    filtering_verbs_result = verbs_extractor_instance.filtering_verbs(verb_dict, [1], "")

    assert VerbsExtractor.cut_verbs.call_count == 0
    assert not filtering_verbs_result


def test_cut_verbs_dict():
    doc = get_doc_example("He is a well trained athlete.")
    span = doc[3:5]
    verbs_extractor_instance = VerbsExtractor()

    cut_verbs_result = verbs_extractor_instance.cut_verbs({}, span, doc)

    assert isinstance(cut_verbs_result, dict)


def test_cut_verbs_empty():
    doc = get_doc_example("He")
    span = doc[2:4]
    verbs_extractor_instance = VerbsExtractor()

    cut_verbs_result = verbs_extractor_instance.cut_verbs({}, span, doc)

    assert not cut_verbs_result


def test_clean_aux_passive_true():

    doc = get_doc_example("The food was eaten by the dogs.")
    span = doc[2:3]
    verb_dict = {'pos_': ['VERB', 'VERB'], 'initial_value': 'was eaten', 'aux': False,
                 'replacement_value': 'was eaten', 'indexes': (2, 4),
                 'dep_': ['auxpass', 'ROOT'], 'active': True}

    verbs_extractor_instance = VerbsExtractor()

    clean_aux_passive_result = verbs_extractor_instance.clean_aux_passive(span, verb_dict)

    assert not clean_aux_passive_result['active']


def test_clean_init_verb():

    pos_to_remove = ['CCONJ', 'PART']
    doc = get_doc_example("He is a well trained athlete.")
    span = doc[3:5]

    verbs_extractor_instance = VerbsExtractor()

    span_return, verb_dict_return = verbs_extractor_instance.clean_init_verb(pos_to_remove, doc, span)

    assert span_return.text == "well trained"
    assert verb_dict_return["indexes"] == (3, 5)
