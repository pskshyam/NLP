from models.context_extraction.impl import utils
import spacy
from spacy.tokens import Doc


def get_doc_example(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return doc


def test_get_doc_neuralcoref():
    test_sentence = "Sam has a daughter. She is starting the school tomorrow."

    doc = utils.get_doc(test_sentence, False)

    assert doc._.has_coref
    assert isinstance(doc, Doc)


def test_get_doc_no_neuralcoref():
    test_sentence = "Sam has a daughter. She is starting the school tomorrow."

    doc = utils.get_doc(test_sentence, True)

    assert not doc._.has_coref
    assert isinstance(doc, Doc)


def test_get_actions_information_structure():
    test_sentence = "Sam has a daughter."

    doc = get_doc_example(test_sentence)

    info = utils.get_actions_information_structure(doc)

    assert isinstance(info, list)
    assert len(info) == 1


def test_check_question_true():
    test_sentence = "Has Sam a daughter?"

    doc = get_doc_example(test_sentence)
    is_question = utils.check_question(doc)

    assert is_question


def test_check_question_false():
    test_sentence = "Sam has a daughter."

    doc = get_doc_example(test_sentence)
    is_question = utils.check_question(doc)

    assert not is_question


def test_get_context_structure():

    structure = utils.get_context_structure()

    assert isinstance(structure, dict)
    assert len(structure.keys()) == 8
