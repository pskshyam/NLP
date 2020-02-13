import copy
import pandas as pd


def check_tuples(tuple_big, tuple_small):
    """Check if a tuple is contained in other tuple. Used to check indexes ranges of the sentences

    Parameters
    ----------
    tuple_big : tuple
        tuple that contains two integers

    tuple_small : tuple
        tuple that contains two integers

    Returns
    -------
        bool
            True if tuple_small contained or equal to tuple_big
            False if tuple_small bigger than tuple_big

    """
    if tuple_big[0] <= tuple_small[0]:
        if tuple_big[1] >= tuple_small[1]:
            return True
    return False


def contains(base, sub_list):
    """Check the elements of a list are contained in other

    Parameters
    ----------
    base : list, tuple or set

    sub_list :  list, tuple or set

    Returns
    -------
        bool
            True if sub_list elements are contained into base
            False if sub_list elements are not contained into base

    """

    return set(base) & set(sub_list) == set(sub_list)


def dict_contains(dct, keys):
    """Check if a list of keys are contained into a dict keys

    Parameters
    ----------
    dct : dict

    keys :  list, int or str

    Returns
    -------
        bool
            True if keys elements are contained into dct.keys()
            False if keys elements are not contained into dct.keys()

    """

    assert isinstance(dct, dict), "dict_contains: dct should be of type dict "
    assert type(keys) in [int, str, list], "dict_contains: keys should be of type list or string "
    if not type(keys) == list:
        keys = [keys]

    return contains(dct.keys(), keys)


def check_object_repeated(lists, obj):
    """Check if an attribute of a dictionary is is inside a tuple

    Parameters
    ----------
    lists : list

    obj :  dict

    Returns
    -------
        None if any attribute is inside the tuple
        dict with the input obj if no attribute is inside the tuple


    """
    for any_obj in lists:
        if check_tuples(any_obj['indexes'], obj['indexes']):
            return None
    return obj


def remove_extra_index(actions_structure, type_object):
    """Remove a key for each object found in a list

    Parameters
    ----------
    actions_structure : list
        list of lists with a dictionary inside the second level list

    type_object :  str

    """
    for i, action_dict in enumerate(actions_structure):
        for obj_dict in action_dict['context'][type_object]:
            obj_dict.pop('main_index')


def retokenize_object_final(actions_structure, obj_type, list_to_check):
    """Depending on the context part join different tokens (retokenize from spacy)

    Parameters
    ----------
    actions_structure : list
        list of dictionaries, each dictionary contains the information of an action

    obj_type :  str
        string with the context part type

    list_to_check :  list
        list of string with the part of speech names of the words that need to be retokenized

    """

    for i, action_dict in enumerate(actions_structure):
        obj_list = []
        doc = copy.copy(action_dict['doc'])
        for j in range(0, len(action_dict['doc'])):
            token = doc[j]
            if token.dep_ in list_to_check:
                if obj_type == 'action_subject' and (token.pos_ == 'DET' or token.text.lower() in ['what', 'who']) and not action_dict['question']:
                    obj = replace_relative_subject(token, action_dict)
                else:
                    span = doc[doc[j].left_edge.i: doc[j].right_edge.i + 1]
                    obj = {'initial_value': span.text,
                           'indexes': (doc[token.i].left_edge.i, doc[token.i].right_edge.i + 1),
                           'replacement_value': span.text, 'main_index': j}
                if obj_type == 'auxiliar_object':
                    obj = add_prep_to_auxiliar_object(doc, obj)

                if obj is not None:
                    obj_list.append(obj)
        actions_structure[i]['context'][obj_type] = obj_list


def add_prep_to_auxiliar_object(doc, aux_obj_dict):
    """Add the corresponding preposition to the auxiliar object in case there is one in the previous token.

    Parameters
    ----------
    doc : Spacy tokens doc
          An instance of spacy doc with an instance of spacy token for each word in the text

    aux_obj_dict :  dict
        dict with auxiliar objects information of an action

    Returns
    -------
        dict
            dict with auxiliar objects information of an action

    """

    if doc[aux_obj_dict['indexes'][0]-1].pos_ == 'ADP':
        aux_obj_dict['initial_value'] = doc[aux_obj_dict['indexes'][0]-1].text+' '+aux_obj_dict['initial_value']
        aux_obj_dict['replacement_value'] = doc[aux_obj_dict['indexes'][0]-1].text+' '+aux_obj_dict['replacement_value']
        aux_obj_dict['indexes'] = (aux_obj_dict['indexes'][0] - 1, aux_obj_dict['indexes'][1])
        aux_obj_dict['prep_added'] = True
    else:
        aux_obj_dict['prep_added'] = False
    return aux_obj_dict


def remove_repeated_components(action_structure, obj_type):
    """Remove components contained into other or with the same indexes

    Parameters
    ----------
    action_structure : list
        list of dictionaries, each dictionary contains the information of an action

    obj_type :  str
        string with the context part type

    """
    lists = []
    for i, action_dct in enumerate(action_structure):
        obj_list = []
        for obj_dict in action_dct['context'][obj_type]:
            if obj_type == 'direct_object':
                lists = action_dct['context']['indirect_object'] + action_dct['context']['agents']
            elif obj_type == 'auxiliar_object':
                lists = action_dct['context']['indirect_object'] + action_dct['context']['agents'] + \
                        action_dct['context']['direct_object'] + obj_list
            obj = check_object_repeated(lists, obj_dict)
            if obj:
                obj_list.append(obj)

        action_dct['context'][obj_type] = obj_list


def cut_objects(actions_structure, type_object):
    """Get the main verb index and uses it to cut other objects that are too long after retokenization

        Parameters
        ----------
        actions_structure : list
            list of dictionaries, each dictionary contains the information of an action

        type_object :  str
            string with the context part type

    """
    for i, action_dct in enumerate(actions_structure):
        doc = copy.copy(action_dct['doc'])
        for j, verb_dct in enumerate(action_dct['context']['verbs']):
            final_index_verb = verb_dct['indexes'][1]
            if j == range(len(action_dct['context']['verbs']))[-1]:
                init_index_next_verb = 100000000
            else:
                init_index_next_verb = action_dct['context']['verbs'][j + 1]['indexes'][0]
            for k, obj_dct in enumerate(action_dct['context'][type_object]):
                if obj_dct['indexes'][0] >= final_index_verb and obj_dct['indexes'][0] <= init_index_next_verb and obj_dct['indexes'][1] > init_index_next_verb:
                    cut_element(obj_dct, doc)


def cut_element(obj_dct, doc):
    """Set the new values and indexes for an object

        Parameters
        ----------
        obj_dct : dict
            dictionary contains the information of an action

        doc : Spacy tokens doc
            An instance of spacy doc with an instance of spacy token for each word in the text
    """
    index = obj_dct['main_index']
    obj_dct['initial_value'] = doc[doc[index].left_edge.i: index + 1].text
    obj_dct['replacement_value'] = doc[doc[index].left_edge.i: index + 1].text
    obj_dct['indexes'] = (doc[index].left_edge.i, index + 1)


def print_doc_tokens(doc):
    """Debug utility. Build a pandas dataframe with the text, part of speech and syntactic dependency relation
    for each token inside a spacy doc object

    Parameters
    ----------
    doc : Spacy tokens doc
          An instance of spacy doc with an instance of spacy token for each word in the text
    Returns
    -------
        pandas dataframe object
            dataframe with the text, part of speech and syntactic dependency relation for each token inside the doc

    """
    tokens = []
    for token in doc:
        tokens.append([token.text, token.pos_, token.dep_, token.tag_])

    df = pd.DataFrame(tokens, columns=["text", "part-of-speech", "syntactic_dependency_relation", "tag"])
    return df


def replace_relative_subject(token, action):
    """Replace subjects that are relatives pronouns by the corresponding subject

    Parameters
    ----------
    token : Spacy tokens object
          A spacy token of a word

    action : dict
          a dict with the information of an action

    Returns
    -------
    dict
        dict with the updated information of the subject

    """
    nearest_obj = get_nearest_component(action, {'initial_value': token.text, 'indexes': (token.i, token.i)})
    subject = {"original_subj_index": (token.i + action['action_range'][0],
                                       token.i + 1 + action['action_range'][0]),
               "indexes": (token.i, token.i + 1),
               "initial_value": token.text,
               "main_index": token.i
               }
    if nearest_obj:
        subject['replacement_value'] = nearest_obj['replacement_value']
    else:
        subject['replacement_value'] = token.text
    return subject


def get_nearest_component(action_dct, init_component):
    """Obtain the nearest component of a given component(init_component)

    Parameters
    ----------
    action_dct : dict
          a dict with the information of an action

    init_component : dict
          a dict with the information of a token

    Returns
    -------
    dict
        dict with the information of the nearest component of the given component

    """
    components = action_dct['context']['direct_object'] + action_dct['context']['direct_object'] + \
                 action_dct['context']['auxiliar_object'] + action_dct['context']['attributes']
    components.sort(key=lambda obj_dict: obj_dict['indexes'][1])
    nearest_comp = None
    for obj_dict in components:
        if obj_dict['indexes'][1] > init_component['indexes'][1]:
            break
        nearest_comp = obj_dict
    return nearest_comp


def replace_object(actions_structure, list_rep, type_object):
    """Replace a part of the action using the replacement list obtained previously if an action
     has a replacement in that list

    Parameters
    ----------
    actions_structure : list
        list of dictionaries, each dictionary contains the information of an action

    list_rep :  list
        list with all neuralcoref replacements of the whole text

    type_object :  str
        string with the context part type

    """
    for j, action_dict in enumerate(actions_structure):
        list_obj = action_dict['context'][type_object]
        if list_obj:
            for i, obj_dict in enumerate(list_obj):
                tuple_whole_text = (obj_dict['indexes'][0] + action_dict['action_range'][0],
                                    obj_dict['indexes'][1] + action_dict['action_range'][0])
                for replacement_dict in list_rep:
                    if check_tuples(tuple_whole_text, replacement_dict['initial_index']):
                        actions_structure[j]['context'][type_object][i]['replacement_value'] = list_obj[i]['replacement_value'].replace(replacement_dict['initial_value'],
                                                                          replacement_dict['replacement_value'])