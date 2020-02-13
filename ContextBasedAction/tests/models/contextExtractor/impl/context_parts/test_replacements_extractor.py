import spacy
from models.context_extraction.impl.context_parts import replacements_extractor
import neuralcoref


def get_doc_example(text):
    nlp = spacy.load("en_core_web_sm")
    neuralcoref.add_to_pipe(nlp)
    doc = nlp(text)
    return doc


def test_get_all_replacements():
    doc = get_doc_example("Sam has a daughter. She is starting the school tomorrow.")

    replacement_list_return = replacements_extractor.get_all_replacements(doc)

    assert isinstance(replacement_list_return, list)
    assert replacement_list_return[0]["initial_index"] == (5, 6)


def test_get_initial_replacement():

    doc = get_doc_example("Sam has a daughter. She is starting the school tomorrow.")

    replacement_list_return = replacements_extractor.get_initial_replacement(doc)

    assert isinstance(replacement_list_return, list)
    assert replacement_list_return[0]["initial_index"] == (5, 6)


def test_check_replacements():

    replacements_list = [{'replacement_value': 'Sam', 'initial_value': 'his',
                          'replacement_main_token': get_doc_example("Sam"),
                          'initial_index': (2, 3)}, {'replacement_value': 'his mother', 'initial_value': 'She',
                                                     'replacement_main_token': get_doc_example("his mother"),
                                                     'initial_index': (6, 7)}]

    replacements_list_initial_replacement = replacements_list[1]['replacement_value']

    replacements_extractor.check_replacements(replacements_list)

    assert replacements_list[1]['replacement_value'] != replacements_list_initial_replacement


def test_remove_pronouns_replacements():

    replacements_list = [{
        'initial_value': 'she',
        'initial_main_token': get_doc_example("she"),
        'replacement_value': 'her',
        'replacement_main_token': get_doc_example("her"),
        'initial_index': (5, 6)}]

    replacements_extractor.remove_pronouns_replacements(replacements_list)

    assert len(replacements_list) == 0