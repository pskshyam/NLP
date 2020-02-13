from models.context_extraction.impl.context_parts.action_extractor import ActionExtractor
from models.context_extraction.impl.context_parts import action_extractor
from models.context_extraction import context_extractor
import mlconjug
import copy


def test_extract(mocker):
    agents_extractor_instance = ActionExtractor()
    mocker.patch.object(ActionExtractor, "context_by_action")
    text_information = mocker.patch.object(context_extractor, 'TextInformation')

    agents_extractor_instance.extract(text_information)

    assert ActionExtractor.context_by_action.call_count == 1


def test_get_not_action_verbs(mocker):
    mocker.patch.object(action_extractor, "get_verb_conjug")
    action_extractor.get_not_action_verbs()
    assert action_extractor.get_verb_conjug.call_count == 2


def test_get_verb_conjug(mocker):
    verb = "be"
    conjug = mlconjug.Conjugator(language="en")
    conjug_verb = conjug.conjugate(verb)
    mocker.patch.object(mlconjug.Conjugator, "conjugate", return_value=conjug_verb)
    mocker.patch.object(mlconjug.PyVerbiste.VerbEn, 'iterate', return_value=[(verb, verb)])
    list_conjugs = action_extractor.get_verb_conjug([verb])

    assert mlconjug.Conjugator.conjugate.call_count == 1
    assert mlconjug.PyVerbiste.VerbEn.iterate.call_count == 1
    assert list_conjugs == [verb]


def contains(base, sub_list):
    return set(base) & set(sub_list) == set(sub_list)


def dict_contains(dct, keys):
    assert isinstance(dct, dict), "dict_contains: dct should be of type dict "
    assert type(keys) in [int, str, list], "dict_contains: keys should be of type list or string "
    if not type(keys) == list:
        keys = [keys]

    return contains(dct.keys(), keys)


def test_remove_prep_from_obj():
    obj_dict = {
        "initial_value":"prep initial value",
        "replacement_value":"prep replacement value"
    }
    ret_dict = action_extractor.remove_prep_from_obj(obj_dict)
    assert dict_contains(ret_dict, ["initial_value", "replacement_value"])


def test_add_element_to_action_agents_false_add(mocker):
    action = {'What is the action?': [],
              'Who is the action directed to?': [],
              'Who is making the action': [],
              'How is the action made': []
              }
    type_obj = "direct_object"
    final_index_current_verb = 1
    init_index_next_verb = 2
    sentence_dict= {
        "action_text": "Sam visited his mun yesterday to give her a present.",
        "context": {"direct_object": [{"initial_value": "his mun","indexes": [2,4],"replacement_value": "Sam mun"}]}}
    action = action_extractor.add_element_to_action(
        context_action_dict=action,
        sent_full_dict=sentence_dict,
        type_object=type_obj,
        final_index_current_verb=final_index_current_verb,
        init_index_next_verb=init_index_next_verb,
        question="What is the action?")
    for key in action:
        if key == "What is the action?":
            assert len(action[key]) == 1
        else:
            assert len(action[key]) == 0


def test_add_element_to_action_agents_false_not_add():
    action = {'What is the action?': [],
              'Who is the action directed to?': [],
              'Who is making the action': [],
              'How is the action made': []
              }
    type_obj = "direct_object"
    final_index_current_verb = 6
    init_index_next_verb = 8
    sentence_dict = {"action_text": "Sam visited his mun yesterday to give her a present.",
        "context": {"direct_object": [{"initial_value": "his mun", "indexes": [2, 4], "replacement_value": "Sam mun"}]}}

    action = action_extractor.add_element_to_action(
        context_action_dict=action,
        sent_full_dict=sentence_dict,
        type_object=type_obj,
        final_index_current_verb=final_index_current_verb,
        init_index_next_verb=init_index_next_verb,
        question="What is the action?")

    for key in action:
        assert len(action[key]) == 0


def test_add_element_to_action_agents_true_not_add(mocker):
    action = {'What is the action?': [],
              'Who is the action directed to?': [],
              'Who is making the action': [],
              'How is the action made': []
              }
    type_obj = "agents"
    final_index_current_verb = 6
    init_index_next_verb = 8
    sentence_dict = {"action_text": "Sam visited his mun yesterday to give her a present.",
                     "context": {"agents": [
                         {"initial_value": "his mun", "indexes": [2, 4], "replacement_value": "Sam mun"}]}}
    verb = {"initial_value": "painted","indexes": [3,5],"replacement_value": "painted","aux": False,"active": False}
    mocker.patch.object(action_extractor, "handling_agent_componentes")

    action_extractor.add_element_to_action(
        context_action_dict=action,
        sent_full_dict=sentence_dict,
        type_object=type_obj,
        final_index_current_verb=final_index_current_verb,
        init_index_next_verb=init_index_next_verb,
        verb_dct=verb)
    assert action_extractor.handling_agent_componentes.call_count == 0


def test_add_element_to_action_agents_true(mocker):
    action = {'What is the action?': [],
              'Who is the action directed to?': [],
              'Who is making the action': [],
              'How is the action made': []
              }
    type_obj = "agents"
    final_index_current_verb = 0
    init_index_next_verb = 1
    sentence_dict = {"action_text": "Sam visited his mun yesterday to give her a present.",
                     "context": {"agents": [
                         {"initial_value": "his mun", "indexes": [2, 4], "replacement_value": "Sam mun"}]}}
    verb = {"initial_value": "painted","indexes": [3,5],"replacement_value": "painted","aux": False,"active": False}
    mocker.patch.object(action_extractor, "handling_agent_componentes")

    action_extractor.add_element_to_action(
        context_action_dict=action,
        sent_full_dict=sentence_dict,
        type_object=type_obj,
        final_index_current_verb=final_index_current_verb,
        init_index_next_verb=init_index_next_verb,
        verb_dct=verb)
    assert action_extractor.handling_agent_componentes.call_count == 0


def test_handling_agent_componentes_active_false(mocker):
        action = {'What is the action?': [],
                  'Who is the action directed to?': [],
                  'Who is making the action': [],
                  'How is the action made': []
                  }
        sentence_dict = {"action_text": "Sam visited his mun yesterday to give her a present.",
                         "context": {"agents": [
                             {"initial_value": "his mun", "indexes": [2, 4], "replacement_value": "Sam mun"}]}}
        verb = {"initial_value": "painted", "indexes": [3, 5], "replacement_value": "painted", "aux": False,
                "active": False}
        mocker.patch.object(action_extractor, "remove_prep_from_obj")
        action_extractor.handling_agent_componentes(
            context_action_dict=action,
            sent_full_dict=sentence_dict,
            verb_dct=verb,
            agent_obj=sentence_dict["context"]["agents"][0]

        )
        assert action_extractor.remove_prep_from_obj.call_count == 1
        for key in action:
            if key == "Who is making the action":
                assert len(action[key]) == 1
            else:
                assert len(action[key]) == 0


def test_handling_agent_componentes_active_true_prep_added(mocker):
    action = {'What is the action?': [],
              'Who is the action directed to?': [],
              'Who is making the action': [],
              'How is the action made': []
              }
    sentence_dict = {"action_text": "Sam visited his mun yesterday to give her a present.",
                     "context": {"agents": [
                         {"initial_value": "his mun", "indexes": [2, 4], "replacement_value": "Sam mun"}]}}
    verb = {"initial_value": "painted", "indexes": [3, 5], "replacement_value": "painted", "aux": False,
            "active": True}
    direct_obj = {"initial_value": "his mun", "indexes": [2, 4], "replacement_value": "Sam mun", "prep_added":True}
    mocker.patch.object(action_extractor, "remove_prep_from_obj", return_value=direct_obj)
    mocker.patch.object(action_extractor, "get_nearest_component", return_value=direct_obj)
    action_extractor.handling_agent_componentes(
        context_action_dict=action,
        sent_full_dict=sentence_dict,
        verb_dct=verb,
        agent_obj=sentence_dict["context"]["agents"][0]

    )
    assert action_extractor.remove_prep_from_obj.call_count == 2
    assert action_extractor.get_nearest_component.call_count == 1
    for key in action:
        if key == "Who is making the action" or key=='What is the action?':
            assert len(action[key]) == 1
        else:
            assert len(action[key]) == 0


def test_handling_agent_componentes_active_true_not_prep_added(mocker):
    action = {'What is the action?': [],
              'Who is the action directed to?': [],
              'Who is making the action': [],
              'How is the action made': []
              }
    sentence_dict = {"action_text": "Sam visited his mun yesterday to give her a present.",
                     "context": {"agents": [
                         {"initial_value": "his mun", "indexes": [2, 4], "replacement_value": "Sam mun"}]}}
    verb = {"initial_value": "painted", "indexes": [3, 5], "replacement_value": "painted", "aux": False,
            "active": True}
    direct_obj = {"initial_value": "his mun", "indexes": [2, 4], "replacement_value": "Sam mun"}
    mocker.patch.object(action_extractor, "remove_prep_from_obj", return_value=direct_obj)
    mocker.patch.object(action_extractor, "get_nearest_component", return_value=direct_obj)
    action_extractor.handling_agent_componentes(
        context_action_dict=action,
        sent_full_dict=sentence_dict,
        verb_dct=verb,
        agent_obj=sentence_dict["context"]["agents"][0]

    )
    assert action_extractor.remove_prep_from_obj.call_count == 1
    assert action_extractor.get_nearest_component.call_count == 1
    for key in action:
        if key == "Who is making the action" or key=='What is the action?':
            assert len(action[key]) == 1
        else:
            assert len(action[key]) == 0


def test_handling_agent_componentes_active_true_none(mocker):
    action = {'What is the action?': [],
              'Who is the action directed to?': [],
              'Who is making the action': [],
              'How is the action made': []
              }
    sentence_dict = {"action_text": "Sam visited his mun yesterday to give her a present.",
                     "context": {"agents": [
                         {"initial_value": "his mun", "indexes": [2, 4], "replacement_value": "Sam mun"}]}}
    verb = {"initial_value": "painted", "indexes": [3, 5], "replacement_value": "painted", "aux": False,
            "active": True}
    direct_obj = {"initial_value": "his mun", "indexes": [2, 4], "replacement_value": "Sam mun", "prep_added":True}
    mocker.patch.object(action_extractor, "remove_prep_from_obj", return_value=direct_obj)
    mocker.patch.object(action_extractor, "get_nearest_component", return_value=None)
    action_extractor.handling_agent_componentes(
        context_action_dict=action,
        sent_full_dict=sentence_dict,
        verb_dct=verb,
        agent_obj=sentence_dict["context"]["agents"][0]

    )
    assert action_extractor.remove_prep_from_obj.call_count == 1
    assert action_extractor.get_nearest_component.call_count == 1
    for key in action:
        if key == "Who is making the action":
            assert len(action[key]) == 1
        else:
            assert len(action[key]) == 0


def test_handling_agent_componentes_active_true_already_what(mocker):

    sentence_dict = {"action_text": "Sam visited his mun yesterday to give her a present.",
                     "context": {"agents": [
                         {"initial_value": "his mun", "indexes": [2, 4], "replacement_value": "Sam mun"}]}}
    verb = {"initial_value": "painted", "indexes": [3, 5], "replacement_value": "painted", "aux": False,
            "active": True}
    direct_obj = {"initial_value": "his mun", "indexes": [2, 4], "replacement_value": "Sam mun", "prep_added":True}
    action = {'What is the action?': [direct_obj],
              'Who is the action directed to?': [],
              'Who is making the action': [],
              'How is the action made': []
              }
    mocker.patch.object(action_extractor, "remove_prep_from_obj", return_value=direct_obj)
    mocker.patch.object(action_extractor, "get_nearest_component", return_value=direct_obj)
    action_extractor.handling_agent_componentes(
        context_action_dict=action,
        sent_full_dict=sentence_dict,
        verb_dct=verb,
        agent_obj=sentence_dict["context"]["agents"][0]

    )
    assert action_extractor.remove_prep_from_obj.call_count == 1
    assert action_extractor.get_nearest_component.call_count == 1
    for key in action:
        if key == "Who is making the action" or key=='What is the action?':
            assert len(action[key]) == 1
        else:
            assert len(action[key]) == 0


def test_create_action():
    verb = {"initial_value": "painted", "indexes": [3, 5], "replacement_value": "painted", "aux": False,
            "active": True}
    ret1, ret2, ret3 = action_extractor.create_action(verb)
    assert isinstance(ret1,dict)
    assert isinstance(ret2,int)
    assert isinstance(ret3,int)


def test_get_init_index_next_verb_not_if():
    sentence_dict = {"action_text": "Sam visited his mun yesterday to give her a present.",
                     "context": {"verbs": [
                {"initial_value": "visited","indexes": [1,2],"replacement_value": "visited","aux": False,"active": True},
                {"initial_value": "give","indexes": [6,7],"replacement_value": "give","aux": False,"active": True},
                     {"initial_value": "give","indexes": [6,7],"replacement_value": "give","aux": False,"active": True}]}}
    index_current_verb = 2
    index = action_extractor.get_init_index_next_verb(index_current_verb, sentence_dict)

    assert index == 100000000


def test_get_init_index_next_verb_if():
    sentence_dict = {"action_text": "Sam visited his mun yesterday to give her a present.",
                     "context": {"verbs": [
                         {"initial_value": "visited", "indexes": [1, 2], "replacement_value": "visited", "aux": False,
                          "active": True},
                         {"initial_value": "give", "indexes": [6, 7], "replacement_value": "give", "aux": False,
                          "active": True},
                         {"initial_value": "give", "indexes": [12, 13], "replacement_value": "give", "aux": False,
                          "active": True}]}}
    index_current_verb = 1
    index = action_extractor.get_init_index_next_verb(index_current_verb, sentence_dict)

    assert isinstance(index, int) and index !=100000000


def test_get_init_index_next_verb_aux():
    sentence_dict = {"action_text": "Sam visited his mun yesterday to give her a present.",
                     "context": {"verbs": [
                         {"initial_value": "visited", "indexes": [1, 2], "replacement_value": "visited", "aux": False,
                          "active": True},
                         {"initial_value": "give", "indexes": [6, 7], "replacement_value": "give", "aux": False,
                          "active": True},
                         {"initial_value": "give", "indexes": [12, 13], "replacement_value": "give", "aux": True,
                          "active": True}]}}
    index_current_verb = 1
    index = action_extractor.get_init_index_next_verb(index_current_verb, sentence_dict)

    assert index == 100000000


def test_check_element_order():
    action_dct = {'What is the action?': [{'initial_value': 'The Mona Lisa', 'indexes': (0, 3),
                                           'replacement_value': 'The Mona Lisa'}], 'Who is the action directed to?': [],
                  'Who is making the action': [{'initial_value': 'Leonardo Da Vinci', 'indexes': (5, 9),
                                                'replacement_value': 'Leonardo Da Vinci'}], 'How is the action made': []}
    action_dct_2 = action_extractor.check_element_order(action_dct)
    for key in action_dct:
        assert len(action_dct[key]) == len(action_dct_2[key])


def test_remove_extra_index_from_context_actions():
    action_dct = {'What is the action?': [{'initial_value': 'The Mona Lisa', 'indexes': (0, 3),
                                           'replacement_value': 'The Mona Lisa'}], 'Who is the action directed to?': [],
                  'Who is making the action': [{'initial_value': 'Leonardo Da Vinci', 'indexes': (5, 9),
                                                'replacement_value': 'Leonardo Da Vinci'}],
                  'How is the action made': []}
    action_dct = action_extractor.remove_extra_index_from_context_actions(action_dct)

    for key in action_dct:
        for obj_dict in action_dct[key]:
            assert dict_contains(obj_dict, ['initial_value', 'replacement_value'])


def test_add_subject_to_action(mocker):
    action_dct = {'What is the action?': [],
                  'Who is the action directed to?': [],
                  'Who is making the action': [],
                  'How is the action made': []}
    verb_dct = {"initial_value": "visited", "indexes": [1, 2], "replacement_value": "visited", "aux": False, "active": True}
    sentence_dict = {"context": {"action_subject": [{"initial_value": "Sam","indexes": [0, 1], "replacement_value": "Sam"}]}}
    subj_dct = {"initial_value": "Sam", "indexes": [0, 1], "replacement_value": "Sam"}
    index_current_verb = 1
    mocker.patch.object(action_extractor, 'select_subject', return_value=[subj_dct, 1])

    action_ret = action_extractor.add_subject_to_action(
        action=action_dct,
        verb_dct=verb_dct,
        action_full_dct=sentence_dict,
        index_current_verb=index_current_verb,
    )
    assert action_extractor.select_subject.call_count == 1
    for key in action_ret:
        if key == 'Who is making the action':
            assert len(action_ret[key])== 1
        else:
            assert len(action_ret[key]) == 0


def test_add_subject_to_action_not_active(mocker):
    action_dct = {'What is the action?': [],
                  'Who is the action directed to?': [],
                  'Who is making the action': [],
                  'How is the action made': []}
    verb_dct = {"initial_value": "visited", "indexes": [1, 2], "replacement_value": "visited", "aux": False,
                "active": False}
    sentence_dict = {
        "context": {"action_subject": [{"initial_value": "Sam", "indexes": [0, 1], "replacement_value": "Sam"}]}}
    subj_dct = {"initial_value": "Sam", "indexes": [0, 1], "replacement_value": "Sam"}
    index_current_verb = 1
    mocker.patch.object(action_extractor, 'select_subject', return_value=[subj_dct, 1])
    mocker.patch.object(action_extractor, 'replace_personal_pronoun_passive')

    action_ret = action_extractor.add_subject_to_action(
        action=action_dct,
        verb_dct=verb_dct,
        action_full_dct=sentence_dict,
        index_current_verb=index_current_verb,
    )
    assert action_extractor.select_subject.call_count == 1
    assert action_extractor.replace_personal_pronoun_passive.call_count == 1
    for key in action_ret:
        if key == 'What is the action?':
            assert len(action_ret[key]) == 1
        else:
            assert len(action_ret[key]) == 0


def test_add_subject_to_action_bad_index(mocker):
    action_dct = {'What is the action?': [],
                  'Who is the action directed to?': [],
                  'Who is making the action': [],
                  'How is the action made': []}
    verb_dct = {"initial_value": "visited", "indexes": [1, 2], "replacement_value": "visited", "aux": False,
                "active": False}
    sentence_dict = {
        "context": {"action_subject": [{"initial_value": "Sam", "indexes": [0, 1], "replacement_value": "Sam"}]}}
    subj_dct = {"initial_value": "Sam", "indexes": [0, 1], "replacement_value": "Sam"}
    index_current_verb = -1
    mocker.patch.object(action_extractor, 'select_subject', return_value=[subj_dct, index_current_verb])
    mocker.patch.object(action_extractor, 'replace_personal_pronoun_passive')

    action_ret = action_extractor.add_subject_to_action(
        action=action_dct,
        verb_dct=verb_dct,
        action_full_dct=sentence_dict,
        index_current_verb=index_current_verb,
    )
    assert action_extractor.select_subject.call_count == 1
    assert action_extractor.replace_personal_pronoun_passive.call_count == 0
    for key in action_ret:
            assert len(action_ret[key]) == 0


def test_replace_personal_pronoun_passive_if_if():
    subj_dict = {'initial_value':'he', 'replacement_value':'he' }
    subj_2 = action_extractor.replace_personal_pronoun_passive((subj_dict))
    assert dict_contains(subj_2, ['initial_value', 'replacement_value'])


def test_select_subject_None():
    sentence_dict = {
        "context": {"action_subject": [{"initial_value": "Sam", "indexes": [3, 6], "replacement_value": "Sam"}]}}
    index_current_verb = 1
    subj_selected, index = action_extractor.select_subject(action_full_dct=sentence_dict
                                                           ,index_current_verb=index_current_verb)

    assert subj_selected is None and index == -1


def test_select_subject():
    sentence_dict = {
        "context": {"action_subject": [{"initial_value": "Sam", "indexes": [3, 6], "replacement_value": "Sam"}]}}
    index_current_verb = 8
    subj_selected, index = action_extractor.select_subject(action_full_dct=sentence_dict
                                                           , index_current_verb=index_current_verb)

    assert subj_selected is not None and index != -1


def test_context_by_action(mocker):
    action_structure = [{'action_range': (0, 10), 'doc':'',
                         'action_text': 'The Mona Lisa was painted by Leonardo Da Vinci.',
                        'context': {'action_subject': [{'initial_value': 'The Mona Lisa', 'indexes': (0, 3),
                                                        'replacement_value': 'The Mona Lisa'}],
                        'indirect_object': [], 'direct_object': [{}], 'auxiliar_object': [{'prep_added':''}],
                        'verbs': [{'initial_value': 'painted', 'indexes': (3, 5), 'replacement_value': 'painted', 'aux': False, 'active': False}],
                                    'adverb_mod': [],
                                    'agents': [{'initial_value': 'by Leonardo Da Vinci', 'indexes': (5, 9), 'replacement_value': 'by Leonardo Da Vinci'}],
                                    'attributes': []}, 'context_actions': [], 'question': False}]
    action = {'What is the action?': [],
              'Who is the action directed to?': [],
              'Who is making the action': [],
              'How is the action made': []
              }
    mocker.patch.object(action_extractor, 'get_not_action_verbs', return_value=[['is'] , ['is']])
    mocker.patch.object(action_extractor, 'create_action', return_value=[action, 3, 4])
    mocker.patch.object(action_extractor, 'get_init_index_next_verb', return_value=9)
    mocker.patch.object(action_extractor, 'add_element_to_action', return_value=action)
    mocker.patch.object(action_extractor, 'add_subject_to_action', return_value=action)
    mocker.patch.object(action_extractor, 'check_element_order', return_value=action)
    mocker.patch.object(action_extractor, 'remove_extra_index_from_context_actions', return_value=action)
    agents_extractor_instance = ActionExtractor()
    agents_extractor_instance.context_by_action(action_structure)

    assert action_extractor.get_not_action_verbs.call_count == 1
    assert action_extractor.create_action.call_count == 1
    assert action_extractor.get_init_index_next_verb.call_count == 1
    assert action_extractor.add_element_to_action.call_count == 5
    assert action_extractor.add_subject_to_action.call_count == 1
    assert action_extractor.check_element_order.call_count == 1
    assert action_extractor.remove_extra_index_from_context_actions.call_count == 1
    for sentence_dict in action_structure:
        assert 'context_actions' in sentence_dict.keys()
        for pobj_dct in sentence_dict['context']['auxiliar_object']:
            assert 'prep_added' not in pobj_dct.keys()
        for action_dct in sentence_dict['context_actions']:
            for key in action_dct:
                if key == 'What is the action?':
                    assert isinstance(action_dct[key],dict)
                else:
                    assert isinstance(action_dct[key],list)


def test_context_by_action_not_action(mocker):
    action_structure = [{'action_range': (0, 10), 'doc':'',
                         'action_text': 'The Mona Lisa was painted by Leonardo Da Vinci.',
                        'context': {'action_subject': [{'initial_value': 'The Mona Lisa', 'indexes': (0, 3),
                                                        'replacement_value': 'The Mona Lisa'}],
                        'indirect_object': [], 'direct_object': [{}], 'auxiliar_object': [{'prep_added':''}],
                        'verbs': [{'initial_value': 'is', 'indexes': (3, 5), 'replacement_value': 'is', 'aux': False, 'active': False}],
                                    'adverb_mod': [],
                                    'agents': [{'initial_value': 'by Leonardo Da Vinci', 'indexes': (5, 9), 'replacement_value': 'by Leonardo Da Vinci'}],
                                    'attributes': []}, 'context_actions': [], 'question': False}]
    action = {'What is the action?': [],
              'Who is the action directed to?': [],
              'Who is making the action': [],
              'How is the action made': []
              }
    mocker.patch.object(action_extractor, 'get_not_action_verbs', return_value=[['is'] , ['is']])
    mocker.patch.object(action_extractor, 'create_action', return_value=[action, 3, 4])
    mocker.patch.object(action_extractor, 'get_init_index_next_verb', return_value=9)
    mocker.patch.object(action_extractor, 'add_element_to_action', return_value=action)
    mocker.patch.object(action_extractor, 'add_subject_to_action', return_value=action)
    mocker.patch.object(action_extractor, 'check_element_order', return_value=action)
    mocker.patch.object(action_extractor, 'remove_extra_index_from_context_actions', return_value=action)
    agents_extractor_instance = ActionExtractor()
    agents_extractor_instance.context_by_action(action_structure)

    assert action_extractor.get_not_action_verbs.call_count == 1
    assert action_extractor.create_action.call_count == 1
    assert action_extractor.get_init_index_next_verb.call_count == 1
    assert action_extractor.add_element_to_action.call_count == 5
    assert action_extractor.add_subject_to_action.call_count == 1
    assert action_extractor.check_element_order.call_count == 1
    assert action_extractor.remove_extra_index_from_context_actions.call_count == 1
    for sentence_dict in action_structure:
        for pobj_dct in sentence_dict['context']['auxiliar_object']:
            assert 'prep_added' not in pobj_dct.keys()
        for action_dct in sentence_dict['context_actions']:
            for key in action_dct:
                    assert isinstance(action_dct[key],list)


def test_context_by_action_aux_verb(mocker):
    action = {'What is the action?': {'initial_value': 'action', 'replacement_value': 'action'},
              'Who is the action directed to?': [],
              'Who is making the action': [],
              'How is the action made': []
              }
    action_structure = [{'action_range': (0, 10), 'doc':'',
                         'action_text': 'The Mona Lisa was painted by Leonardo Da Vinci.',
                        'context': {'action_subject': [{'initial_value': 'The Mona Lisa', 'indexes': (0, 3),
                                                        'replacement_value': 'The Mona Lisa'}],
                        'indirect_object': [], 'direct_object': [{}], 'auxiliar_object': [{'prep_added':''}],
                        'verbs': [{'initial_value': 'is', 'indexes': (3, 5), 'replacement_value': 'is', 'aux': True, 'active': False}],
                                    'adverb_mod': [],
                                    'agents': [{'initial_value': 'by Leonardo Da Vinci', 'indexes': (5, 9), 'replacement_value': 'by Leonardo Da Vinci'}],
                                    'attributes': []}, 'context_actions': [copy.copy(action)], 'question': False}]

    mocker.patch.object(action_extractor, 'get_not_action_verbs', return_value=[['is'] , ['is']])
    mocker.patch.object(action_extractor, 'create_action', return_value=[action, 3, 4])
    mocker.patch.object(action_extractor, 'get_init_index_next_verb', return_value=9)
    mocker.patch.object(action_extractor, 'add_element_to_action', return_value=action)
    mocker.patch.object(action_extractor, 'add_subject_to_action', return_value=action)
    mocker.patch.object(action_extractor, 'check_element_order', return_value=action)
    mocker.patch.object(action_extractor, 'remove_extra_index_from_context_actions', return_value=action)
    agents_extractor_instance = ActionExtractor()
    agents_extractor_instance.context_by_action(action_structure)

    assert action_extractor.get_not_action_verbs.call_count == 1
    assert action_extractor.create_action.call_count == 0
    assert action_extractor.get_init_index_next_verb.call_count == 0
    assert action_extractor.add_element_to_action.call_count == 0
    assert action_extractor.add_subject_to_action.call_count == 0
    assert action_extractor.check_element_order.call_count == 0
    assert action_extractor.remove_extra_index_from_context_actions.call_count == 0
    assert len(action_structure[0]['context_actions'][0]['What is the action?']['initial_value']) > len('action')

    assert len(action_structure[0]['context_actions'][0]['What is the action?']['replacement_value']) > len('action')


def test_context_by_action_aux_verb(mocker):
    action = {'What is the action?': {'initial_value': 'action', 'replacement_value': 'action'},
              'Who is the action directed to?': [],
              'Who is making the action': [],
              'How is the action made': []
              }
    action_structure = [{'action_range': (0, 10), 'doc':'',
                         'action_text': 'The Mona Lisa was painted by Leonardo Da Vinci.',
                        'context': {'action_subject': [{'initial_value': 'The Mona Lisa', 'indexes': (0, 3),
                                                        'replacement_value': 'The Mona Lisa'}],
                        'indirect_object': [], 'direct_object': [{}], 'auxiliar_object': [{'prep_added':''}],
                        'verbs': [{'initial_value': 'is', 'indexes': (3, 5), 'replacement_value': 'is', 'aux': True, 'active': False}],
                                    'adverb_mod': [],
                                    'agents': [{'initial_value': 'by Leonardo Da Vinci', 'indexes': (5, 9), 'replacement_value': 'by Leonardo Da Vinci'}],
                                    'attributes': []}, 'context_actions': [], 'question': False}]

    mocker.patch.object(action_extractor, 'get_not_action_verbs', return_value=[['is'], ['is']])
    mocker.patch.object(action_extractor, 'create_action', return_value=[action, 3, 4])
    mocker.patch.object(action_extractor, 'get_init_index_next_verb', return_value=9)
    mocker.patch.object(action_extractor, 'add_element_to_action', return_value=action)
    mocker.patch.object(action_extractor, 'add_subject_to_action', return_value=action)
    mocker.patch.object(action_extractor, 'check_element_order', return_value=action)
    mocker.patch.object(action_extractor, 'remove_extra_index_from_context_actions', return_value=action)
    agents_extractor_instance = ActionExtractor()
    agents_extractor_instance.context_by_action(action_structure)

    assert action_extractor.get_not_action_verbs.call_count == 1
    assert action_extractor.create_action.call_count == 1
    assert action_extractor.get_init_index_next_verb.call_count == 1
    assert action_extractor.add_element_to_action.call_count == 5
    assert action_extractor.add_subject_to_action.call_count == 1
    assert action_extractor.check_element_order.call_count == 1
    assert action_extractor.remove_extra_index_from_context_actions.call_count == 1
    for sentence_dict in action_structure:
        for pobj_dct in sentence_dict['context']['auxiliar_object']:
            assert 'prep_added' not in pobj_dct.keys()
        for action_dct in sentence_dict['context_actions']:
            for key in action_dct:
                assert isinstance(action_dct[key], list)
