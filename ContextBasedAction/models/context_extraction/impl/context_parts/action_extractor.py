import copy
from models.context_extraction.impl.context_parts.utils import get_nearest_component
from app.common.logger import set_up_logging
import mlconjug
import itertools
import pandas as pd
import pickle


class ActionExtractor:
    """This class is always the last element of the extractor pipeline, here we extract the actions
    inside each sentence and set the corresponding parts of the context previously extracted to each action
    """

    def __init__(self):

        self.logger = set_up_logging(__name__)

    def extract(self, text_information):
        """This method is present in all the steps of the pipeline that we will use to extract the context
        and is the first that is called to extract the corresponding part of the context

        Parameters
        ----------
        text_information : instance of text_information class
            contains all the information related to the text and its context
        """
        self.logger.info("************ Setting actions")

        self.context_by_action(text_information.actions_context_structure)
        self.logger.info("************ Setting actions done")

    def context_by_action(self, actions_structure):
        """Get the different actions inside each sentence and set the context to each action
            Parameters
            ----------
            actions_structure : list
                list of dictionaries with information about each sentence

        """
        verbs_alone, verbs_complex = get_not_action_verbs()
        for i, action_dct in enumerate(actions_structure):
            for j, verb_dct in enumerate(action_dct['context']['verbs']):

                if verb_dct['aux'] and len(actions_structure[i]['context_actions']) > 0:
                    actions_structure[i]['context_actions'][-1]['What is the action?']['initial_value'] += ' ' + verb_dct['initial_value']
                    actions_structure[i]['context_actions'][-1]['What is the action?'][
                        'replacement_value'] += ' ' + verb_dct['replacement_value']
                    #update_action_additional_info_auxiliar(actions_structure, i, verb_dct)
                else:
                    action, init_index_verb, final_index_verb = create_action(verb_dct)
                    init_index_next_verb = get_init_index_next_verb(j, action_dct)
                    action = add_element_to_action(action, action_dct, 'attributes', final_index_verb, init_index_next_verb, question='What is the action?')
                    action = add_element_to_action(action, action_dct, 'direct_object', final_index_verb, init_index_next_verb, question='What is the action?')
                    has_direct_object = True if len(action["What is the action?"]) > 0 else False
                    action = add_element_to_action(action, action_dct, 'indirect_object', final_index_verb, init_index_next_verb, question='Who is the action directed to?')
                    has_indirect_object = True if len(action["Who is the action directed to?"]) > 0 else False
                    action = add_element_to_action(action, action_dct, 'adverb_mod', final_index_verb, init_index_next_verb, question='How is the action made')

                    action = add_element_to_action(action, action_dct, 'auxiliar_object', final_index_verb, init_index_next_verb, question='What is the action?')

                    action = add_subject_to_action(action, verb_dct, action_dct, init_index_verb)

                    action = add_element_to_action(action, action_dct, 'agents', final_index_verb, init_index_next_verb, verb_dct=verb_dct)

                    action = check_element_order(action)
                    action = remove_extra_index_from_context_actions(action)

                    if verb_dct['initial_value'] not in verbs_alone:
                        initial_value = verb_dct['initial_value'] + ' ' + ' '.join(
                            [element['initial_value'] for element in action['What is the action?']]) \
                            if len([element['initial_value'] for element in action['What is the action?']]) > 0\
                            else verb_dct['initial_value']

                        replacement_value = verb_dct['replacement_value']+' '+' '.join(
                            [element['replacement_value'] for element in action['What is the action?']]) \
                            if len([element['replacement_value'] for element in action['What is the action?']]) > 0\
                            else verb_dct['replacement_value']

                        action['What is the action?'] = {'initial_value': initial_value,
                                                         'replacement_value': replacement_value}
                        actions_structure[i]['context_actions'].append(action)

                        # TODO Model loaded from local, improve model
                        #action_info = get_action_additional_info(action_dct, verb_dct, action, has_direct_object,
                        #                                     has_indirect_object, init_index_verb, final_index_verb)

                        #action["action_info"] = action_info
                        #is_main_action = predict_main_action(action)
                        #action["is_main_action"] = is_main_action

            for pobj_dct in action_dct['context']['auxiliar_object']:
                pobj_dct.pop('prep_added')
            actions_structure[i].pop('doc')
            #for act in actions_structure[i]["context_actions"]:
            #    act.pop("action_info")
        #is_main_action = predict_main_action(actions_structure)


def predict_main_action(action):

    action_replacement_text = get_action_replacement_text(action)
    print("ACTION PREDICT")
    print(action)
    action['action_info']["action_text"] = action_replacement_text
    data_df = pd.DataFrame([action['action_info']])
    print("DATAFRAME PREDICT")
    print(data_df)
    model = get_model_pipeline()
    prediction = model.predict(data_df)
    print(prediction)
    return prediction[0]


def get_model_pipeline():
    with open("/home/alvaro/Escritorio/action_model/pipeline_model.pkl", "rb") as f:
        model_pipeline = pickle.load(f)
        return model_pipeline


def get_action_replacement_text(action):
    action_text = ""
    if action["Who is making the action"] and 'replacement_value' in action["Who is making the action"][0]:
        action_text += " " + action["Who is making the action"][0]["replacement_value"]
    if action["What is the action?"] and 'replacement_value' in action["What is the action?"]:
        action_text += " " + action["What is the action?"]["replacement_value"]
    if action["Who is the action directed to?"] and 'replacement_value' in action["Who is the action directed to?"][0]:
        action_text += " " + action["Who is the action directed to?"][0]["replacement_value"]
    if action["How is the action made"] and 'replacement_value' in action["How is the action made"][0]:
        action_text += " " + action["How is the action made"][0]["replacement_value"]
    return action_text


"""
def predict_main_action(actions_structure):
    #DELETE WHEN MODEL IS TRAINED
    action_info_list = []
    for action in actions_structure:
        action_info_list.extend(action["context_actions"])
    import json
    file_path = "/home/alvaro/Escritorio/action_model/data_attr.txt"
    with open(file_path, 'a') as outfile:
            json.dum<p(action_info_list, outfile)
    return True
"""


def get_action_additional_info(action_dct, verb_dct, action, has_direct_object, has_indirect_object, init_index_verb, final_index_verb):
    """Obtain additional information about the action
            Parameters
            ----------
            verb_dct : dct optional
                dict with verb information to handle passive sentences
            action : dict
                dictionary with the action information
            action_dct : dict
                dict with the current information about the context of the action
            Returns
            -------
            dict
                dict with additional information about the action
    """
    print("ACTION")
    print(action)
    has_replacements = False if action['What is the action?']['initial_value'] == \
                               action['What is the action?']['replacement_value'] else True
    additional_info = {
                       "tokens_len": action_dct["action_range"][1] - action_dct["action_range"][0],
                       "sentence_len_start": action_dct["action_range"][0],
                       "sentence_len_end": action_dct["action_range"][1],
                       "number_of_verbs": len(verb_dct["replacement_value"].split(" ")),
                       "has_replacements":  has_replacements,
                       "direct_object": has_direct_object,
                       "indirect_object": has_indirect_object,
                       "init_index_verb": init_index_verb,
                       "final_index_verb": final_index_verb,
                       "auxiliar_verb": False
                       }

    return additional_info


def update_action_additional_info_auxiliar(actions_structure, i, verb_dct):
    """Update the action information if an auxiliar verb is found
        Parameters
        ----------
        verb_dct : dct optional
            dict with verb information to handle passive sentences
        i : int
            action index
        actions_structure : list
            list of dictionaries with information of the actions
    """
    current_number_of_verbs = actions_structure[i]['context_actions'][-1]["action_info"]["number_of_verbs"]
    has_replacements = False if actions_structure[i]['context_actions'][-1]['What is the action?']['initial_value'] == \
                                actions_structure[i]['context_actions'][-1]['What is the action?'][
                                    'replacement_value'] else True

    actions_structure[i]['context_actions'][-1]["action_info"]["number_of_verbs"] = \
        current_number_of_verbs + len(verb_dct["replacement_value"].split(" "))
    actions_structure[i]['context_actions'][-1]["action_info"]["auxiliar_verb"] = True
    actions_structure[i]['context_actions'][-1]["action_info"]["has_replacements"] = has_replacements


def get_not_action_verbs():
    """
    return verbs that we will not consider actions
    :return: two list
    """
    verbs_alone = ['be', 'have']
    verb_complex = ["say", "believe", "suggest", "think", "get", "seem", "contain" ]
    verbs_alone = get_verb_conjug(verbs_alone)+["'s"]
    verb_complex = get_verb_conjug(verb_complex)
    return verbs_alone, verb_complex


def get_verb_conjug(verb_list):
    """
    it conjugates te list of verbs that it receives as input
    :param verb_list: list
        list of verbs that we want to conjugate
    :return: list that contains all conjugations of the input verbs
    """
    verbs = []
    for verb in verb_list:
        default_conjugator = mlconjug.Conjugator(language='en')
        test_verb = default_conjugator.conjugate(verb)
        all_conjugated_forms = test_verb.iterate()
        verbs.append(list(set([verb_tuple[-1] for verb_tuple in all_conjugated_forms])))
    verbs = list(itertools.chain.from_iterable(verbs))
    return verbs


def remove_prep_from_obj(objt):
    """Remove the initial preposition in agents components
        Parameters
        ----------
        obj : str
            string with the agent component text
        Returns
        -------
        str : input string without the initial preposition
    """
    objt['initial_value'] = " ".join(objt['initial_value'].split(" ")[1:])
    objt['replacement_value'] = " ".join(objt['replacement_value'].split(" ")[1:])
    return objt


def add_element_to_action(context_action_dict, sent_full_dict, type_object, final_index_current_verb, init_index_next_verb, verb_dct=None, question=None):
    """Add the context element to the action information if the context element is contained into the action range
        Parameters
        ----------
        context_action_dict : dict
            dict with the current information about the context of the action
        sent_full_dict : dict
            dict with the entire information about the sentence
        type_object : str
            context part type
        final_index_current_verb : int
        init_index_next_verb : int
        verb_dct : dct optional
            dict with verb information to handle passive sentences
        question : str optional
            string with the question about the context that will be answered by the context element
    """
    for obj_dct in sent_full_dict['context'][type_object]:
        if final_index_current_verb <= obj_dct['indexes'][0] <= init_index_next_verb:
            if type_object == 'agents':
                handling_agent_componentes(context_action_dict, sent_full_dict,  verb_dct, obj_dct)
            else:
                context_action_dict[question].append(copy.copy(obj_dct))
    return context_action_dict


def handling_agent_componentes(context_action_dict, sent_full_dict, verb_dct, agent_obj):
    """Append agent object as direct object to the context information in case no direct object in sentence
        Parameters
        ----------
        context_action_dict : dict
            dict with the current information about the context of the action
        sent_full_dict : dict
            with the entire information about the sentence
        verb_dct : dct optional
            dict with verb information to handle passive sentences
        agent_obj : str
            string with the agent obj of the sentence
        Returns
        -------
            dict : dict with information about the action context
    """
    obj_dct = remove_prep_from_obj(agent_obj)
    if verb_dct['active']:
        direct_obj = get_nearest_component(sent_full_dict, agent_obj)
        if direct_obj is not None and direct_obj not in context_action_dict['What is the action?']:
            if 'prep_added' in direct_obj.keys():
                direct_obj = remove_prep_from_obj(direct_obj)
            context_action_dict['What is the action?'].append(copy.copy(direct_obj))
    context_action_dict['Who is making the action'] = [copy.copy(obj_dct)]
    return context_action_dict


def create_action(verb_dct):
    """Creates the structure of the dictionary that will contain the action context
        Parameters
        ----------
        verb_dct : dict
            dict with verb context information
        Returns
        -------
        action : dict
            dictionary with the action information
        final_index_current_verb : int
        init_index_next_verb : int
    """
    action = {'What is the action?': [],
              'Who is the action directed to?': [],
              'Who is making the action': [],
              'How is the action made': []
              }
    final_index_verb = verb_dct['indexes'][1]
    init_index_verb = verb_dct['indexes'][0]

    return action, init_index_verb, final_index_verb


def get_init_index_next_verb(index_current_verb, action_full_dct):
    """Get the initial index of the next verb on the action
        Parameters
        ----------
        index_current_verb : int
        action_full_dct : dict
            dict with the entire information about the action
        Returns
        -------
        int : next verb initial index
    """
    init_index_next_verb = 100000000
    if index_current_verb != len(action_full_dct['context']['verbs'])-1:
        for i in range(index_current_verb+1, len(action_full_dct['context']['verbs'])):
            if not action_full_dct['context']['verbs'][i]['aux']:
                init_index_next_verb = action_full_dct['context']['verbs'][index_current_verb + 1]['indexes'][0]
                break
    return init_index_next_verb


def check_element_order(context_action_dict):
    """Sort the elements of the action if it is a question
        Parameters
        ----------
        context_action_dict : dict
            dict with the current information about the context of the action
        Returns
        -------
        dict
            dict with the current information about the context of the action
    """
    for question in context_action_dict:
        elements = context_action_dict[question]
        context_action_dict[question] = sorted(elements, key=lambda x: x['indexes'][0])
    return context_action_dict


def remove_extra_index_from_context_actions(context_action_dict):
    """Remove all the useless indexes in the action context dict
        Parameters
        ----------
        context_action_dict : dict
            dict with the current information about the context of the action
        Returns
        -------
        dict : dict with the current information about the context of the action
    """
    keys_to_keep = {'initial_value', 'replacement_value'}
    for question in context_action_dict:
        for obj_dct in context_action_dict[question]:
            total_keys = set(obj_dct.keys())
            keys_to_remove = total_keys - keys_to_keep
            for key in keys_to_remove:
                obj_dct.pop(key)
    return context_action_dict


def add_subject_to_action(action, verb_dct, action_full_dct, index_current_verb):
    """Add the subject to the action depending on active or passive action
        Parameters
        ----------
        action : dict
            dictionary with the action information
        verb_dct : dict
            dict with verb context information
        action_full_dct : dict
            dict with the entire information about the action
        index_current_verb : int
        Returns
        -------
        dict : dictionary with the action information
    """
    subj_selected, subj_index, = select_subject(action_full_dct, index_current_verb)
    if verb_dct['active']:
        if subj_index != -1:
            action['Who is making the action'].append(copy.copy(subj_selected))
    elif not verb_dct['active'] and subj_index != -1:
        replace_personal_pronoun_passive(subj_selected)
        action['What is the action?'].append(copy.copy(subj_selected))
    return action


def replace_personal_pronoun_passive(subj_dict):
    """
    Replace the subjective personal pronouns by its corresponding
    objective personal pronouns  in case of passive voice sentences, because in that cases
    we will set the subject as an object.
    :param subj_dict: dict
        dictionary which contains the initial and replacement value for the selected subject
    :return: dict
         dictionary which contains the initial and replacement value for the selected subject.
         The dictionary will be muted if it is required
    """
    pron_replacements = [{'initial_value': 'i', 'replacement_value': 'me'},
    {'initial_value': 'he', 'replacement_value': 'him'},
    {'initial_value': 'she', 'replacement_value': 'her'},
    {'initial_value': 'we', 'replacement_value': 'us'},
    {'initial_value': 'their', 'replacement_value': 'them'}]

    if subj_dict['initial_value'].lower() in [pron_dict['initial_value'] for pron_dict in pron_replacements]:
        index = [pron_dict['initial_value'] for pron_dict in pron_replacements].index(subj_dict['initial_value'].lower())
        if subj_dict['initial_value'].lower() == subj_dict['replacement_value']:
            subj_dict['replacement_value'] = pron_replacements[index]['replacement_value']
        subj_dict['initial_value'] = pron_replacements[index]['replacement_value']

    return subj_dict


def select_subject(action_full_dct, index_current_verb):
    """Get the action subject
        Parameters
        ----------
        action_full_dct : dict
            dict with the entire information about the action
        index_current_verb : int

        Returns
        -------
        subj_selected
            dict if a subject is found returns dict with the information of the subject
            none if no subject is found
        subj_index
            int if a subject is found returns the corresponding subject index
            -1 if no subject is found
    """
    subj_index = -1
    subj_selected = None
    for k, subject in enumerate(action_full_dct['context']['action_subject']):
        if subject['indexes'][1] <= index_current_verb:
            subj_index = k
            subj_selected = subject
        else:
            break
    return subj_selected, subj_index
