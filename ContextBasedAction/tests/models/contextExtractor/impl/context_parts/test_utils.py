from models.context_extraction.impl.context_parts import utils
from unittest.mock import patch
import spacy
import pandas


def get_doc_example(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return doc


def test_check_tuples_true():

    check_tuple_return = utils.check_tuples((1, 10), (3, 4))
    assert check_tuple_return


def test_check_tuples_false():

    check_tuple_return = utils.check_tuples((1, 10), (30, 40))
    assert not check_tuple_return


def test_contains_true():
    base_test = "test"
    sub_list_test = "t"
    contains_return = utils.contains(base_test, sub_list_test)
    assert contains_return


def test_contains_false():
    base_test = "test"
    sub_list_test = "a"
    contains_return = utils.contains(base_test, sub_list_test)
    assert not contains_return


def test_dict_contains_not_dict():
    try:
        utils.dict_contains([], [])
    except AssertionError as exc:
        assert str(exc) == "dict_contains: dct should be of type dict "


def test_dict_contains_not_types_keys():
    try:
        utils.dict_contains({}, 1.2)
    except AssertionError as exc:
        assert str(exc) == "dict_contains: keys should be of type list or string "


@patch('models.context_extraction.impl.context_parts.utils.contains')
def test_dict_contains_contains_call(mocker):

    dct_contains = {'test_key': 'test_value'}
    keys_list_dct_contains = ['test_key']
    utils.dict_contains(dct_contains, keys_list_dct_contains)

    mocker.assert_called_once_with(dct_contains.keys(), keys_list_dct_contains)


def test_check_object_repeated_true(mocker):

    dict_list = [{"indexes": (1, 10)}]

    obj = {"indexes": (3, 4)}

    mocker.patch.object(utils, 'check_tuples', return_value=True)
    check_repeated_return = utils.check_object_repeated(dict_list, obj)

    assert not isinstance(check_repeated_return, dict)


def test_check_object_repeated_false(mocker):

    dict_list = [{"indexes": (1, 10)}]

    obj = {"indexes": (3, 4)}

    mocker.patch.object(utils, 'check_tuples', return_value=False)
    check_repeated_return = utils.check_object_repeated(dict_list, obj)

    assert isinstance(check_repeated_return, dict)


def test_remove_extra_index():

    test_dict = [{"context": {"type_object": [{'main_index': 1}]}}]

    assert "main_index" in test_dict[0]["context"]["type_object"][0].keys()
    utils.remove_extra_index(test_dict, "type_object")

    assert not "main_index" in test_dict[0]["context"]["type_object"][0].keys()

def test_retokenize_object_final_auxiliar(mocker):
    action_structure = [{'doc': get_doc_example('I will go to the cinema tomorrow.'),
                         'action_range': (0, 8), 'action_text': 'I will go to the cinema tomorrow.',
                         'context': {}, 'context_actions': [], 'question': False}]

    obj_dct = {'initial_value': 'the cinema', 'indexes': (4, 6), 'replacement_value': 'the cinema', 'main_index': 5}
    type_obj = 'auxiliar_object'
    mocker.patch.object(utils, 'replace_relative_subject', return_value=obj_dct)
    mocker.patch.object(utils, 'add_prep_to_auxiliar_object', return_value=obj_dct)
    utils.retokenize_object_final(action_structure, type_obj, ['pobj'])
    assert utils.replace_relative_subject.call_count == 0
    assert utils.add_prep_to_auxiliar_object.call_count == 1
    assert len(action_structure[0]['context'][type_obj]) > 0

def test_retokenize_object_final_auxiliar_none(mocker):
    action_structure = [{'doc':get_doc_example('I will go to the cinema tomorrow.'),
                         'action_range': (0, 8), 'action_text': 'I will go to the cinema tomorrow.',
                         'context': {}, 'context_actions': [], 'question': False}]
    type_obj = 'auxiliar_object'
    mocker.patch.object(utils, 'replace_relative_subject', return_value=None)
    mocker.patch.object(utils, 'add_prep_to_auxiliar_object', return_value=None)
    utils.retokenize_object_final(action_structure, type_obj, ['pobj'])
    assert utils.replace_relative_subject.call_count == 0
    assert utils.add_prep_to_auxiliar_object.call_count == 1
    assert len(action_structure[0]['context'][type_obj]) == 0

def test_retokenize_object_final(mocker):
    action_structure = [{'doc':get_doc_example('I will go to the cinema tomorrow.'),
                         'action_range': (0, 8), 'action_text': 'I will go to the cinema tomorrow.',
                         'context': {}, 'context_actions': [], 'question': False}]
    obj_dct = {'initial_value': 'I', 'indexes': (0, 1), 'replacement_value': 'I', 'main_index': 0}
    type_obj = 'action_subject'
    mocker.patch.object(utils, 'replace_relative_subject', return_value=obj_dct)
    mocker.patch.object(utils, 'add_prep_to_auxiliar_object', return_value=obj_dct)
    utils.retokenize_object_final(action_structure, type_obj, ['nsubj','nsubjpass'])
    assert utils.replace_relative_subject.call_count == 0
    assert utils.add_prep_to_auxiliar_object.call_count == 0
    assert len(action_structure[0]['context'][type_obj]) > 0


def test_retokenize_object_final_relative(mocker):
    action_structure = [{'doc': get_doc_example("The current model is able to extract actions from afirmative sentences which doesn't contain relative pronouns."),
                         'action_range': (0, 8), 'action_text': "The current model is able to extract actions from afirmative sentences which doesn't contain relative pronouns.",
                         'context': {}, 'context_actions': [], 'question': False}]

    obj_dct = {'initial_value': 'which', 'indexes': (4, 6), 'replacement_value': 'afirmative sentences', 'main_index': 5}
    type_obj = 'action_subject'
    mocker.patch.object(utils, 'replace_relative_subject', return_value=obj_dct)
    mocker.patch.object(utils, 'add_prep_to_auxiliar_object', return_value=None)
    utils.retokenize_object_final(action_structure, type_obj, ['nsubj', 'nsubjpass'])
    assert utils.replace_relative_subject.call_count == 1
    assert utils.add_prep_to_auxiliar_object.call_count == 0
    assert len(action_structure[0]['context'][type_obj]) == 2


def test_retokenize_object_final_subject_none_relative(mocker):
    action_structure = [{'doc': get_doc_example("The current model is able to extract actions from afirmative sentences which doesn't contain relative pronouns."),
                         'action_range': (0, 8), 'action_text': "The current model is able to extract actions from afirmative sentences which doesn't contain relative pronouns.",
                         'context': {}, 'context_actions': [], 'question': False}]
    type_obj = 'action_subject'
    mocker.patch.object(utils, 'replace_relative_subject', return_value=None)
    mocker.patch.object(utils, 'add_prep_to_auxiliar_object', return_value=None)
    utils.retokenize_object_final(action_structure, type_obj, ['nsubj', 'nsubjpass'])
    assert utils.replace_relative_subject.call_count == 1
    assert utils.add_prep_to_auxiliar_object.call_count == 0
    assert len(action_structure[0]['context'][type_obj]) == 1

def test__prep_to_auxiliar_object_true():
    aux_obj_dict = {'initial_value': 'the cinema', 'indexes': (4, 6), 'main_index': 5, 'replacement_value': 'the cinema'}
    doc = get_doc_example("I will go to the cinema")

    aux_obj_dict_return = utils.add_prep_to_auxiliar_object(doc, aux_obj_dict)

    assert aux_obj_dict_return['prep_added']


def test__prep_to_auxiliar_object_false():
    aux_obj_dict = {'initial_value': 'the cinema', 'indexes': (4, 6), 'main_index': 5, 'replacement_value': 'the cinema'}
    doc = get_doc_example("I will visit you tomorrow")

    aux_obj_dict_return = utils.add_prep_to_auxiliar_object(doc, aux_obj_dict)

    assert not aux_obj_dict_return['prep_added']


def test_remove_repeated_components(mocker):

    action_structure = [{"context" : {"objtype" : [{"action1": "action1_value"},
                                                   {"action2": "action2_value"}]}}]
    mocker.patch.object(utils, "check_object_repeated")

    utils.remove_repeated_components(action_structure, "objtype")

    assert utils.check_object_repeated.call_count == 2


def test_cut_objects(mocker):

    action = [{'context': {'verbs': [{'indexes': (1, 2)}, {'indexes': (5, 6)}]},
               'doc': 'This is a sentence which contains words'}]

    mocker.patch.object(utils, "cut_element")

    utils.cut_objects(action, 'verbs')

    assert utils.cut_element.call_count == 1

def test_cut_element(mocker):
    doc = get_doc_example("The current model is able to extract actions from afirmative sentences which doesn't contain relative pronouns.")
    obj_dict = {'initial_value': "from afirmative sentences which does n't contain relative pronouns", 'indexes': (8, 17),
     'replacement_value': "from afirmative sentences which does n't contain relative pronouns", 'main_index': 10,
     'prep_added': True}
    utils.cut_element(obj_dict, doc)
    assert  dict_contains(obj_dict, ['main_index','initial_value', 'replacement_value', 'indexes'])

def contains(base, sub_list):
    return set(base) & set(sub_list) == set(sub_list)


def dict_contains(dct, keys):
    assert isinstance(dct, dict), "dict_contains: dct should be of type dict "
    assert type(keys) in [int, str, list], "dict_contains: keys should be of type list or string "
    if not type(keys) == list:
        keys = [keys]

    return contains(dct.keys(), keys)


def test_print_doc_tokens(mocker):

    df = mocker.patch.object(pandas, "DataFrame", return_value=pandas.DataFrame())

    doc = get_doc_example("test text.")

    utils.print_doc_tokens(doc)

    assert pandas.DataFrame.call_count == 1
    assert isinstance(df, type(pandas.DataFrame))


def test_replace_relative_subject_nearest_true(mocker):

    nearest_object = {'replacement_value': 'a sentence'}

    mocker.patch.object(utils, "get_nearest_component", return_value=nearest_object)

    action = {'action_range': (0, 8)}
    token = get_doc_example("which")[0]

    subject_return = utils.replace_relative_subject(token, action)

    assert utils.get_nearest_component.call_count == 1
    assert subject_return['replacement_value'] == nearest_object['replacement_value']


def test_replace_relative_subject_nearest_false(mocker):

    mocker.patch.object(utils, "get_nearest_component", return_value=None)

    action = {'action_range': (0, 8)}
    token = get_doc_example("which")[0]

    subject_return = utils.replace_relative_subject(token, action)

    assert utils.get_nearest_component.call_count == 1
    assert subject_return['replacement_value'] == token.text

